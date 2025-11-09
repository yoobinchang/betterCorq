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

    events.forEach(event => {
        const eventDiv = document.createElement('div');
        eventDiv.className = 'event';
        eventDiv.dataset.name = event.name;

        // Event name container
        const nameContainer = document.createElement('div');
        nameContainer.className = 'event-name-container';

        const eventName = document.createElement('h2');
        eventName.className = 'event-name';
        eventName.textContent = event.name;

        nameContainer.appendChild(eventName);
        eventDiv.appendChild(nameContainer);

        // Inner box with details
        const innerBox = document.createElement('div');
        innerBox.className = 'inner-box';
        innerBox.innerHTML = `
            <p><strong>Start:</strong> ${formatDateTime(event.start)}</p>
            <p><strong>End:</strong> ${event.end}</p>
            <p><strong>Location:</strong> ${event.location}</p>
            <p><strong>Organization:</strong> ${event.organization}</p>
        `;
        eventDiv.appendChild(innerBox);

        // Selection logic
        if (selectedEvents.some(e => e.name === event.name)) {
            eventDiv.classList.add('selected');
        }

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

// Initialize selected events
let selectedEvents = JSON.parse(localStorage.getItem('selectedEvents')) || [];

// Load events on page load
document.addEventListener('DOMContentLoaded', loadEvents);
