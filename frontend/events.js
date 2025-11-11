// Function to format the date and time
function formatDateTime(dateTimeStr) {
    if (!dateTimeStr || typeof dateTimeStr !== 'string') {
        return 'Invalid Date';
    }

    const date = new Date(dateTimeStr);
    if (isNaN(date.getTime())) {
        return 'Invalid Date';
    }

    return date.toLocaleString('en-US', {
        month: 'numeric',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}


// Function to load events from the JSON file
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

// Function to display events
function displayEvents(events) {
    const container = document.querySelector('.event-container');
    container.innerHTML = ''; // Clear existing content

    events.forEach(event => {
        const eventDiv = document.createElement('div');
        eventDiv.className = 'event';
        eventDiv.dataset.name = event.name;

        // Create the event content
        eventDiv.innerHTML = `
            <strong>${event.name}</strong><br>
            <span class="event-time">${formatDateTime(event.start)} - ${event.end}</span><br>
            <span class="event-location">${event.location}</span><br>
            <span class="event-org">${event.organization}</span>
    
        `;

        // Check if this event is already in the schedule
        if (selectedEvents.some(e => e.name === event.name)) {
            eventDiv.classList.add('selected');
        }

        // Add click event listener for selection
        eventDiv.addEventListener('click', () => {
            if (eventDiv.classList.contains('selected')) {
                eventDiv.classList.remove('selected');
                selectedEvents = selectedEvents.filter(e => e.name !== event.name);
            } else {
                eventDiv.classList.add('selected');
                selectedEvents.push({
                    name: event.name,
                    start: event.start,
                    end: event.end,
                    location: event.location,
                    organization: event.organization
                });
            }
            localStorage.setItem('selectedEvents', JSON.stringify(selectedEvents));
        });

        container.appendChild(eventDiv);
    });
}

// Initialize selected events from localStorage
let selectedEvents = JSON.parse(localStorage.getItem('selectedEvents')) || [];

// Load events when the page loads
document.addEventListener('DOMContentLoaded', loadEvents);