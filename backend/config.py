import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Weather API Configuration (OpenMeteo - Free, no API key required)
    OPENMETEO_BASE_URL = 'https://api.open-meteo.com/v1/forecast'
    
    # Google Gemini Configuration (New GenAI SDK)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    
    # Deepgram Configuration for Voice Transcription
    DEEPGRAM_API_KEY = os.environ.get('DEEPGRAM_API_KEY')
    
    # Agriculture specific settings
    DEFAULT_LOCATION = "Tokyo, Japan"  # Default location for weather
    
    # Temperature thresholds for agriculture (in Celsius)
    CROP_TEMP_THRESHOLDS = {
        'rice': {'min': 20, 'max': 35, 'optimal': 25},
        'wheat': {'min': 5, 'max': 25, 'optimal': 15},
        'corn': {'min': 18, 'max': 35, 'optimal': 25},
        'tomato': {'min': 15, 'max': 30, 'optimal': 22},
        'potato': {'min': 10, 'max': 25, 'optimal': 18}
    }
    
    # Voice Processing Configuration
    VOICE_CONFIG = {
        'max_file_size': 500 * 1024 * 1024,  # 500MB
        'supported_formats': ['audio/webm', 'audio/wav', 'audio/mp3', 'audio/m4a', 'audio/ogg'],
        'default_language': 'ja',
        'transcription_timeout': 30,
        'min_confidence_threshold': 0.3,
        'recommended_sample_rate': 16000,
        'recommended_channels': 1  # Mono
    }