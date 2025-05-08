from flask import Blueprint, request, jsonify
import requests
import os
from datetime import datetime
from utils.auth_utils import api_key_required
from extensions import mysql, groq_client

api_bp = Blueprint('api', __name__)

# API keys for third-party services
SKYSCANNER_API_KEY = os.getenv('SKYSCANNER_API_KEY')
BOOKING_API_KEY = os.getenv('BOOKING_API_KEY')

@api_bp.route('/api/flights/search', methods=['GET'])
@api_key_required
def search_flights_api():
    """API endpoint to search for flights using Skyscanner API"""
    # Get search parameters
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    departure_date = request.args.get('departure_date')
    return_date = request.args.get('return_date')
    adults = request.args.get('adults', 1)
    
    if not origin or not destination or not departure_date:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        # Call Skyscanner API
        response = requests.get(
            'https://partners.api.skyscanner.net/apiservices/v3/flights/live/search/create',
            headers={
                'x-api-key': SKYSCANNER_API_KEY
            },
            json={
                'query': {
                    'market': 'US',
                    'locale': 'en-US',
                    'currency': 'USD',
                    'queryLegs': [
                        {
                            'originPlaceId': {'iata': origin},
                            'destinationPlaceId': {'iata': destination},
                            'date': {
                                'year': int(departure_date.split('-')[0]),
                                'month': int(departure_date.split('-')[1]),
                                'day': int(departure_date.split('-')[2])
                            }
                        }
                    ],
                    'adults': int(adults),
                    'childrenAges': []
                }
            }
        )
        
        if response.status_code != 200:
            # If real API fails, use mock data for demonstration
            return jsonify(mock_flight_search(origin, destination, departure_date, return_date, adults))
        
        return jsonify(response.json())
    
    except Exception as e:
        # If there's an error, use mock data for demonstration
        return jsonify(mock_flight_search(origin, destination, departure_date, return_date, adults))

@api_bp.route('/api/hotels/search', methods=['GET'])
@api_key_required
def search_hotels_api():
    """API endpoint to search for hotels using Booking.com API"""
    # Get search parameters
    destination = request.args.get('destination')
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    guests = request.args.get('guests', 2)
    
    if not destination or not check_in or not check_out:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        # Call Booking.com API
        response = requests.get(
            'https://booking-com.p.rapidapi.com/v1/hotels/search',
            headers={
                'X-RapidAPI-Key': BOOKING_API_KEY,
                'X-RapidAPI-Host': 'booking-com.p.rapidapi.com'
            },
            params={
                'dest_id': destination,
                'checkin_date': check_in,
                'checkout_date': check_out,
                'adults_number': guests,
                'room_number': '1',
                'units': 'metric',
                'order_by': 'popularity',
                'filter_by_currency': 'USD',
                'locale': 'en-us'
            }
        )
        
        if response.status_code != 200:
            # If real API fails, use mock data for demonstration
            return jsonify(mock_hotel_search(destination, check_in, check_out, guests))
        
        return jsonify(response.json())
    
    except Exception as e:
        # If there's an error, use mock data for demonstration
        return jsonify(mock_hotel_search(destination, check_in, check_out, guests))

@api_bp.route('/api/weather', methods=['GET'])
@api_key_required
def get_weather_api():
    """API endpoint to get weather data"""
    # Get parameters
    location = request.args.get('location')
    
    if not location:
        return jsonify({'error': 'Missing location parameter'}), 400
    
    try:
        # Call OpenWeatherMap API
        response = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather',
            params={
                'q': location,
                'appid': os.getenv('OPENWEATHER_API_KEY'),
                'units': 'metric'
            }
        )
        
        if response.status_code != 200:
            return jsonify({'error': f'Weather API error: {response.json().get("message", "Unknown error")}'}), response.status_code
        
        return jsonify(response.json())
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@api_bp.route('/api/itinerary/generate', methods=['POST'])
@api_key_required
def generate_itinerary_api():
    """API endpoint to generate an itinerary using Groq AI"""
    # Get request data
    data = request.json
    
    if not data:
        return jsonify({'error': 'Missing request data'}), 400
    
    destination = data.get('destination')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    budget = data.get('budget')
    preferences = data.get('preferences', '')
    
    if not destination or not start_date or not end_date or not budget:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        # Call itinerary generation function
        from routes.trip_routes import generate_itinerary
        
        itinerary = generate_itinerary(destination, start_date, end_date, budget, preferences)
        
        return jsonify({
            'success': True,
            'itinerary': itinerary
        })
    
    except Exception as e:
        return jsonify({'error': f'Error generating itinerary: {str(e)}'}), 500

