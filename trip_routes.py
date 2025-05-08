from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from extensions import mysql, groq_client
import json
from datetime import datetime, timedelta
from utils.auth_utils import login_required

trip_bp = Blueprint('trip', __name__)

@trip_bp.route('/trips')
@login_required
def trips():
    # Get all trips for the logged-in user
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    ''', (session['user_id'],))
    trips = cursor.fetchall()
    cursor.close()
    
    return render_template('trips.html', trips=trips)

@trip_bp.route('/trips/new', methods=['GET', 'POST'])
@login_required
def new_trip():
    if request.method == 'POST':
        # Get form data
        destination = request.form['destination']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        budget = request.form['budget']

        # Get preferences (handle both array and string formats)
        preferences = request.form.getlist('preferences[]')
        if not preferences:
            # If no preferences are selected, use an empty string
            preferences = ""
        else:
            # Join the preferences into a comma-separated string
            preferences = ", ".join(preferences)
        
        # Validate form data
        if not destination or not start_date or not end_date or not budget:
            flash('Please fill out all required fields', 'danger')
            return render_template('new_trip.html')
        
        # Convert dates to datetime objects
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Check if end date is after start date
        if end_date_obj <= start_date_obj:
            flash('End date must be after start date', 'danger')
            return render_template('new_trip.html')
        
        # Generate itinerary using Groq AI
        itinerary = generate_itinerary(destination, start_date, end_date, budget, preferences)
        
        # Insert trip into database
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO trips (user_id, destination, start_date, end_date, budget, preferences, itinerary) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (session['user_id'], destination, start_date, end_date, budget, preferences, json.dumps(itinerary)))
        mysql.connection.commit()
        trip_id = cursor.lastrowid
        cursor.close()
        
        flash('Trip created successfully!', 'success')
        return redirect(url_for('trip.view_trip', trip_id=trip_id))
    
    return render_template('new_trip.html')

@trip_bp.route('/trips/<int:trip_id>')
@login_required
def view_trip(trip_id):
    # Get trip details
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips 
        WHERE id = %s AND user_id = %s
    ''', (trip_id, session['user_id']))
    trip = cursor.fetchone()
    
    if not trip:
        flash('Trip not found', 'danger')
        return redirect(url_for('trip.trips'))
    
    # Parse itinerary from JSON
    trip['itinerary'] = json.loads(trip['itinerary'])
    
    # Get bookings for this trip
    cursor.execute('''
        SELECT * FROM bookings
        WHERE trip_id = %s
    ''', (trip_id,))
    bookings = cursor.fetchall()
    cursor.close()

    # Mock weather data for the destination
    weather = {
        'icon': 'sunny',
        'temp': 25,
        'feels_like': 27,
        'description': 'Sunny with clear skies',
        'humidity': 60,
        'wind_speed': 10,
        'forecast': [
            {
                'day': 'Today',
                'icon': 'sunny',
                'high': 28,
                'low': 18,
                'description': 'Sunny'
            },
            {
                'day': 'Tomorrow',
                'icon': 'partly_cloudy',
                'high': 26,
                'low': 17,
                'description': 'Partly cloudy'
            },
            {
                'day': 'Day 3',
                'icon': 'cloudy',
                'high': 24,
                'low': 16,
                'description': 'Cloudy'
            }
        ]
    }

    # Get current date for weather display
    now = datetime.now()

    return render_template('view_trip.html', trip=trip, bookings=bookings, weather=weather, timedelta=timedelta, now=now)

