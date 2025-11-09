// ====================
// 📅 CALENDAR SETUP
// ====================
const schedule = document.getElementById("schedule");
const days = 7;
const intervalCount = (24 - 2) * 2 + 1; // 8 AM → 10 PM (30-min intervals)
const cellHeight = 20;
let isMouseDown = false;
let toggleMode = null;

// Track mouse for click & drag selection
document.body.addEventListener("mousedown", () => (isMouseDown = true));
document.body.addEventListener("mouseup", () => {
  isMouseDown = false;
  toggleMode = null;
});

// ====================
// 📤 FILE UPLOAD (AI extraction)
// ====================
document.getElementById("file-upload").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    showCustomAlert("📤 Uploading schedule... please wait");

    // ✅ Flask endpoint updated
    const response = await fetch("http://127.0.0.1:5000/api/ai/upload-schedule", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Upload failed");
    const data = await response.json();

    showCustomAlert("✅ Schedule processed! Highlighting your free time...");

    if (data.data) {
      localStorage.setItem("aiFreeTime", JSON.stringify(data.data)); // ✅ Save AI result
      highlightFreeTime(data.data);
    }
  } catch (err) {
    console.error(err);
    showCustomAlert("❌ Failed to upload schedule.");
  }
});

// ====================
// ⚠️ CUSTOM ALERT BOX
// ====================
function showCustomAlert(message) {
  const alertBox = document.getElementById("custom-alert");
  alertBox.textContent = message;
  alertBox.classList.remove("hidden", "visible");
  void alertBox.offsetWidth; // restart animation
  alertBox.classList.add("visible");
  setTimeout(() => {
    alertBox.classList.remove("visible");
    alertBox.classList.add("hidden");
  }, 3000);
}

// ====================
// 🗓 CALENDAR GRID GENERATION
// ====================
for (let i = 16; i < intervalCount; i++) {
  let hour = Math.floor(i / 2);
  let minute = (i % 2) * 30;
  let timeStr = `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;

  const timeCell = document.createElement("div");
  timeCell.classList.add("time-cell");
  timeCell.textContent = timeStr;
  schedule.appendChild(timeCell);

  for (let j = 0; j < days; j++) {
    const cell = document.createElement("div");
    cell.classList.add("cell");
    cell.style.height = cellHeight + "px";

    const today = new Date();
    const cellDate = new Date(today);
    cellDate.setDate(today.getDate() + j);
    const dayStr = cellDate.toISOString().split("T")[0]; // "YYYY-MM-DD"

    cell.setAttribute("data-day", dayStr);
    cell.setAttribute("data-time", timeStr);

    cell.addEventListener("mousedown", () => {
      isMouseDown = true;
      toggleMode = cell.classList.contains("selected") ? "remove" : "add";
      cell.classList.toggle("selected");
    });

    cell.addEventListener("mouseover", () => {
      if (isMouseDown && toggleMode) cell.classList[toggleMode]("selected");
    });

    schedule.appendChild(cell);
  }
}

// ====================
// 🧮 SELECTED TIME EXTRACTION
// ====================
function getSelectedTimes() {
  const selectedCells = Array.from(document.querySelectorAll(".cell.selected"));

  const times = selectedCells
    .map((cell) => {
      const day = cell.getAttribute("data-day");
      const time = cell.getAttribute("data-time");
      return { day, time };
    })
    .filter((t) => t.day && t.time)
    .sort((a, b) => `${a.day}${a.time}`.localeCompare(`${b.day}${b.time}`));

  const grouped = [];
  let start = null;

  for (let i = 0; i < times.length; i++) {
    const current = times[i];
    const next = times[i + 1];
    if (!start) start = current;

    const [h, m] = current.time.split(":").map(Number);
    const nextTime = next?.time?.split(":").map(Number);
    const nextDay = next?.day;
    const isConsecutive =
      next &&
      current.day === nextDay &&
      nextTime[0] * 60 + nextTime[1] === h * 60 + m + 30;

    if (!isConsecutive) {
      grouped.push({ start, end: current });
      start = null;
    }
  }

  return grouped.map(({ start, end }) => ({
    day: start.day,
    from: start.time,
    to: end.time,
  }));
}

// ====================
// 💾 SAVE BUTTON → Flask
// ====================
document.getElementById("save-button").addEventListener("click", async () => {
  const selectedTimes = getSelectedTimes();
  localStorage.setItem("userAvailability", JSON.stringify(selectedTimes));

  try {
    // ✅ Updated route
    const response = await fetch("http://127.0.0.1:5000/api/schedule/save-free-time", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(selectedTimes),
    });

    if (response.ok) showCustomAlert("✅ Your schedule has been saved!");
    else showCustomAlert("⚠️ Server error while saving schedule.");
  } catch (error) {
    console.error(error);
    showCustomAlert("❌ Failed to connect to server.");
  }
});

// ====================
// 🔄 RESTORE LOCAL DATA
// ====================
function restoreAvailability() {
  const aiFree = localStorage.getItem("aiFreeTime");
  if (aiFree) highlightFreeTime(JSON.parse(aiFree));

  const saved = localStorage.getItem("userAvailability");
  if (!saved) return;
  const availability = JSON.parse(saved);

  availability.forEach(({ day, from, to }) => {
    let [h, m] = from.split(":").map(Number);
    const [endH, endM] = to.split(":").map(Number);

    while (h < endH || (h === endH && m < endM)) {
      const timeStr = `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
      const cell = document.querySelector(`.cell[data-day="${day}"][data-time="${timeStr}"]`);
      if (cell) cell.classList.add("selected");
      m += 30;
      if (m >= 60) {
        m = 0;
        h++;
      }
    }
  });
}
restoreAvailability();

