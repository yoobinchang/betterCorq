const schedule = document.getElementById('schedule');
const days = 7;
const intervalCount = (24 - 2) * 2 + 1; // 8 AM to 10 PM in 30-min intervals
const cellHeight = 20;

let isMouseDown = false;
let toggleMode = null;

// Mouse tracking
document.body.addEventListener('mousedown', () => {
  isMouseDown = true;
});
document.body.addEventListener('mouseup', () => {
  isMouseDown = false;
  toggleMode = null;
});

// Generate calendar grid
for (let i = 16; i < intervalCount; i++) {
  let hour = Math.floor(i / 2);
  let minute = (i % 2) * 30;
  let timeStr = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;

  const timeCell = document.createElement('div');
  timeCell.classList.add('time-cell');
  timeCell.textContent = timeStr;
  schedule.appendChild(timeCell);

  for (let j = 0; j < days; j++) {
    const cell = document.createElement('div');
    cell.classList.add('cell');
    cell.style.height = cellHeight + 'px';

    // Assign day and time
    const today = new Date();
    const cellDate = new Date(today);
    cellDate.setDate(today.getDate() + j);
    const dayStr = cellDate.toISOString().split('T')[0]; // "YYYY-MM-DD"

    cell.setAttribute('data-day', dayStr);
    cell.setAttribute('data-time', timeStr);

    // Selection logic
    cell.addEventListener('mousedown', () => {
      isMouseDown = true;
      toggleMode = cell.classList.contains('selected') ? 'remove' : 'add';
      cell.classList.toggle('selected');
    });

    cell.addEventListener('mouseover', () => {
      if (isMouseDown && toggleMode) {
        cell.classList[toggleMode]('selected');
      }
    });

    schedule.appendChild(cell);
  }
}

// Format selected times
function getSelectedTimes() {
  const selectedCells = Array.from(document.querySelectorAll('.cell.selected'));

  const times = selectedCells.map(cell => {
    const day = cell.getAttribute('data-day');
    const time = cell.getAttribute('data-time');
    return { day, time };
  }).filter(t => t.day && t.time).sort((a, b) => {
    const aKey = `${a.day}${a.time}`;
    const bKey = `${b.day}${b.time}`;
    return aKey.localeCompare(bKey);
  });

  const grouped = [];
  let start = null;
  let end = null;

  for (let i = 0; i < times.length; i++) {
    const current = times[i];
    const next = times[i + 1];

    if (!start) start = current;

    if (!current.time || !/^\d{2}:\d{2}$/.test(current.time)) {
      console.warn("Invalid time format:", current.time);
      continue;
    }

    const [h, m] = current.time.split(':').map(Number);
    const nextTime = next?.time?.split(':').map(Number);
    const nextDay = next?.day;

    const isConsecutive =
      next &&
      current.day === nextDay &&
      nextTime[0] * 60 + nextTime[1] === h * 60 + m + 15; // 15-min slots

    if (!isConsecutive) {
      end = current;
      grouped.push({ start, end });
      start = null;
    }
  }

  const formatted = grouped.map(({ start, end }) => {
    const format = (d, t) => {
      const [year, month, day] = d.split('-');
      const [hour, minute] = t.split(':');
      return `${year}${month}${day}${hour}${minute}`; // no "T"
    };
    return {
      from: format(start.day, start.time),
      to: format(end.day, end.time)
    };
  });

  return formatted;
}

// Save button logic
document.getElementById('save-button').addEventListener('click', () => {
  const selectedTimes = getSelectedTimes();
  localStorage.setItem('userAvailability', JSON.stringify(selectedTimes));
  console.log("Saved availability:", selectedTimes);
  alert("Your availability has been saved!");
});

// Restore saved availability
function restoreAvailability() {
  const saved = localStorage.getItem('userAvailability');
  if (!saved) return;

  const availability = JSON.parse(saved);
  availability.forEach(({ from, to }) => {
    const day = from.slice(0, 4) + '-' + from.slice(4, 6) + '-' + from.slice(6, 8);
    const startHour = parseInt(from.slice(8, 10));
    const startMinute = parseInt(from.slice(10, 12));
    const endHour = parseInt(to.slice(8, 10));
    const endMinute = parseInt(to.slice(10, 12));

    let currentHour = startHour;
    let currentMinute = startMinute;

    while (
      currentHour < endHour ||
      (currentHour === endHour && currentMinute < endMinute)
    ) {
      const timeStr = `${String(currentHour).padStart(2, '0')}:${String(currentMinute).padStart(2, '0')}`;
      const selector = `.cell[data-day="${day}"][data-time="${timeStr}"]`;
      const cell = document.querySelector(selector);
      if (cell) cell.classList.add('selected');

      currentMinute += 30;
      if (currentMinute >= 60) {
        currentMinute = 0;
        currentHour += 1;
      }
    }
  });
}

restoreAvailability();