@trip_bp.route('/trips/<int:trip_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_trip(trip_id):
    # Get trip details
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
        destination = request.form['destination']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        budget = request.form['budget']

        # Get preferences (handle both array and string formats)
        preferences = request.form.getlist('preferences[]')
        if not preferences:
            # If no preferences are selected, use an empty string
            preferences = ""
        else:
            # Join the preferences into a comma-separated string
            preferences = ", ".join(preferences)
        
        # Validate form data
        if not destination or not start_date or not end_date or not budget:
            flash('Please fill out all required fields', 'danger')
            return render_template('edit_trip.html', trip=trip)
        
        # Convert dates to datetime objects
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Check if end date is after start date
        if end_date_obj <= start_date_obj:
            flash('End date must be after start date', 'danger')
            return render_template('edit_trip.html', trip=trip)
        
        # Check if itinerary needs to be regenerated
        if (destination != trip['destination'] or 
            start_date != trip['start_date'].strftime('%Y-%m-%d') or 
            end_date != trip['end_date'].strftime('%Y-%m-%d') or 
            budget != str(trip['budget']) or 
            preferences != trip['preferences']):
            
            # Generate new itinerary using Groq AI
            itinerary = generate_itinerary(destination, start_date, end_date, budget, preferences)
            
            # Update trip in database with new itinerary
            cursor.execute('''
                UPDATE trips 
                SET destination = %s, start_date = %s, end_date = %s, budget = %s, preferences = %s, itinerary = %s 
                WHERE id = %s
            ''', (destination, start_date, end_date, budget, preferences, json.dumps(itinerary), trip_id))
        else:
            # Update trip in database without changing itinerary
            cursor.execute('''
                UPDATE trips 
                SET destination = %s, start_date = %s, end_date = %s, budget = %s, preferences = %s 
                WHERE id = %s
            ''', (destination, start_date, end_date, budget, preferences, trip_id))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('Trip updated successfully!', 'success')
        return redirect(url_for('trip.view_trip', trip_id=trip_id))
    
    return render_template('edit_trip.html', trip=trip)

@trip_bp.route('/trips/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
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
    
    # Delete all bookings for this trip
    cursor.execute('DELETE FROM bookings WHERE trip_id = %s', (trip_id,))
    
    # Delete trip
    cursor.execute('DELETE FROM trips WHERE id = %s', (trip_id,))
    mysql.connection.commit()
    cursor.close()
    
    flash('Trip deleted successfully!', 'success')
    return redirect(url_for('trip.trips'))

@trip_bp.route('/trips/<int:trip_id>/regenerate', methods=['POST'])
@login_required
def regenerate_itinerary(trip_id):
    # Get trip details
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips 
        WHERE id = %s AND user_id = %s
    ''', (trip_id, session['user_id']))
    trip = cursor.fetchone()
    
    if not trip:
        flash('Trip not found', 'danger')
        return redirect(url_for('trip.trips'))
    
    # Generate new itinerary using Groq AI
    itinerary = generate_itinerary(
        trip['destination'], 
        trip['start_date'].strftime('%Y-%m-%d'), 
        trip['end_date'].strftime('%Y-%m-%d'), 
        str(trip['budget']), 
        trip['preferences']
    )
    
    # Update trip in database with new itinerary
    cursor.execute('''
        UPDATE trips 
        SET itinerary = %s 
        WHERE id = %s
    ''', (json.dumps(itinerary), trip_id))
    mysql.connection.commit()
    cursor.close()
    
    flash('Itinerary regenerated successfully!', 'success')
    return redirect(url_for('trip.view_trip', trip_id=trip_id))

@trip_bp.route('/trips/favorite/<int:trip_id>', methods=['POST'])
@login_required
def favorite_trip(trip_id):
    # Check if trip exists and belongs to user
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips 
        WHERE id = %s AND user_id = %s
    ''', (trip_id, session['user_id']))
    trip = cursor.fetchone()
    
    if not trip:
        return jsonify({'success': False, 'message': 'Trip not found'})
    
    # Toggle favorite status
    new_status = not trip['is_favorite']
    
    cursor.execute('''
        UPDATE trips 
        SET is_favorite = %s 
        WHERE id = %s
    ''', (new_status, trip_id))
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({'success': True, 'is_favorite': new_status})

@trip_bp.route('/trips/favorites')
@login_required
def favorite_trips():
    # Get all favorite trips for the logged-in user
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips 
        WHERE user_id = %s AND is_favorite = 1
        ORDER BY created_at DESC
    ''', (session['user_id'],))
    trips = cursor.fetchall()
    cursor.close()
    
    return render_template('favorite_trips.html', trips=trips)

@trip_bp.route('/trips/past')
@login_required
def past_trips():
    # Get all past trips for the logged-in user
    today = datetime.now().date()

    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips
        WHERE user_id = %s AND end_date < %s
        ORDER BY end_date DESC
    ''', (session['user_id'], today))
    trips = cursor.fetchall()
    cursor.close()

    return render_template('past_trips.html', trips=trips)

