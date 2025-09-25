"""
Helper functions and utilities for Agriculture Helper API
Contains validation, formatting, and common utility functions
"""

import re
import html
from datetime import datetime
from flask import jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_location(city, country):
    """
    Validate and sanitize location parameters
    
    Args:
        city (str): City name
        country (str): Country code
        
    Returns:
        tuple: Validated (city, country) tuple
        
    Raises:
        ValueError: If validation fails
    """
    # Sanitize inputs
    city = sanitize_input(city.strip()) if city else 'Tokyo'
    country = sanitize_input(country.strip().upper()) if country else 'JP'
    
    # Validate city name (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-']+$", city):
        raise ValueError(f"Invalid city name: {city}")
    
    # Validate country code (2-3 letter codes)
    if not re.match(r"^[A-Z]{2,3}$", country):
        raise ValueError(f"Invalid country code: {country}")
    
    # Length limits
    if len(city) > 100:
        raise ValueError("City name too long")
    
    return city, country

def validate_chat_input(data):
    """
    Validate chat input data
    
    Args:
        data (dict): Request data from chat endpoint
        
    Returns:
        dict: Validation result with 'valid' and optional 'error' keys
    """
    if not data:
        return {'valid': False, 'error': 'Request body is required'}
    
    message = data.get('message', '').strip()
    if not message:
        return {'valid': False, 'error': 'Message is required'}
    
    # Check message length
    if len(message) > 1000:
        return {'valid': False, 'error': 'Message too long (max 1000 characters)'}
    
    # Check for potentially harmful content (basic)
    if contains_harmful_content(message):
        return {'valid': False, 'error': 'Message contains inappropriate content'}
    
    # Validate language parameter if provided
    language = data.get('language', 'japanese')
    if language not in ['japanese', 'english']:
        return {'valid': False, 'error': 'Supported languages: japanese, english'}
    
    return {'valid': True}

def handle_api_error(error, default_message="An error occurred"):
    """
    Handle API errors and return consistent error responses
    
    Args:
        error (Exception): The error that occurred
        default_message (str): Default error message
        
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    error_message = str(error)
    
    # Log the error
    logger.error(f"API Error: {error_message}")
    
    # Don't expose internal error details in production
    public_message = default_message
    
    # Map specific error types to more user-friendly messages
    if "connection" in error_message.lower():
        public_message = "Unable to connect to external service. Please try again."
    elif "timeout" in error_message.lower():
        public_message = "Request timed out. Please try again."
    elif "api key" in error_message.lower():
        public_message = "API configuration error. Please contact support."
    elif "rate limit" in error_message.lower():
        public_message = "Too many requests. Please wait a moment and try again."
    
    return jsonify({
        'success': False,
        'error': public_message,
        'timestamp': datetime.now().isoformat()
    }), 500

def sanitize_input(text):
    """
    Sanitize user input to prevent XSS and other attacks
    
    Args:
        text (str): Input text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not isinstance(text, str):
        return str(text)
    
    # HTML escape
    text = html.escape(text)
    
    # Remove potentially dangerous characters for file paths
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    
    # Limit length
    return text[:500]

def format_temperature(temp_celsius, unit='celsius'):
    """
    Format temperature with appropriate unit
    
    Args:
        temp_celsius (float): Temperature in Celsius
        unit (str): Target unit ('celsius' or 'fahrenheit')
        
    Returns:
        str: Formatted temperature string
    """
    if unit.lower() == 'fahrenheit':
        temp_f = (temp_celsius * 9/5) + 32
        return f"{temp_f:.1f}°F"
    else:
        return f"{temp_celsius:.1f}°C"

def format_timestamp(timestamp=None, format_type='iso'):
    """
    Format timestamp in various formats
    
    Args:
        timestamp (datetime, optional): Timestamp to format (default: now)
        format_type (str): Format type ('iso', 'friendly', 'date_only')
        
    Returns:
        str: Formatted timestamp
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    if format_type == 'iso':
        return timestamp.isoformat()
    elif format_type == 'friendly':
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    elif format_type == 'date_only':
        return timestamp.strftime('%Y-%m-%d')
    elif format_type == 'japanese':
        return timestamp.strftime('%Y年%m月%d日 %H時%M分')
    else:
        return timestamp.isoformat()

def contains_harmful_content(text):
    """
    Basic check for potentially harmful content
    
    Args:
        text (str): Text to check
        
    Returns:
        bool: True if harmful content detected
    """
    # Basic harmful patterns (this would be more sophisticated in production)
    harmful_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',  # HTML event handlers
        r'eval\s*\(',
        r'exec\s*\(',
    ]
    
    text_lower = text.lower()
    for pattern in harmful_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def validate_coordinates(latitude, longitude):
    """
    Validate geographic coordinates
    
    Args:
        latitude (float): Latitude value
        longitude (float): Longitude value
        
    Returns:
        bool: True if coordinates are valid
    """
    try:
        lat = float(latitude)
        lng = float(longitude)
        
        if -90 <= lat <= 90 and -180 <= lng <= 180:
            return True
        return False
    except (ValueError, TypeError):
        return False

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two geographic points using Haversine formula
    
    Args:
        lat1, lon1 (float): First point coordinates
        lat2, lon2 (float): Second point coordinates
        
    Returns:
        float: Distance in kilometers
    """
    import math
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth radius in kilometers
    r = 6371
    
    return c * r

