const schedule = document.getElementById('schedule');
const days = 7;
const intervalCount = 24 * 4;
const cellHeight = 20;

let isMouseDown = false;
let toggleMode = null;

document.body.addEventListener('mousedown', () => {
  isMouseDown = true;
});
document.body.addEventListener('mouseup', () => {
  isMouseDown = false;
  toggleMode = null;
});

for (let i = 32; i < intervalCount; i++) {
  let hour = Math.floor(i / 4);
  let minute = (i % 4) * 15;
  let timeStr = `${String(hour).padStart(2,'0')}:${String(minute).padStart(2,'0')}`;

  const timeCell = document.createElement('div');
  timeCell.classList.add('time-cell');
  timeCell.textContent = timeStr;
  schedule.appendChild(timeCell);

  for (let j = 0; j < days; j++) {
    const cell = document.createElement('div');
    cell.classList.add('cell');
    cell.style.height = cellHeight + 'px';

    // Detect initial toggle mode on mousedown
    cell.addEventListener('mousedown', () => {
      isMouseDown = true;
      toggleMode = cell.classList.contains('selected') ? 'remove' : 'add';
      cell.classList.toggle('selected');
    });

    // Apply toggle mode on drag
    cell.addEventListener('mouseover', () => {
      if (isMouseDown && toggleMode) {
        cell.classList[toggleMode]('selected');
      }
    });

    schedule.appendChild(cell);
  }
}
