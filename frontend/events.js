// Format date/time
function formatDateTime(dateTimeStr) {
    if (!dateTimeStr.includes('2025')) {
        return dateTimeStr;
    }
    const date = new Date(dateTimeStr);
    return date.toLocaleString('en-US', {
        month: 'numeric',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

// Load events
async function loadEvents() {
    try {
        const response = await fetch('/backend/data/events_est.json');
        const events = await response.json();
        displayEvents(events);
    } catch (error) {
        console.error('Error loading events:', error);
        document.querySelector('.event-container').innerHTML = 
            '<p class="error">Error loading events. Please try again later.</p>';
    }
}

// Display events
function displayEvents(events) {
  const container = document.querySelector('.event-container');
  container.innerHTML = '';

  // Load free time ranges from localStorage
  const freeTimes = JSON.parse(localStorage.getItem("userAvailability")) || [];

  // Only keep events that overlap with free time
  const filteredEvents = events.filter(event => eventFitsFreeTime(event, freeTimes, 15));

  filteredEvents.forEach(event => {
    // ... your existing eventDiv creation code ...
  });
}


// Check if an event overlaps with free time (with tolerance)
function eventFitsFreeTime(event, freeTimes, toleranceMinutes = 15) {
  const eventStart = new Date(event.start);
  const eventEnd   = new Date(event.end);

  return freeTimes.some(free => {
    const freeStart = new Date(`${free.day}T${free.from}:00`);
    const freeEnd   = new Date(`${free.day}T${free.to}:00`);

    // Apply tolerance: extend free time window slightly
    const freeStartTol = new Date(freeStart.getTime() - toleranceMinutes * 60000);
    const freeEndTol   = new Date(freeEnd.getTime() + toleranceMinutes * 60000);

    // Overlap condition: event and free time intersect
    return eventStart < freeEndTol && eventEnd > freeStartTol;
  });
}


// Initialize selected events
let selectedEvents = JSON.parse(localStorage.getItem('selectedEvents')) || [];

// Load events on page load
document.addEventListener('DOMContentLoaded', loadEvents);
