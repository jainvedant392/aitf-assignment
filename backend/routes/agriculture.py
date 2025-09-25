"""
Agriculture API routes for Agriculture Helper
Handles crop recommendations, seasonal advice, and agricultural analysis
"""

from flask import Blueprint, request, jsonify
from services.ai_service import AIService
from services.weather_service import WeatherService
from services.agriculture_service import AgricultureService
from utils.helpers import validate_location, handle_api_error
from datetime import datetime

# Create blueprint
agriculture_bp = Blueprint('agriculture', __name__, url_prefix='/api/agriculture')

# Initialize services
ai_service = AIService()
weather_service = WeatherService()
agriculture_service = AgricultureService()

@agriculture_bp.route('/crops/recommendations', methods=['GET'])
def get_crop_recommendations():
    """
    Get crop recommendations based on current weather conditions
    
    Query Parameters:
        city (str): City name (default: Tokyo)
        country (str): Country code (default: JP)
        season (str): Season context (spring/summer/autumn/winter)
        
    Returns:
        JSON: List of recommended crops with suitability scores
    """
    try:
        city = request.args.get('city', 'Tokyo')
        country = request.args.get('country', 'JP')
        season = request.args.get('season', 'current')
        
        # Validate location
        city, country = validate_location(city, country)
        
        # Get current weather
        weather_data = weather_service.get_current_weather(city, country)
        
        if not weather_data.get('success'):
            return jsonify(weather_data), 400
        
        # Get recommendations
        recommendations = ai_service.get_crop_recommendations(weather_data, season)
        
        # Enhanced recommendations with agricultural service
        enhanced_recommendations = agriculture_service.enhance_crop_recommendations(
            recommendations, weather_data
        )
        
        return jsonify(enhanced_recommendations)
        
    except Exception as e:
        return handle_api_error(e, 'Failed to get crop recommendations')