// ====================
// 🧹 CLEAR BUTTONS
// ====================
document.querySelectorAll(".clear-day").forEach((button) => {
  button.addEventListener("click", () => {
    const dayOffset = parseInt(button.dataset.day);
    const targetDate = new Date();
    targetDate.setDate(targetDate.getDate() + dayOffset);
    const dayStr = targetDate.toISOString().split("T")[0];
    document
      .querySelectorAll(`.cell[data-day='${dayStr}']`)
      .forEach((cell) => cell.classList.remove("selected"));
  });
});

document.getElementById("clear-button").addEventListener("click", () => {
  document.querySelectorAll(".cell.selected").forEach((cell) => cell.classList.remove("selected"));
  localStorage.removeItem("userAvailability");
  localStorage.removeItem("aiFreeTime");
  showCustomAlert("🧹 Cleared all selections.");
});

// ====================
// 🎨 HIGHLIGHT FREE TIME (AI result → paint on grid)
// ====================

// 🧭 Helper: weekday ("Mon") → actual date string ("2025-11-10")
function dateStrForWeekday(dayName) {
  const shortDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  for (let offset = 0; offset < 7; offset++) {
    const d = new Date();
    d.setDate(d.getDate() + offset);
    if (shortDays[d.getDay()] === dayName) {
      return d.toISOString().split("T")[0];
    }
  }
  return null;
}

function highlightFreeTime(freeTimeData) {
  Object.entries(freeTimeData).forEach(([dayName, intervals]) => {
    const dayStr = dateStrForWeekday(dayName);
    if (!dayStr) return;

    intervals.forEach(([start, end]) => {
      let [h, m] = start.split(":").map(Number);
      const [endH, endM] = end.split(":").map(Number);

      while (h < endH || (h === endH && m < endM)) {
        const timeStr = `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
        const sel = `.cell[data-day="${dayStr}"][data-time="${timeStr}"]`;
        const cell = document.querySelector(sel);
        if (cell) cell.classList.add("selected");

        m += 30;
        if (m >= 60) {
          m = 0;
          h++;
        }
      }
    });
  });
}
