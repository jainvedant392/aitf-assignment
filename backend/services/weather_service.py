import requests
from datetime import datetime
from config import Config

class WeatherService:
    def __init__(self):
        self.base_url = Config.OPENMETEO_BASE_URL
        self.geocoding_url = 'https://geocoding-api.open-meteo.com/v1/search'
    
    def get_coordinates(self, city="Tokyo", country_code="JP"):
        """Get latitude and longitude for a city"""
        try:
            params = {
                'name': city,
                'count': 1,
                'language': 'en',
                'format': 'json'
            }
            
            response = requests.get(self.geocoding_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('results') and len(data['results']) > 0:
                result = data['results'][0]
                return {
                    'success': True,
                    'latitude': result['latitude'],
                    'longitude': result['longitude'],
                    'location_name': f"{result['name']}, {result.get('country', '')}"
                }
            else:
                # Fallback to Tokyo coordinates
                return {
                    'success': True,
                    'latitude': 35.6762,
                    'longitude': 139.6503,
                    'location_name': 'Tokyo, Japan'
                }
                
        except Exception as e:
            # Fallback to Tokyo coordinates
            return {
                'success': True,
                'latitude': 35.6762,
                'longitude': 139.6503,
                'location_name': 'Tokyo, Japan'
            }
    
    def get_current_weather(self, city="Tokyo", country_code="JP"):
        """Get current weather for specified location using OpenMeteo"""
        try:
            # Get coordinates for the city
            coords = self.get_coordinates(city, country_code)
            if not coords['success']:
                return {'success': False, 'error': 'Could not find location coordinates'}
            
            # OpenMeteo API parameters
            params = {
                'latitude': coords['latitude'],
                'longitude': coords['longitude'],
                'current': [
                    'temperature_2m',
                    'relative_humidity_2m', 
                    'apparent_temperature',
                    'precipitation',
                    'weather_code',
                    'surface_pressure',
                    'wind_speed_10m',
                    'wind_direction_10m'
                ],
                'hourly': [
                    'soil_temperature_0cm',
                    'soil_moisture_0_1cm'
                ],
                'timezone': 'auto',
                'forecast_days': 1
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            current = data['current']
            
            return {
                'success': True,
                'data': {
                    'location': coords['location_name'],
                    'temperature': current['temperature_2m'],
                    'feels_like': current['apparent_temperature'],
                    'humidity': current['relative_humidity_2m'],
                    'description': self.get_weather_description(current['weather_code']),
                    'wind_speed': current['wind_speed_10m'],
                    'wind_direction': current['wind_direction_10m'],
                    'pressure': current['surface_pressure'],
                    'precipitation': current.get('precipitation', 0),
                    'soil_temperature': data['hourly']['soil_temperature_0cm'][0] if data.get('hourly') else None,
                    'soil_moisture': data['hourly']['soil_moisture_0_1cm'][0] if data.get('hourly') else None,
                    'timestamp': datetime.now().isoformat(),
                    'weather_code': current['weather_code']
                }
            }
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f"Weather API error: {str(e)}"}
        except KeyError as e:
            return {'success': False, 'error': f"Invalid response format: {str(e)}"}
    
    def get_forecast(self, city="Tokyo", country_code="JP", days=5):
        """Get weather forecast for specified location"""
        try:
            coords = self.get_coordinates(city, country_code)
            if not coords['success']:
                return {'success': False, 'error': 'Could not find location coordinates'}
            
            params = {
                'latitude': coords['latitude'],
                'longitude': coords['longitude'],
                'daily': [
                    'temperature_2m_max',
                    'temperature_2m_min',
                    'weather_code',
                    'precipitation_sum',
                    'wind_speed_10m_max'
                ],
                'timezone': 'auto',
                'forecast_days': min(days, 16)  # OpenMeteo max is 16 days
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            daily = data['daily']
            forecast_list = []
            
            for i in range(len(daily['time'])):
                forecast_list.append({
                    'date': daily['time'][i],
                    'temperature_max': daily['temperature_2m_max'][i],
                    'temperature_min': daily['temperature_2m_min'][i],
                    'description': self.get_weather_description(daily['weather_code'][i]),
                    'precipitation': daily['precipitation_sum'][i],
                    'wind_speed': daily['wind_speed_10m_max'][i],
                    'weather_code': daily['weather_code'][i]
                })
            
            return {
                'success': True,
                'data': {
                    'location': coords['location_name'],
                    'forecast': forecast_list
                }
            }
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f"Forecast API error: {str(e)}"}
        except KeyError as e:
            return {'success': False, 'error': f"Invalid response format: {str(e)}"}
    
    def get_weather_description(self, weather_code):
        """Convert OpenMeteo weather code to description"""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy", 
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(weather_code, "Unknown weather condition")
    
    def analyze_weather_for_agriculture(self, weather_data):
        """Analyze weather conditions for agricultural activities"""
        if not weather_data.get('success'):
            return weather_data
        
        data = weather_data['data']
        temp = data['temperature']
        humidity = data['humidity']
        wind_speed = data['wind_speed']
        precipitation = data.get('precipitation', 0)
        weather_code = data.get('weather_code', 0)
        
        analysis = {
            'suitable_for_fieldwork': True,
            'irrigation_needed': False,
            'pest_risk': 'low',
            'recommendations': []
        }
        
        # Temperature analysis
        if temp < 5:
            analysis['suitable_for_fieldwork'] = False
            analysis['recommendations'].append("Too cold for most field activities")
        elif temp > 35:
            analysis['suitable_for_fieldwork'] = False
            analysis['recommendations'].append("Too hot - avoid heavy fieldwork during day")
        elif temp < 10:
            analysis['recommendations'].append("Cold weather - protect sensitive plants")
        elif temp > 30:
            analysis['recommendations'].append("Hot weather - ensure adequate watering")
        
        # Humidity analysis
        if humidity < 40:
            analysis['irrigation_needed'] = True
            analysis['recommendations'].append("Low humidity - consider irrigation")
        elif humidity > 80:
            analysis['pest_risk'] = 'high'
            analysis['recommendations'].append("High humidity - monitor for fungal diseases")
        
        # Wind analysis
        if wind_speed > 10:
            analysis['recommendations'].append("High winds - avoid spraying pesticides")
            if wind_speed > 15:
                analysis['suitable_for_fieldwork'] = False
                analysis['recommendations'].append("Very strong winds - postpone outdoor work")
        
        # Precipitation analysis
        if precipitation > 0:
            if precipitation < 2:
                analysis['recommendations'].append("Light rain - good for recently planted crops")
            elif precipitation < 10:
                analysis['recommendations'].append("Moderate rain - avoid heavy machinery use")
            else:
                analysis['suitable_for_fieldwork'] = False
                analysis['recommendations'].append("Heavy rain - postpone fieldwork")
        
        # Weather code specific advice
        if weather_code >= 95:  # Thunderstorms
            analysis['suitable_for_fieldwork'] = False
            analysis['recommendations'].append("Thunderstorm conditions - stay indoors")
        elif weather_code >= 71 and weather_code <= 77:  # Snow
            analysis['suitable_for_fieldwork'] = False
            analysis['recommendations'].append("Snow conditions - protect crops from frost")
        
        # Soil conditions (if available)
        if data.get('soil_temperature') is not None:
            soil_temp = data['soil_temperature']
            if soil_temp < 5:
                analysis['recommendations'].append("Soil too cold for planting")
            elif soil_temp > 30:
                analysis['recommendations'].append("Very warm soil - good for germination")
        
        if data.get('soil_moisture') is not None:
            soil_moisture = data['soil_moisture']
            if soil_moisture < 0.1:
                analysis['irrigation_needed'] = True
                analysis['recommendations'].append("Dry soil - irrigation recommended")
            elif soil_moisture > 0.4:
                analysis['recommendations'].append("High soil moisture - good for crops")
        
    def search_locations(self, query, limit=5):
        """Search for locations using geocoding API"""
        try:
            params = {
                'name': query,
                'count': limit,
                'language': 'en',
                'format': 'json'
            }
            
            response = requests.get(self.geocoding_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            locations = []
            if data.get('results'):
                for result in data['results']:
                    locations.append({
                        'name': result['name'],
                        'country': result.get('country', ''),
                        'latitude': result['latitude'],
                        'longitude': result['longitude'],
                        'admin1': result.get('admin1', ''),
                        'timezone': result.get('timezone', '')
                    })
            
            return {
                'success': True,
                'locations': locations,
                'query': query
            }
            
        except Exception as e:
            return {'success': False, 'error': f"Location search error: {str(e)}"}
    
    def get_historical_weather(self, city="Tokyo", country_code="JP", days=7):
        """Get historical weather data for the past few days"""
        try:
            from datetime import datetime, timedelta
            
            # Get coordinates
            coords = self.get_coordinates(city, country_code)
            if not coords['success']:
                return coords
            
            # Calculate date range (past 7 days)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            params = {
                'latitude': coords['latitude'],
                'longitude': coords['longitude'],
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'daily': [
                    'temperature_2m_max',
                    'temperature_2m_min',
                    'precipitation_sum',
                    'weather_code'
                ],
                'timezone': 'auto'
            }
            
            # Use historical endpoint
            historical_url = 'https://archive-api.open-meteo.com/v1/archive'
            response = requests.get(historical_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            daily = data['daily']
            historical_data = []
            
            for i in range(len(daily['time'])):
                historical_data.append({
                    'date': daily['time'][i],
                    'temperature_max': daily['temperature_2m_max'][i],
                    'temperature_min': daily['temperature_2m_min'][i],
                    'precipitation': daily['precipitation_sum'][i],
                    'weather_description': self.get_weather_description(daily['weather_code'][i])
                })
            
            return {
                'success': True,
                'data': {
                    'location': coords['location_name'],
                    'historical_data': historical_data,
                    'period': f"{start_date} to {end_date}"
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': f"Historical weather error: {str(e)}"}