from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from extensions import mysql
import json
import requests
from datetime import datetime
from utils.auth_utils import login_required

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/bookings')
@login_required
def bookings():
    # Get all bookings for the logged-in user
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT b.*, t.destination 
        FROM bookings b
        JOIN trips t ON b.trip_id = t.id
        WHERE t.user_id = %s 
        ORDER BY b.booking_date DESC
    ''', (session['user_id'],))
    bookings = cursor.fetchall()
    cursor.close()
    
    return render_template('bookings.html', bookings=bookings)

@booking_bp.route('/trips/<int:trip_id>/bookings/new', methods=['GET', 'POST'])
@login_required
def new_booking(trip_id):
    # Check if trip exists and belongs to user
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips 
        WHERE id = %s AND user_id = %s
    ''', (trip_id, session['user_id']))
    trip = cursor.fetchone()
    
    if not trip:
        flash('Trip not found', 'danger')
        return redirect(url_for('trip.trips'))
    
    if request.method == 'POST':
        # Get form data
        booking_type = request.form['booking_type']
        provider = request.form['provider']
        booking_details = request.form['booking_details']
        booking_date = request.form['booking_date']
        price = request.form['price']
        
        # Validate form data
        if not booking_type or not provider or not booking_details or not booking_date or not price:
            flash('Please fill out all required fields', 'danger')
            return render_template('new_booking.html', trip=trip)
        
        # Insert booking into database
        cursor.execute('''
            INSERT INTO bookings (trip_id, booking_type, provider, booking_details, booking_date, price) 
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (trip_id, booking_type, provider, booking_details, booking_date, price))
        mysql.connection.commit()
        cursor.close()
        
        flash('Booking added successfully!', 'success')
        return redirect(url_for('trip.view_trip', trip_id=trip_id))
    
    return render_template('new_booking.html', trip=trip)

@booking_bp.route('/bookings/<int:booking_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_booking(booking_id):
    # Get booking details
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT b.*, t.id as trip_id, t.user_id 
        FROM bookings b
        JOIN trips t ON b.trip_id = t.id
        WHERE b.id = %s
    ''', (booking_id,))
    booking = cursor.fetchone()
    
    if not booking or booking['user_id'] != session['user_id']:
        flash('Booking not found', 'danger')
        return redirect(url_for('booking.bookings'))
    
    if request.method == 'POST':
        # Get form data
        booking_type = request.form['booking_type']
        provider = request.form['provider']
        booking_details = request.form['booking_details']
        booking_date = request.form['booking_date']
        price = request.form['price']
        
        # Validate form data
        if not booking_type or not provider or not booking_details or not booking_date or not price:
            flash('Please fill out all required fields', 'danger')
            return render_template('edit_booking.html', booking=booking)
        
        # Update booking in database
        cursor.execute('''
            UPDATE bookings 
            SET booking_type = %s, provider = %s, booking_details = %s, booking_date = %s, price = %s 
            WHERE id = %s
        ''', (booking_type, provider, booking_details, booking_date, price, booking_id))
        mysql.connection.commit()
        cursor.close()
        
        flash('Booking updated successfully!', 'success')
        return redirect(url_for('trip.view_trip', trip_id=booking['trip_id']))
    
    return render_template('edit_booking.html', booking=booking)