@trip_bp.route('/trips/<int:trip_id>/share')
@login_required
def share_trip(trip_id):
    # Get trip details
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips
        WHERE id = %s AND user_id = %s
    ''', (trip_id, session['user_id']))
    trip = cursor.fetchone()
    cursor.close()

    if not trip:
        flash('Trip not found', 'danger')
        return redirect(url_for('trip.trips'))

    # For now, just redirect back to the trip view with a message
    # In a real implementation, this would generate a shareable link or show sharing options
    flash('Sharing functionality will be implemented in a future update', 'info')
    return redirect(url_for('trip.view_trip', trip_id=trip_id))

@trip_bp.route('/trips/<int:trip_id>/duplicate')
@login_required
def duplicate_trip(trip_id):
    # Get trip details
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips
        WHERE id = %s AND user_id = %s
    ''', (trip_id, session['user_id']))
    trip = cursor.fetchone()

    if not trip:
        flash('Trip not found', 'danger')
        return redirect(url_for('trip.trips'))

    # Create a copy of the trip
    cursor.execute('''
        INSERT INTO trips (user_id, destination, start_date, end_date, budget, preferences, itinerary)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (
        session['user_id'],
        trip['destination'],
        trip['start_date'],
        trip['end_date'],
        trip['budget'],
        trip['preferences'],
        trip['itinerary']
    ))
    mysql.connection.commit()
    new_trip_id = cursor.lastrowid
    cursor.close()

    flash('Trip duplicated successfully!', 'success')
    return redirect(url_for('trip.view_trip', trip_id=new_trip_id))

@trip_bp.route('/trips/<int:trip_id>/export')
@login_required
def export_trip(trip_id):
    # Get trip details
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips
        WHERE id = %s AND user_id = %s
    ''', (trip_id, session['user_id']))
    trip = cursor.fetchone()
    cursor.close()

    if not trip:
        flash('Trip not found', 'danger')
        return redirect(url_for('trip.trips'))

    # For now, just redirect back to the trip view with a message
    # In a real implementation, this would generate a PDF or other export format
    flash('Export functionality will be implemented in a future update', 'info')
    return redirect(url_for('trip.view_trip', trip_id=trip_id))