def format_weather_description(weather_code):
    """
    Format weather description for user display
    
    Args:
        weather_code (int): OpenMeteo weather code
        
    Returns:
        dict: Formatted weather information with emoji and description
    """
    weather_descriptions = {
        0: {"description": "Clear sky", "emoji": "☀️", "category": "clear"},
        1: {"description": "Mainly clear", "emoji": "🌤️", "category": "clear"},
        2: {"description": "Partly cloudy", "emoji": "⛅", "category": "cloudy"},
        3: {"description": "Overcast", "emoji": "☁️", "category": "cloudy"},
        45: {"description": "Fog", "emoji": "🌫️", "category": "fog"},
        48: {"description": "Depositing rime fog", "emoji": "🌫️", "category": "fog"},
        51: {"description": "Light drizzle", "emoji": "🌦️", "category": "rain"},
        53: {"description": "Moderate drizzle", "emoji": "🌦️", "category": "rain"},
        55: {"description": "Dense drizzle", "emoji": "🌧️", "category": "rain"},
        61: {"description": "Slight rain", "emoji": "🌧️", "category": "rain"},
        63: {"description": "Moderate rain", "emoji": "🌧️", "category": "rain"},
        65: {"description": "Heavy rain", "emoji": "🌧️", "category": "rain"},
        71: {"description": "Slight snow", "emoji": "🌨️", "category": "snow"},
        73: {"description": "Moderate snow", "emoji": "❄️", "category": "snow"},
        75: {"description": "Heavy snow", "emoji": "❄️", "category": "snow"},
        80: {"description": "Slight rain showers", "emoji": "🌦️", "category": "rain"},
        81: {"description": "Moderate rain showers", "emoji": "🌦️", "category": "rain"},
        82: {"description": "Violent rain showers", "emoji": "⛈️", "category": "storm"},
        95: {"description": "Thunderstorm", "emoji": "⛈️", "category": "storm"},
        96: {"description": "Thunderstorm with hail", "emoji": "⛈️", "category": "storm"},
        99: {"description": "Thunderstorm with heavy hail", "emoji": "⛈️", "category": "storm"}
    }
    
    return weather_descriptions.get(weather_code, {
        "description": "Unknown weather",
        "emoji": "❓",
        "category": "unknown"
    })

def get_agricultural_advice_template(crop_type, weather_condition):
    """
    Get template for agricultural advice based on crop and weather
    
    Args:
        crop_type (str): Type of crop
        weather_condition (str): Weather condition category
        
    Returns:
        str: Advice template
    """
    templates = {
        'rice': {
            'rain': '稲作では適度な降雨が重要です。現在の雨は水田の水位管理に役立ちます。',
            'sun': '晴天は稲の光合成に良好です。水位を監視し、必要に応じて灌漑してください。',
            'cloudy': '曇天では病気のリスクが高まる可能性があります。換気と監視を強化してください。'
        },
        'tomato': {
            'rain': 'トマトは過度の雨を嫌います。排水を確保し、病気の予防に注意してください。',
            'sun': '晴天はトマトの成長に最適です。適切な水やりを継続してください。',
            'cloudy': '湿度が高い場合は、うどんこ病などに注意が必要です。'
        },
        'general': {
            'rain': '雨天時は排水に注意し、病害虫の監視を強化してください。',
            'sun': '晴天を活用して必要な農作業を進めてください。',
            'cloudy': '曇天時は湿度管理と病気の予防に注意してください。'
        }
    }
    
    crop_templates = templates.get(crop_type, templates['general'])
    return crop_templates.get(weather_condition, crop_templates.get('general', '天候に応じた適切な管理を行ってください。'))

def parse_growth_stage(stage_input):
    """
    Parse and validate growth stage input
    
    Args:
        stage_input (str): Growth stage input
        
    Returns:
        str: Standardized growth stage
    """
    stage_mapping = {
        'seedling': 'seedling',
        'vegetative': 'vegetative',
        'flowering': 'flowering',
        'fruiting': 'fruiting',
        'harvest': 'harvest',
        'maturity': 'maturity',
        '苗': 'seedling',
        '栄養成長期': 'vegetative',
        '開花期': 'flowering',
        '結実期': 'fruiting',
        '収穫期': 'harvest',
        '成熟期': 'maturity'
    }
    
    if stage_input:
        stage_lower = stage_input.lower()
        return stage_mapping.get(stage_lower, 'general')
    
    return 'general'

def validate_api_rate_limit(client_id, max_requests=100, time_window=3600):
    """
    Basic rate limiting validation (in production, use Redis or similar)
    
    Args:
        client_id (str): Client identifier
        max_requests (int): Maximum requests allowed
        time_window (int): Time window in seconds
        
    Returns:
        bool: True if request is allowed
    """
    # This is a simplified version - in production, implement proper rate limiting
    # with Redis, database, or memory store with expiration
    return True

def generate_response_id():
    """
    Generate unique response ID for tracking
    
    Returns:
        str: Unique response ID
    """
    import uuid
    return str(uuid.uuid4())

def log_api_usage(endpoint, client_id, response_time, status_code):
    """
    Log API usage for monitoring and analytics
    
    Args:
        endpoint (str): API endpoint
        client_id (str): Client identifier  
        response_time (float): Response time in seconds
        status_code (int): HTTP status code
    """
    logger.info(f"API Usage - Endpoint: {endpoint}, Client: {client_id}, "
                f"Response Time: {response_time:.3f}s, Status: {status_code}")

def create_success_response(data, message=None):
    """
    Create standardized success response
    
    Args:
        data: Response data
        message (str, optional): Success message
        
    Returns:
        dict: Standardized success response
    """
    response = {
        'success': True,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    
    if message:
        response['message'] = message
    
    return response

def create_error_response(error_message, error_code=None):
    """
    Create standardized error response
    
    Args:
        error_message (str): Error message
        error_code (str, optional): Error code
        
    Returns:
        dict: Standardized error response
    """
    response = {
        'success': False,
        'error': error_message,
        'timestamp': datetime.now().isoformat()
    }
    
    if error_code:
        response['error_code'] = error_code
    
    return response