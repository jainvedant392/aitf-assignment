# routes/__init__.py
"""
Routes package for Agriculture Helper API
Contains all API endpoint definitions organized by functionality
"""

from .weather import weather_bp
from .chat import chat_bp
from .agriculture import agriculture_bp

# List of all blueprints to register
blueprints = [
    weather_bp,
    chat_bp,
    agriculture_bp
]

__all__ = ['blueprints', 'weather_bp', 'chat_bp', 'agriculture_bp']