@agriculture_bp.route('/crops/analysis', methods=['POST'])
def get_detailed_crop_analysis():
    """
    Get detailed AI-powered crop analysis for specific crop type
    
    Request Body:
        crop_type (str): Type of crop to analyze
        city (str, optional): City name for weather context
        country (str, optional): Country code for weather context
        growth_stage (str, optional): Current growth stage
        
    Returns:
        JSON: Detailed crop analysis and recommendations
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Request body is required'}), 400
        
        crop_type = data.get('crop_type', '').strip()
        city = data.get('city', 'Tokyo')
        country = data.get('country', 'JP')
        growth_stage = data.get('growth_stage', 'general')
        
        if not crop_type:
            return jsonify({'success': False, 'error': 'crop_type is required'}), 400
        
        # Validate location
        city, country = validate_location(city, country)
        
        # Get current weather
        weather_data = weather_service.get_current_weather(city, country)
        
        if not weather_data.get('success'):
            return jsonify(weather_data), 400
        
        # Get detailed analysis
        analysis = ai_service.get_detailed_crop_analysis(weather_data, crop_type)
        
        # Add agricultural science context
        enhanced_analysis = agriculture_service.add_scientific_context(
            analysis, crop_type, growth_stage
        )
        
        return jsonify(enhanced_analysis)
        
    except Exception as e:
        return handle_api_error(e, 'Failed to get crop analysis')

@agriculture_bp.route('/seasonal/advice', methods=['GET'])
def get_seasonal_advice():
    """
    Get seasonal agricultural advice based on current month and weather
    
    Query Parameters:
        city (str): City name (default: Tokyo)
        country (str): Country code (default: JP)
        month (int, optional): Month number (1-12, default: current month)
        
    Returns:
        JSON: Seasonal advice and recommendations
    """
    try:
        city = request.args.get('city', 'Tokyo')
        country = request.args.get('country', 'JP')
        month = request.args.get('month', None)
        
        if month:
            month = int(month)
            if month < 1 or month > 12:
                return jsonify({'success': False, 'error': 'Month must be between 1 and 12'}), 400
        
        # Validate location
        city, country = validate_location(city, country)
        
        # Get current weather
        weather_data = weather_service.get_current_weather(city, country)
        
        if not weather_data.get('success'):
            return jsonify(weather_data), 400
        
        # Get seasonal advice
        advice = ai_service.get_seasonal_advice(weather_data, month)
        
        # Add practical seasonal tasks
        enhanced_advice = agriculture_service.add_seasonal_tasks(advice, month or datetime.now().month)
        
        return jsonify(enhanced_advice)
        
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Invalid month parameter: {str(e)}'}), 400
    except Exception as e:
        return handle_api_error(e, 'Failed to get seasonal advice')

@agriculture_bp.route('/pest/risk-assessment', methods=['GET'])
def get_pest_risk_assessment():
    """
    Get pest and disease risk assessment based on weather conditions
    
    Query Parameters:
        city (str): City name (default: Tokyo)
        country (str): Country code (default: JP)
        crop_type (str, optional): Specific crop to assess
        
    Returns:
        JSON: Pest risk assessment and prevention advice
    """
    try:
        city = request.args.get('city', 'Tokyo')
        country = request.args.get('country', 'JP')
        crop_type = request.args.get('crop_type', 'general')
        
        # Validate location
        city, country = validate_location(city, country)
        
        # Get current weather
        weather_data = weather_service.get_current_weather(city, country)
        
        if not weather_data.get('success'):
            return jsonify(weather_data), 400
        
        # Get pest risk assessment
        risk_assessment = agriculture_service.assess_pest_risk(weather_data, crop_type)
        
        return jsonify(risk_assessment)
        
    except Exception as e:
        return handle_api_error(e, 'Failed to get pest risk assessment')

@agriculture_bp.route('/irrigation/recommendations', methods=['GET'])
def get_irrigation_recommendations():
    """
    Get irrigation recommendations based on weather and soil conditions
    
    Query Parameters:
        city (str): City name (default: Tokyo)
        country (str): Country code (default: JP)
        crop_type (str, optional): Type of crop
        soil_type (str, optional): Type of soil
        
    Returns:
        JSON: Irrigation recommendations and water management advice
    """
    try:
        city = request.args.get('city', 'Tokyo')
        country = request.args.get('country', 'JP')
        crop_type = request.args.get('crop_type', 'general')
        soil_type = request.args.get('soil_type', 'general')
        
        # Validate location
        city, country = validate_location(city, country)
        
        # Get current weather with agricultural analysis
        weather_data = weather_service.get_current_weather(city, country)
        
        if not weather_data.get('success'):
            return jsonify(weather_data), 400
        
        weather_data = weather_service.analyze_weather_for_agriculture(weather_data)
        
        # Get irrigation recommendations
        irrigation_advice = agriculture_service.get_irrigation_recommendations(
            weather_data, crop_type, soil_type
        )
        
        return jsonify(irrigation_advice)
        
    except Exception as e:
        return handle_api_error(e, 'Failed to get irrigation recommendations')

@agriculture_bp.route('/planting/calendar', methods=['GET'])
def get_planting_calendar():
    """
    Get planting calendar and timing recommendations
    
    Query Parameters:
        city (str): City name (default: Tokyo)
        country (str): Country code (default: JP)
        crop_type (str, optional): Specific crop type
        year (int, optional): Year for calendar (default: current year)
        
    Returns:
        JSON: Planting calendar with optimal timing
    """
    try:
        city = request.args.get('city', 'Tokyo')
        country = request.args.get('country', 'JP')
        crop_type = request.args.get('crop_type', 'all')
        year = request.args.get('year', datetime.now().year)
        
        if year:
            year = int(year)
        
        # Validate location
        city, country = validate_location(city, country)
        
        # Get planting calendar
        calendar_data = agriculture_service.get_planting_calendar(
            city, country, crop_type, year
        )
        
        return jsonify(calendar_data)
        
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Invalid year parameter: {str(e)}'}), 400
    except Exception as e:
        return handle_api_error(e, 'Failed to get planting calendar')

@agriculture_bp.route('/soil/analysis', methods=['POST'])
def analyze_soil_conditions():
    """
    Analyze soil conditions and provide recommendations
    
    Request Body:
        soil_data (dict): Soil test results and observations
        city (str, optional): City name for climate context
        country (str, optional): Country code for climate context
        
    Returns:
        JSON: Soil analysis and improvement recommendations
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Request body is required'}), 400
        
        soil_data = data.get('soil_data', {})
        city = data.get('city', 'Tokyo')
        country = data.get('country', 'JP')
        
        if not soil_data:
            return jsonify({'success': False, 'error': 'soil_data is required'}), 400
        
        # Validate location
        city, country = validate_location(city, country)
        
        # Get weather context
        weather_data = weather_service.get_current_weather(city, country)
        
        # Analyze soil conditions
        soil_analysis = agriculture_service.analyze_soil_conditions(
            soil_data, weather_data
        )
        
        return jsonify(soil_analysis)
        
    except Exception as e:
        return handle_api_error(e, 'Failed to analyze soil conditions')