@booking_bp.route('/bookings/<int:booking_id>/delete', methods=['POST'])
@login_required
def delete_booking(booking_id):
    # Check if booking exists and belongs to user's trip
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT b.*, t.id as trip_id, t.user_id 
        FROM bookings b
        JOIN trips t ON b.trip_id = t.id
        WHERE b.id = %s
    ''', (booking_id,))
    booking = cursor.fetchone()
    
    if not booking or booking['user_id'] != session['user_id']:
        flash('Booking not found', 'danger')
        return redirect(url_for('booking.bookings'))
    
    # Delete booking
    cursor.execute('DELETE FROM bookings WHERE id = %s', (booking_id,))
    mysql.connection.commit()
    cursor.close()
    
    flash('Booking deleted successfully!', 'success')
    return redirect(url_for('trip.view_trip', trip_id=booking['trip_id']))

@booking_bp.route('/search/flights', methods=['GET'])
@login_required
def search_flights():
    # Get trip_id from query parameters
    trip_id = request.args.get('trip_id')

    # Get user's trips for the dropdown
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips
        WHERE user_id = %s
        ORDER BY start_date DESC
    ''', (session['user_id'],))
    user_trips = cursor.fetchall()

    # If trip_id is provided, get the trip details
    trip = None
    if trip_id:
        cursor.execute('''
            SELECT * FROM trips
            WHERE id = %s AND user_id = %s
        ''', (trip_id, session['user_id']))
        trip = cursor.fetchone()

    cursor.close()

    # Get search parameters
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    departure_date = request.args.get('departure_date')
    return_date = request.args.get('return_date')
    adults = request.args.get('adults', 1)

    # Initialize flights to None
    flights = None

    # If all required parameters are provided, search for flights
    if origin and destination and departure_date:
        try:
            # In a real implementation, you would call the Skyscanner API here
            # For this example, we'll return mock data
            flights = search_skyscanner_flights(origin, destination, departure_date, return_date, adults)
        except Exception as e:
            flash(f'Error searching for flights: {str(e)}', 'danger')

    return render_template('search_flights.html',
                          user_trips=user_trips,
                          trip=trip,
                          flights=flights,
                          search_params={
                              'origin': origin,
                              'destination': destination,
                              'departure_date': departure_date,
                              'return_date': return_date,
                              'adults': adults
                          })