def generate_itinerary(destination, start_date, end_date, budget, preferences):
    """Generate an itinerary using Groq AI or fallback to mock data"""
    # Calculate number of days
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    num_days = (end_date_obj - start_date_obj).days + 1

    # Check if Groq client is available
    if groq_client is None:
        print("Groq client not initialized. Using mock itinerary.")
        return generate_mock_itinerary(destination, start_date_obj, end_date_obj, num_days, budget, preferences)

    # Create prompt for Groq AI
    prompt = f"""
    Create a detailed travel itinerary for a trip to {destination}.
    Trip details:
    - Duration: {num_days} days (from {start_date} to {end_date})
    - Budget: ${budget}
    - Preferences: {preferences}

    Please provide a day-by-day itinerary with:
    1. Morning activities
    2. Lunch recommendations
    3. Afternoon activities
    4. Dinner recommendations
    5. Evening activities (if applicable)
    6. Accommodation suggestions

    For each activity, include:
    - Name of the place/activity
    - Brief description
    - Estimated cost
    - Time required

    Format the response as a JSON object with the following structure:
    {{
        "destination": "{destination}",
        "duration": {num_days},
        "budget": {budget},
        "days": [
            {{
                "day": 1,
                "date": "{start_date}",
                "morning": [
                    {{
                        "activity": "Activity name",
                        "description": "Brief description",
                        "cost": "Estimated cost",
                        "duration": "Time required"
                    }}
                ],
                "lunch": {{
                    "place": "Restaurant name",
                    "description": "Brief description",
                    "cost": "Estimated cost"
                }},
                "afternoon": [...],
                "dinner": {{...}},
                "evening": [...],
                "accommodation": {{
                    "name": "Hotel/Accommodation name",
                    "description": "Brief description",
                    "cost": "Estimated cost per night"
                }}
            }},
            ...
        ]
    }}
    """

    try:
        print(f"Attempting to generate itinerary for {destination} using Groq API")

        # Check if Groq client is properly initialized
        if groq_client is None:
            print("Groq client is not initialized. Falling back to mock data.")
            raise Exception("Groq client is not initialized")

        # Try different models if one fails
        models = ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]
        last_error = None

        for model in models:
            try:
                print(f"Trying model: {model}")
                # Call Groq API
                response = groq_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a travel planning assistant that creates detailed itineraries."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )

                # Parse the response
                itinerary_text = response.choices[0].message.content
                print(f"Received response from Groq API using model {model}")

                # Extract JSON from the response
                try:
                    # Try to parse the JSON directly
                    print("Attempting to parse JSON directly")
                    itinerary_json = json.loads(itinerary_text)
                    print("Successfully parsed JSON")
                except json.JSONDecodeError:
                    # If direct parsing fails, try to extract JSON from markdown code blocks
                    print("Direct JSON parsing failed, trying to extract from code blocks")
                    import re
                    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', itinerary_text)
                    if json_match:
                        try:
                            print("Found JSON code block, attempting to parse")
                            itinerary_json = json.loads(json_match.group(1))
                            print("Successfully parsed JSON from code block")
                        except json.JSONDecodeError as e:
                            print(f"Failed to parse JSON from code block: {e}")
                            print(f"Content: {json_match.group(1)[:100]}...")
                            raise Exception(f"Failed to parse JSON from code block: {e}")
                    else:
                        print("No JSON code block found in response")
                        print(f"Response content (first 200 chars): {itinerary_text[:200]}...")
                        raise Exception("No valid JSON found in response")

                # Validate the structure of the JSON
                if "destination" not in itinerary_json or "days" not in itinerary_json:
                    print(f"Invalid itinerary structure. Keys found: {list(itinerary_json.keys())}")
                    raise Exception("Invalid itinerary structure")

                print("Successfully generated and validated itinerary")
                return itinerary_json

            except Exception as e:
                print(f"Error with model {model}: {e}")
                last_error = e
                continue

        # If we've tried all models and none worked
        raise Exception(f"All models failed. Last error: {last_error}")
    except Exception as e:
        # If there's an error, log it and return a mock itinerary
        print(f"Error generating itinerary: {e}")
        return generate_mock_itinerary(destination, start_date_obj, end_date_obj, num_days, budget, preferences)