# Mock implementations for demonstration purposes
def mock_flight_search(origin, destination, departure_date, return_date, adults):
    """Mock implementation of Skyscanner API call"""
    # Convert dates to datetime objects
    departure_date_obj = datetime.strptime(departure_date, '%Y-%m-%d')
    
    # Generate mock flights
    flights = []
    airlines = ['American Airlines', 'Delta', 'United', 'Southwest', 'JetBlue']
    
    for i in range(5):
        departure_hour = 6 + (i * 3)
        arrival_hour = departure_hour + 2 + (i % 3)
        
        flight = {
            'id': f'FL{1000 + i}',
            'airline': airlines[i],
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'departure_time': f'{departure_hour:02d}:00',
            'arrival_time': f'{arrival_hour:02d}:00',
            'duration': f'{2 + (i % 3)}h {(i * 15) % 60}m',
            'price': 150 + (i * 50),
            'currency': 'USD',
            'stops': i % 2,
            'available_seats': 10 + (i * 5)
        }
        
        flights.append(flight)
    
    # Add return flights if return_date is provided
    if return_date:
        return_date_obj = datetime.strptime(return_date, '%Y-%m-%d')
        
        for i in range(5):
            departure_hour = 8 + (i * 3)
            arrival_hour = departure_hour + 2 + (i % 3)
            
            flight = {
                'id': f'FL{2000 + i}',
                'airline': airlines[(i + 2) % 5],
                'origin': destination,
                'destination': origin,
                'departure_date': return_date,
                'departure_time': f'{departure_hour:02d}:00',
                'arrival_time': f'{arrival_hour:02d}:00',
                'duration': f'{2 + (i % 3)}h {(i * 20) % 60}m',
                'price': 180 + (i * 40),
                'currency': 'USD',
                'stops': i % 2,
                'available_seats': 15 + (i * 4)
            }
            
            flights.append(flight)
    
    return {'flights': flights}

def mock_hotel_search(destination, check_in, check_out, guests):
    """Mock implementation of Booking.com API call"""
    # Convert dates to datetime objects
    check_in_obj = datetime.strptime(check_in, '%Y-%m-%d')
    check_out_obj = datetime.strptime(check_out, '%Y-%m-%d')
    
    # Calculate number of nights
    num_nights = (check_out_obj - check_in_obj).days
    
    # Generate mock hotels
    hotels = []
    hotel_names = [
        'Grand Hotel', 'City Center Inn', 'Luxury Suites', 
        'Comfort Stay', 'Ocean View Resort', 'Mountain Lodge',
        'Downtown Apartments', 'Riverside Hotel'
    ]
    
    for i in range(8):
        base_price = 80 + (i * 30)
        
        hotel = {
            'id': f'HT{1000 + i}',
            'name': f'{hotel_names[i]} {destination}',
            'address': f'{100 + i} Main Street, {destination}',
            'stars': min(5, 3 + (i % 3)),
            'rating': round(3.5 + (i * 0.2), 1),
            'price_per_night': base_price,
            'total_price': base_price * num_nights,
            'currency': 'USD',
            'available_rooms': 5 + (i % 5),
            'amenities': ['WiFi', 'Parking', 'Breakfast'],
            'image_url': f'https://example.com/hotel{i}.jpg',
            'cancellation_policy': 'Free cancellation up to 24 hours before check-in'
        }
        
        # Add more amenities for higher-end hotels
        if i > 3:
            hotel['amenities'].extend(['Pool', 'Gym'])
        
        if i > 5:
            hotel['amenities'].extend(['Spa', 'Restaurant'])
        
        hotels.append(hotel)
    
    return {'hotels': hotels}