@booking_bp.route('/search/hotels', methods=['GET'])
@login_required
def search_hotels():
    # Get trip_id from query parameters
    trip_id = request.args.get('trip_id')

    # Get user's trips for the dropdown
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips
        WHERE user_id = %s
        ORDER BY start_date DESC
    ''', (session['user_id'],))
    user_trips = cursor.fetchall()

    # If trip_id is provided, get the trip details
    trip = None
    if trip_id:
        cursor.execute('''
            SELECT * FROM trips
            WHERE id = %s AND user_id = %s
        ''', (trip_id, session['user_id']))
        trip = cursor.fetchone()

    cursor.close()

    # Get search parameters
    destination = request.args.get('destination')
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    guests = request.args.get('guests', 2)

    # Initialize hotels to None
    hotels = None

    # If all required parameters are provided, search for hotels
    if destination and check_in and check_out:
        try:
            # In a real implementation, you would call the Booking.com API here
            # For this example, we'll return mock data
            hotels = search_booking_hotels(destination, check_in, check_out, guests)
        except Exception as e:
            flash(f'Error searching for hotels: {str(e)}', 'danger')

    return render_template('search_hotels.html',
                          user_trips=user_trips,
                          trip=trip,
                          hotels=hotels,
                          search_params={
                              'destination': destination,
                              'check_in': check_in,
                              'check_out': check_out,
                              'guests': guests
                          })

@booking_bp.route('/book/flight', methods=['POST'])
@login_required
def book_flight():
    # Get booking details
    data = request.json
    trip_id = data.get('trip_id')
    flight_id = data.get('flight_id')
    
    if not trip_id or not flight_id:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Check if trip exists and belongs to user
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips 
        WHERE id = %s AND user_id = %s
    ''', (trip_id, session['user_id']))
    trip = cursor.fetchone()
    
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404
    
    # Get flight details (mock implementation)
    flight = get_flight_details(flight_id)
    
    if not flight:
        return jsonify({'error': 'Flight not found'}), 404
    
    # Insert booking into database
    booking_details = json.dumps(flight)
    cursor.execute('''
        INSERT INTO bookings (trip_id, booking_type, provider, booking_details, booking_date, price) 
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (trip_id, 'Flight', flight['airline'], booking_details, flight['departure_date'], flight['price']))
    mysql.connection.commit()
    booking_id = cursor.lastrowid
    cursor.close()
    
    return jsonify({'success': True, 'booking_id': booking_id})

@booking_bp.route('/book/hotel', methods=['POST'])
@login_required
def book_hotel():
    # Get booking details
    data = request.json
    trip_id = data.get('trip_id')
    hotel_id = data.get('hotel_id')
    
    if not trip_id or not hotel_id:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Check if trip exists and belongs to user
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips 
        WHERE id = %s AND user_id = %s
    ''', (trip_id, session['user_id']))
    trip = cursor.fetchone()
    
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404
    
    # Get hotel details (mock implementation)
    hotel = get_hotel_details(hotel_id)
    
    if not hotel:
        return jsonify({'error': 'Hotel not found'}), 404
    
    # Insert booking into database
    booking_details = json.dumps(hotel)
    cursor.execute('''
        INSERT INTO bookings (trip_id, booking_type, provider, booking_details, booking_date, price) 
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (trip_id, 'Hotel', hotel['name'], booking_details, trip['start_date'], hotel['price_per_night'] * (trip['end_date'] - trip['start_date']).days))
    mysql.connection.commit()
    booking_id = cursor.lastrowid
    cursor.close()
    
    return jsonify({'success': True, 'booking_id': booking_id})

# Mock implementations of third-party API calls
def search_skyscanner_flights(origin, destination, departure_date, return_date, adults):
    """Mock implementation of Skyscanner API call"""
    # In a real implementation, you would call the Skyscanner API here
    # For this example, we'll return mock data
    
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

def search_booking_hotels(destination, check_in, check_out, guests):
    """Mock implementation of Booking.com API call"""
    # In a real implementation, you would call the Booking.com API here
    # For this example, we'll return mock data
    
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

def get_flight_details(flight_id):
    """Mock implementation to get flight details by ID"""
    # In a real implementation, you would call the Skyscanner API here
    # For this example, we'll return mock data based on the ID
    
    flight_num = int(flight_id[2:])
    
    if flight_num < 2000:
        # Outbound flight
        i = flight_num - 1000
        airlines = ['American Airlines', 'Delta', 'United', 'Southwest', 'JetBlue']
        
        departure_hour = 6 + (i * 3)
        arrival_hour = departure_hour + 2 + (i % 3)
        
        return {
            'id': flight_id,
            'airline': airlines[i % 5],
            'origin': 'Mock Origin',
            'destination': 'Mock Destination',
            'departure_date': datetime.now().strftime('%Y-%m-%d'),
            'departure_time': f'{departure_hour:02d}:00',
            'arrival_time': f'{arrival_hour:02d}:00',
            'duration': f'{2 + (i % 3)}h {(i * 15) % 60}m',
            'price': 150 + (i * 50),
            'currency': 'USD',
            'stops': i % 2,
            'booking_reference': f'REF{10000 + i}'
        }
    else:
        # Return flight
        i = flight_num - 2000
        airlines = ['American Airlines', 'Delta', 'United', 'Southwest', 'JetBlue']
        
        departure_hour = 8 + (i * 3)
        arrival_hour = departure_hour + 2 + (i % 3)
        
        return {
            'id': flight_id,
            'airline': airlines[(i + 2) % 5],
            'origin': 'Mock Destination',
            'destination': 'Mock Origin',
            'departure_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'departure_time': f'{departure_hour:02d}:00',
            'arrival_time': f'{arrival_hour:02d}:00',
            'duration': f'{2 + (i % 3)}h {(i * 20) % 60}m',
            'price': 180 + (i * 40),
            'currency': 'USD',
            'stops': i % 2,
            'booking_reference': f'REF{20000 + i}'
        }

def get_hotel_details(hotel_id):
    """Mock implementation to get hotel details by ID"""
    # In a real implementation, you would call the Booking.com API here
    # For this example, we'll return mock data based on the ID
    
    hotel_num = int(hotel_id[2:])
    i = hotel_num - 1000
    
    hotel_names = [
        'Grand Hotel', 'City Center Inn', 'Luxury Suites', 
        'Comfort Stay', 'Ocean View Resort', 'Mountain Lodge',
        'Downtown Apartments', 'Riverside Hotel'
    ]
    
    base_price = 80 + (i * 30)
    
    return {
        'id': hotel_id,
        'name': f'{hotel_names[i % 8]} Mock Destination',
        'address': f'{100 + i} Main Street, Mock Destination',
        'stars': min(5, 3 + (i % 3)),
        'rating': round(3.5 + (i * 0.2), 1),
        'price_per_night': base_price,
        'currency': 'USD',
        'room_type': 'Standard Double Room',
        'amenities': ['WiFi', 'Parking', 'Breakfast'],
        'image_url': f'https://example.com/hotel{i}.jpg',
        'cancellation_policy': 'Free cancellation up to 24 hours before check-in',
        'booking_reference': f'BK{30000 + i}'
    }