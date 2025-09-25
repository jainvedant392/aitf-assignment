"""
Weather API routes for Agriculture Helper
Handles all weather-related endpoints using OpenMeteo API
"""

from flask import Blueprint, request, jsonify
from services.weather_service import WeatherService
from datetime import datetime

# Create blueprint
weather_bp = Blueprint('weather', __name__, url_prefix='/api/weather')

# Initialize weather service
weather_service = WeatherService()

def safe_validate_location(city, country):
    """Safe location validation that won't return None"""
    try:
        # Simple validation without external dependencies
        city = city.strip() if city else 'Tokyo'
        country = country.strip().upper() if country else 'JP'
        
        # Basic validation
        if not city or len(city) > 100:
            city = 'Tokyo'
        if not country or len(country) > 3:
            country = 'JP'
            
        return city, country
    except:
        return 'Tokyo', 'JP'

@weather_bp.route('/current', methods=['GET'])
def get_current_weather():
    """
    Get current weather for specified location with agricultural analysis
    """
    try:
        city = request.args.get('city', 'Tokyo')
        country = request.args.get('country', 'JP')
        
        print(f"Weather route: city={city}, country={country}")
        
        # Safe validation
        city, country = safe_validate_location(city, country)
        print(f"After validation: city={city}, country={country}")
        
        # Get current weather data
        weather_data = weather_service.get_current_weather(city, country)
        print(f"Weather service returned: {type(weather_data)}, success: {weather_data.get('success') if weather_data else None}")
        
        if not weather_data:
            print("Weather data is None!")
            return jsonify({'success': False, 'error': 'Weather service returned None'}), 500
        
        if weather_data.get('success'):
            print("Weather data successful, adding agricultural analysis...")
            
            # Safe agricultural analysis
            try:
                agricultural_weather = weather_service.analyze_weather_for_agriculture(weather_data)
                print(f"Agricultural analysis: {type(agricultural_weather)}, success: {agricultural_weather.get('success') if agricultural_weather else None}")
                
                if agricultural_weather and agricultural_weather.get('success'):
                    return jsonify(agricultural_weather)
                else:
                    print("Agricultural analysis returned None, using original weather data")
                    # Add basic agricultural context to original weather data
                    enhanced_weather = weather_data.copy()
                    temp = weather_data['data']['temperature']
                    humidity = weather_data['data']['humidity']
                    
                    # Basic agricultural advice
                    agricultural_analysis = {
                        'suitable_for_fieldwork': True,
                        'irrigation_needed': humidity < 40 or temp > 30,
                        'pest_risk': 'high' if humidity > 80 else 'low',
                        'recommendations': []
                    }
                    
                    if temp > 30:
                        agricultural_analysis['recommendations'].append("Hot weather - avoid heavy work during day")
                    if humidity > 80:
                        agricultural_analysis['recommendations'].append("High humidity - monitor for fungal diseases")
                    if humidity < 40:
                        agricultural_analysis['recommendations'].append("Low humidity - increase irrigation")
                    
                    enhanced_weather['agricultural_analysis'] = agricultural_analysis
                    return jsonify(enhanced_weather)
            except Exception as e:
                print(f"Agricultural analysis failed: {e}")
                return jsonify(weather_data)
        else:
            print(f"Weather service error: {weather_data.get('error')}")
            return jsonify(weather_data), 400
            
    except Exception as e:
        print(f"Weather route exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': f'Weather route error: {str(e)}'
        }), 500

@weather_bp.route('/forecast', methods=['GET'])
def get_weather_forecast():
    """Get weather forecast for specified location"""
    try:
        city = request.args.get('city', 'Tokyo')
        country = request.args.get('country', 'JP')
        days = min(int(request.args.get('days', 3)), 16)
        
        city, country = safe_validate_location(city, country)
        
        forecast_data = weather_service.get_forecast(city, country, days)
        if forecast_data:
            return jsonify(forecast_data)
        else:
            return jsonify({'success': False, 'error': 'Forecast service returned None'}), 500
        
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Invalid days parameter: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Forecast error: {str(e)}'}), 500

@weather_bp.route('/locations/search', methods=['GET'])
def search_locations():
    """Search for locations using geocoding"""
    try:
        query = request.args.get('query', '').strip()
        limit = min(int(request.args.get('limit', 5)), 10)
        
        if not query:
            return jsonify({'success': False, 'error': 'Query parameter is required'}), 400
        
        locations = weather_service.search_locations(query, limit)
        if locations:
            return jsonify(locations)
        else:
            return jsonify({'success': False, 'error': 'Location search returned None'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Location search error: {str(e)}'}), 500

@weather_bp.route('/historical', methods=['GET'])
def get_historical_weather():
    """Get historical weather data (last 7 days)"""
    try:
        city = request.args.get('city', 'Tokyo')
        country = request.args.get('country', 'JP')
        
        city, country = safe_validate_location(city, country)
        
        historical_data = weather_service.get_historical_weather(city, country)
        if historical_data:
            return jsonify(historical_data)
        else:
            return jsonify({'success': False, 'error': 'Historical service returned None'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Historical weather error: {str(e)}'}), 500