def generate_mock_itinerary(destination, start_date_obj, end_date_obj, num_days, budget, preferences):
    """Generate a mock itinerary when Groq API is unavailable or fails"""
    print(f"Generating mock itinerary for {destination}")

    try:
        # Try to use the enhanced itinerary generator
        from utils.itinerary_generator import itinerary_generator
        return itinerary_generator.generate_itinerary(
            destination,
            start_date_obj.strftime('%Y-%m-%d'),
            end_date_obj.strftime('%Y-%m-%d'),
            budget,
            preferences
        )
    except Exception as e:
        print(f"Error using enhanced itinerary generator: {e}")
        print("Falling back to basic mock itinerary")

        # Create a list of sample activities for each destination
        activities = {
            "morning": [
                {"activity": "City Walking Tour", "description": "Explore the city with a local guide", "cost": "$25", "duration": "3 hours"},
                {"activity": "Museum Visit", "description": "Explore local history and culture", "cost": "$15", "duration": "2 hours"},
                {"activity": "Local Market", "description": "Shop for local goods and souvenirs", "cost": "$0-30", "duration": "1.5 hours"},
                {"activity": "Scenic Hike", "description": "Enjoy nature and panoramic views", "cost": "$0", "duration": "3 hours"},
                {"activity": "Bike Rental", "description": "Explore the area on two wheels", "cost": "$20", "duration": "4 hours"}
            ],
            "lunch": [
                {"place": "Local Café", "description": "Casual dining with local specialties", "cost": "$15-25"},
                {"place": "Street Food Market", "description": "Try various local street foods", "cost": "$10-20"},
                {"place": "Waterfront Restaurant", "description": "Enjoy seafood with a view", "cost": "$20-35"},
                {"place": "Historic Tavern", "description": "Traditional food in a historic setting", "cost": "$15-30"},
                {"place": "Food Truck Park", "description": "Various cuisines in a casual setting", "cost": "$10-15"}
            ],
            "afternoon": [
                {"activity": "Beach Time", "description": "Relax on the sandy shores", "cost": "$0-10", "duration": "3 hours"},
                {"activity": "Historical Site", "description": "Visit important landmarks", "cost": "$15", "duration": "2 hours"},
                {"activity": "Boat Tour", "description": "See the area from the water", "cost": "$40", "duration": "1.5 hours"},
                {"activity": "Shopping District", "description": "Explore local shops and boutiques", "cost": "Varies", "duration": "2 hours"},
                {"activity": "Art Gallery", "description": "Appreciate local and international art", "cost": "$12", "duration": "1.5 hours"}
            ],
            "dinner": [
                {"place": "Fine Dining Restaurant", "description": "Upscale local cuisine", "cost": "$50-80"},
                {"place": "Family-owned Bistro", "description": "Authentic local dishes", "cost": "$25-40"},
                {"place": "Rooftop Restaurant", "description": "Dinner with a panoramic view", "cost": "$35-60"},
                {"place": "Seafood Grill", "description": "Fresh seafood specialties", "cost": "$30-50"},
                {"place": "International Cuisine", "description": "Global flavors in a modern setting", "cost": "$25-45"}
            ],
            "evening": [
                {"activity": "Live Music Venue", "description": "Enjoy local performers", "cost": "$15-30", "duration": "2 hours"},
                {"activity": "Night Walking Tour", "description": "See the city lights", "cost": "$25", "duration": "1.5 hours"},
                {"activity": "Local Bar", "description": "Try local drinks and meet people", "cost": "$20-40", "duration": "2 hours"},
                {"activity": "Theater Show", "description": "Watch a local performance", "cost": "$35", "duration": "2 hours"},
                {"activity": "Sunset Viewpoint", "description": "Enjoy the sunset from a scenic spot", "cost": "$0", "duration": "1 hour"}
            ],
            "accommodation": [
                {"name": "Boutique Hotel", "description": "Charming hotel in a central location", "cost": "$120-180 per night"},
                {"name": "City Center Apartment", "description": "Self-catering accommodation near attractions", "cost": "$100-150 per night"},
                {"name": "Beachfront Resort", "description": "Luxury accommodation with ocean views", "cost": "$180-250 per night"},
                {"name": "Historic Inn", "description": "Stay in a building with character", "cost": "$90-130 per night"},
                {"name": "Modern Hotel", "description": "Contemporary comfort with amenities", "cost": "$110-160 per night"}
            ]
        }

        # Create the itinerary structure
        itinerary = {
            "destination": destination,
            "duration": num_days,
            "budget": budget,
            "preferences": preferences,
            "days": []
        }

        # Generate a day-by-day itinerary
        import random
        for i in range(num_days):
            current_date = (start_date_obj + timedelta(days=i)).strftime('%Y-%m-%d')

            # Select random activities for each part of the day
            morning_activity = random.choice(activities["morning"])
            lunch = random.choice(activities["lunch"])
            afternoon_activity = random.choice(activities["afternoon"])
            dinner = random.choice(activities["dinner"])
            evening_activity = random.choice(activities["evening"])
            accommodation = random.choice(activities["accommodation"])

            # Add the day to the itinerary
            day = {
                "day": i + 1,
                "date": current_date,
                "morning": [morning_activity],
                "lunch": lunch,
                "afternoon": [afternoon_activity],
                "dinner": dinner,
                "evening": [evening_activity],
                "accommodation": accommodation
            }

            itinerary["days"].append(day)

        return itinerary