from flask import Blueprint, jsonify, request
import requests
import os
from datetime import datetime, timedelta
from utils.auth_utils import login_required

weather_bp = Blueprint('weather', __name__)

# OpenWeatherMap API key
WEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

@weather_bp.route('/weather/<location>')
@login_required
def get_weather(location):
    """Get current weather for a location"""
    try:
        # Call OpenWeatherMap API
        response = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather',
            params={
                'q': location,
                'appid': WEATHER_API_KEY,
                'units': 'metric'  # Use metric units (Celsius)
            }
        )
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'message': f'Error fetching weather data: {response.json().get("message", "Unknown error")}'
            }), response.status_code
        
        # Parse response
        data = response.json()
        
        # Extract relevant information
        weather = {
            'location': location,
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'weather': data['weather'][0]['main'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
            'wind_speed': data['wind']['speed'],
            'clouds': data['clouds']['all'],
            'timestamp': datetime.fromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify({
            'success': True,
            'data': weather
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@weather_bp.route('/weather/forecast/<location>')
@login_required
def get_weather_forecast(location):
    """Get 5-day weather forecast for a location"""
    try:
        # Get start and end dates from query parameters (optional)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Call OpenWeatherMap API for 5-day forecast
        response = requests.get(
            f'https://api.openweathermap.org/data/2.5/forecast',
            params={
                'q': location,
                'appid': WEATHER_API_KEY,
                'units': 'metric'  # Use metric units (Celsius)
            }
        )
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'message': f'Error fetching forecast data: {response.json().get("message", "Unknown error")}'
            }), response.status_code
        
        # Parse response
        data = response.json()
        
        # Extract relevant information
        forecast_items = data['list']
        
        # Filter by date range if provided
        if start_date and end_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Include end date
            
            forecast_items = [
                item for item in forecast_items
                if start_date_obj <= datetime.fromtimestamp(item['dt']) < end_date_obj
            ]
        
        # Group forecast by day
        forecast_by_day = {}
        
        for item in forecast_items:
            dt = datetime.fromtimestamp(item['dt'])
            day = dt.strftime('%Y-%m-%d')
            
            if day not in forecast_by_day:
                forecast_by_day[day] = []
            
            forecast_by_day[day].append({
                'time': dt.strftime('%H:%M'),
                'temperature': item['main']['temp'],
                'feels_like': item['main']['feels_like'],
                'humidity': item['main']['humidity'],
                'pressure': item['main']['pressure'],
                'weather': item['weather'][0]['main'],
                'description': item['weather'][0]['description'],
                'icon': item['weather'][0]['icon'],
                'wind_speed': item['wind']['speed'],
                'clouds': item['clouds']['all']
            })
        
        # Calculate daily averages
        daily_forecast = []
        
        for day, items in forecast_by_day.items():
            # Calculate averages
            avg_temp = sum(item['temperature'] for item in items) / len(items)
            avg_humidity = sum(item['humidity'] for item in items) / len(items)
            
            # Find most common weather condition
            weather_counts = {}
            for item in items:
                weather = item['weather']
                weather_counts[weather] = weather_counts.get(weather, 0) + 1
            
            most_common_weather = max(weather_counts.items(), key=lambda x: x[1])[0]
            
            # Get icon for most common weather
            icon = next(item['icon'] for item in items if item['weather'] == most_common_weather)
            
            # Get description for most common weather
            description = next(item['description'] for item in items if item['weather'] == most_common_weather)
            
            daily_forecast.append({
                'date': day,
                'avg_temperature': round(avg_temp, 1),
                'avg_humidity': round(avg_humidity, 1),
                'weather': most_common_weather,
                'description': description,
                'icon': icon,
                'hourly_forecast': items
            })
        
        # Sort by date
        daily_forecast.sort(key=lambda x: x['date'])
        
        return jsonify({
            'success': True,
            'location': location,
            'forecast': daily_forecast
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500