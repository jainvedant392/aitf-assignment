"""
Agriculture Helper API - Main Application
Flask application with organized routes using blueprints
"""

from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import os

# Import configuration
from config import Config

# Import blueprints
from routes import blueprints

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    
    # Health check endpoint
    @app.route('/', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'Agriculture Helper API',
            'version': '1.0.0',
            'endpoints': {
                'weather': '/api/weather/current',
                'forecast': '/api/weather/forecast',
                'chat': '/api/chat/',
                'crops': '/api/agriculture/crops/recommendations',
                'seasonal': '/api/agriculture/seasonal/advice'
            },
            'timestamp': datetime.now().isoformat()
        })
    
    # API documentation endpoint
    @app.route('/api', methods=['GET'])
    def api_documentation():
        """API documentation endpoint"""
        return jsonify({
            'name': 'Agriculture Helper API',
            'description': 'AI-powered agricultural assistant with weather integration',
            'version': '1.0.0',
            'features': [
                'Real-time weather data with agricultural analysis',
                'AI-powered farming advice in Japanese and English',
                'Crop recommendations based on weather conditions',
                'Seasonal agricultural guidance',
                'Pest risk assessment',
                'Irrigation recommendations',
                'Soil analysis and improvement suggestions'
            ],
            'endpoints': {
                'weather': {
                    'current': 'GET /api/weather/current',
                    'forecast': 'GET /api/weather/forecast',
                    'historical': 'GET /api/weather/historical',
                    'search_locations': 'GET /api/weather/locations/search'
                },
                'chat': {
                    'main_chat': 'POST /api/chat/',
                    'translate': 'POST /api/chat/translate',
                    'conversation': 'POST /api/chat/conversation',
                    'voice_processing': 'POST /api/chat/voice/process'
                },
                'agriculture': {
                    'crop_recommendations': 'GET /api/agriculture/crops/recommendations',
                    'crop_analysis': 'POST /api/agriculture/crops/analysis',
                    'seasonal_advice': 'GET /api/agriculture/seasonal/advice',
                    'pest_assessment': 'GET /api/agriculture/pest/risk-assessment',
                    'irrigation': 'GET /api/agriculture/irrigation/recommendations',
                    'planting_calendar': 'GET /api/agriculture/planting/calendar',
                    'soil_analysis': 'POST /api/agriculture/soil/analysis'
                }
            },
            'powered_by': {
                'weather_api': 'OpenMeteo (free)',
                'ai_model': 'Google Gemini 2.5 Flash',
                'framework': 'Flask',
                'language_support': ['Japanese', 'English']
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'message': 'The requested endpoint does not exist',
            'available_endpoints': '/api',
            'timestamp': datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors"""
        return jsonify({
            'success': False,
            'error': 'Method not allowed',
            'message': 'The requested method is not allowed for this endpoint',
            'timestamp': datetime.now().isoformat()
        }), 405
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 errors"""
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again.',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    # Request logging middleware
    @app.before_request
    def log_request_info():
        """Log request information"""
        from flask import request
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"Request: {request.method} {request.url}")
    
    # Response headers middleware
    @app.after_request
    def after_request(response):
        """Add security headers and CORS"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    return app

# Create the application
app = create_app()

# CLI command to test the application
@app.cli.command()
def test():
    """Run basic application tests"""
    import requests
    
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Agriculture Helper API")
    print("=" * 50)
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Health check: PASS")
        else:
            print(f"❌ Health check: FAIL ({response.status_code})")
    except Exception as e:
        print(f"❌ Health check: FAIL ({str(e)})")
    
    # Test weather API
    try:
        response = requests.get(f"{base_url}/api/weather/current?city=Tokyo")
        if response.status_code == 200:
            print("✅ Weather API: PASS")
        else:
            print(f"❌ Weather API: FAIL ({response.status_code})")
    except Exception as e:
        print(f"❌ Weather API: FAIL ({str(e)})")
    
    print("\n🎯 Tests completed!")
    print("Run 'python app.py' to start the server")

if __name__ == '__main__':
    # Configuration for development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print("🌾 Starting Agriculture Helper API Server")
    print("=" * 50)
    print(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")
    print(f"Debug mode: {debug_mode}")
    print("Server: http://localhost:5000")
    print("API docs: http://localhost:5000/api")
    print("Health check: http://localhost:5000/")
    print("=" * 50)
    
    # Run the application
    app.run(
        debug=debug_mode,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )