// Main JavaScript for AI Trip Planner

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Handle flight search form
    const flightSearchForm = document.getElementById('flightSearchForm');
    if (flightSearchForm) {
        flightSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            searchFlights();
        });
    }

    // Handle hotel search form
    const hotelSearchForm = document.getElementById('hotelSearchForm');
    if (hotelSearchForm) {
        hotelSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            searchHotels();
        });
    }

    // Handle review form star rating
    const ratingInputs = document.querySelectorAll('.rating-input');
    if (ratingInputs.length > 0) {
        ratingInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                updateStarRating(this.value);
            });
        });
    }
});

// Function to search for flights
function searchFlights() {
    const origin = document.getElementById('flightOrigin').value;
    const destination = document.getElementById('flightDestination').value;
    const departureDate = document.getElementById('flightDepartureDate').value;
    const returnDate = document.getElementById('flightReturnDate').value;
    const adults = document.getElementById('flightAdults').value;

    // Show loading state
    const resultsContainer = document.getElementById('flightResults');
    resultsContainer.innerHTML = `
        <div class="text-center p-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">Searching for flights...</p>
        </div>
    `;

    // Make API request
    fetch(`/search/flights?origin=${origin}&destination=${destination}&departure_date=${departureDate}&return_date=${returnDate}&adults=${adults}`)
        .then(response => response.json())
        .then(data => {
            displayFlightResults(data);
        })
        .catch(error => {
            resultsContainer.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-circle me-2"></i>Error searching for flights: ${error.message}
                </div>
            `;
        });
}

// Function to display flight search results
function displayFlightResults(data) {
    const resultsContainer = document.getElementById('flightResults');
    
    if (!data.flights || data.flights.length === 0) {
        resultsContainer.innerHTML = `
            <div class="alert alert-info" role="alert">
                <i class="fas fa-info-circle me-2"></i>No flights found for your search criteria.
            </div>
        `;
        return;
    }

    let html = '<div class="list-group">';
    
    data.flights.forEach(flight => {
        html += `
            <div class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between align-items-center">
                    <div>
                        <h5 class="mb-1">${flight.airline}</h5>
                        <p class="mb-1">
                            <span class="badge bg-primary">${flight.departure_time}</span>
                            <i class="fas fa-arrow-right mx-2"></i>
                            <span class="badge bg-success">${flight.arrival_time}</span>
                        </p>
                        <small>
                            <i class="fas fa-clock me-1"></i>${flight.duration}
                            <i class="fas fa-plane ms-3 me-1"></i>${flight.stops === 0 ? 'Direct' : flight.stops + ' stop(s)'}
                        </small>
                    </div>
                    <div class="text-end">
                        <h5 class="mb-1">$${flight.price}</h5>
                        <small class="text-muted">${flight.available_seats} seats left</small>
                        <button class="btn btn-sm btn-primary mt-2" onclick="selectFlight('${flight.id}')">
                            Select
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    resultsContainer.innerHTML = html;
}

// Function to search for hotels
function searchHotels() {
    const destination = document.getElementById('hotelDestination').value;
    const checkIn = document.getElementById('hotelCheckIn').value;
    const checkOut = document.getElementById('hotelCheckOut').value;
    const guests = document.getElementById('hotelGuests').value;

    // Show loading state
    const resultsContainer = document.getElementById('hotelResults');
    resultsContainer.innerHTML = `
        <div class="text-center p-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">Searching for hotels...</p>
        </div>
    `;

    // Make API request
    fetch(`/search/hotels?destination=${destination}&check_in=${checkIn}&check_out=${checkOut}&guests=${guests}`)
        .then(response => response.json())
        .then(data => {
            displayHotelResults(data);
        })
        .catch(error => {
            resultsContainer.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-circle me-2"></i>Error searching for hotels: ${error.message}
                </div>
            `;
        });
}

// Function to display hotel search results
function displayHotelResults(data) {
    const resultsContainer = document.getElementById('hotelResults');
    
    if (!data.hotels || data.hotels.length === 0) {
        resultsContainer.innerHTML = `
            <div class="alert alert-info" role="alert">
                <i class="fas fa-info-circle me-2"></i>No hotels found for your search criteria.
            </div>
        `;
        return;
    }

    let html = '<div class="row">';
    
    data.hotels.forEach(hotel => {
        // Generate stars HTML
        let starsHtml = '';
        for (let i = 0; i < hotel.stars; i++) {
            starsHtml += '<i class="fas fa-star text-warning"></i>';
        }
        
        // Generate amenities HTML
        let amenitiesHtml = '';
        hotel.amenities.forEach(amenity => {
            amenitiesHtml += `<span class="badge bg-light text-dark me-1 mb-1">${amenity}</span>`;
        });
        
        html += `
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="row g-0">
                        <div class="col-md-4">
                            <img src="${hotel.image_url}" class="img-fluid rounded-start h-100" style="object-fit: cover;" alt="${hotel.name}">
                        </div>
                        <div class="col-md-8">
                            <div class="card-body">
                                <h5 class="card-title">${hotel.name}</h5>
                                <div class="mb-2">${starsHtml}</div>
                                <p class="card-text small">${hotel.address}</p>
                                <div class="mb-2">${amenitiesHtml}</div>
                                <div class="d-flex justify-content-between align-items-center mt-3">
                                    <div>
                                        <h5 class="mb-0">$${hotel.price_per_night}</h5>
                                        <small class="text-muted">per night</small>
                                    </div>
                                    <button class="btn btn-sm btn-primary" onclick="selectHotel('${hotel.id}')">
                                        Select
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    resultsContainer.innerHTML = html;
}

// Function to select a flight
function selectFlight(flightId) {
    const tripId = document.getElementById('tripId').value;
    
    // Show confirmation modal
    const modal = new bootstrap.Modal(document.getElementById('confirmBookingModal'));
    document.getElementById('confirmBookingTitle').textContent = 'Confirm Flight Booking';
    document.getElementById('confirmBookingBody').innerHTML = `
        <p>Are you sure you want to book this flight?</p>
        <p><strong>Flight ID:</strong> ${flightId}</p>
        <div class="spinner-border text-primary d-none" id="bookingSpinner" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    
    // Set up confirm button
    const confirmButton = document.getElementById('confirmBookingButton');
    confirmButton.onclick = function() {
        // Show spinner
        document.getElementById('bookingSpinner').classList.remove('d-none');
        confirmButton.disabled = true;
        
        // Make booking request
        fetch('/book/flight', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                trip_id: tripId,
                flight_id: flightId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Close modal and show success message
                modal.hide();
                showAlert('Flight booked successfully!', 'success');
                
                // Reload page after a short delay
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                throw new Error(data.error || 'Failed to book flight');
            }
        })
        .catch(error => {
            // Show error in modal
            document.getElementById('bookingSpinner').classList.add('d-none');
            confirmButton.disabled = false;
            document.getElementById('confirmBookingBody').innerHTML += `
                <div class="alert alert-danger mt-3" role="alert">
                    <i class="fas fa-exclamation-circle me-2"></i>${error.message}
                </div>
            `;
        });
    };
    
    modal.show();
}

// Function to select a hotel
function selectHotel(hotelId) {
    const tripId = document.getElementById('tripId').value;
    
    // Show confirmation modal
    const modal = new bootstrap.Modal(document.getElementById('confirmBookingModal'));
    document.getElementById('confirmBookingTitle').textContent = 'Confirm Hotel Booking';
    document.getElementById('confirmBookingBody').innerHTML = `
        <p>Are you sure you want to book this hotel?</p>
        <p><strong>Hotel ID:</strong> ${hotelId}</p>
        <div class="spinner-border text-primary d-none" id="bookingSpinner" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    
    // Set up confirm button
    const confirmButton = document.getElementById('confirmBookingButton');
    confirmButton.onclick = function() {
        // Show spinner
        document.getElementById('bookingSpinner').classList.remove('d-none');
        confirmButton.disabled = true;
        
        // Make booking request
        fetch('/book/hotel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                trip_id: tripId,
                hotel_id: hotelId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Close modal and show success message
                modal.hide();
                showAlert('Hotel booked successfully!', 'success');
                
                // Reload page after a short delay
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                throw new Error(data.error || 'Failed to book hotel');
            }
        })
        .catch(error => {
            // Show error in modal
            document.getElementById('bookingSpinner').classList.add('d-none');
            confirmButton.disabled = false;
            document.getElementById('confirmBookingBody').innerHTML += `
                <div class="alert alert-danger mt-3" role="alert">
                    <i class="fas fa-exclamation-circle me-2"></i>${error.message}
                </div>
            `;
        });
    };
    
    modal.show();
}

// Function to update star rating display
function updateStarRating(rating) {
    const stars = document.querySelectorAll('.rating-star');
    
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.remove('far');
            star.classList.add('fas');
        } else {
            star.classList.remove('fas');
            star.classList.add('far');
        }
    });
}

// Function to show an alert
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-4`;
    alertContainer.style.zIndex = '9999';
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertContainer);
        bsAlert.close();
    }, 5000);
}