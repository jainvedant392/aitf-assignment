from google import genai
from google.genai import types
from config import Config
import json
import re

class LocationService:
    def __init__(self):
        """Initialize location extraction service"""
        try:
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
            self.model = "gemini-2.5-flash"
            print("✅ Location Service initialized")
        except Exception as e:
            print(f"❌ Location Service initialization failed: {e}")
            self.client = None
    
    def extract_location_from_message(self, message):
        """
        Extract location (city, country) from user message using AI
        
        Args:
            message (str): User's message
            
        Returns:
            dict: {
                'has_location': bool,
                'city': str or None,
                'country': str or None,
                'confidence': float,
                'extracted_phrase': str or None
            }
        """
        if not self.client:
            return self._fallback_location_extraction(message)
        
        location_prompt = f"""Analyze this user message and extract location information for weather/agricultural queries.

User message: "{message}"

Rules:
1. Look for city names, country names, or location references
2. Focus on locations relevant to weather/farming context
3. Return JSON format only, no additional text
4. If no clear location found, set has_location to false

Required JSON format:
{{
    "has_location": boolean,
    "city": "city name or null",
    "country": "2-letter country code or null", 
    "confidence": float between 0.0 and 1.0,
    "extracted_phrase": "original location phrase from message or null"
}}

Examples:
- "How's farming in Mumbai?" → {{"has_location": true, "city": "Mumbai", "country": "IN", "confidence": 0.9, "extracted_phrase": "Mumbai"}}
- "Tell me about agriculture in London, UK" → {{"has_location": true, "city": "London", "country": "GB", "confidence": 0.95, "extracted_phrase": "London, UK"}}  
- "What crops grow well?" → {{"has_location": false, "city": null, "country": null, "confidence": 0.0, "extracted_phrase": null}}
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=location_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Low temperature for consistent extraction
                    max_output_tokens=200
                )
            )
            
            if response and response.text:
                # Extract JSON from response
                json_text = self._extract_json_from_response(response.text)
                location_data = json.loads(json_text)
                
                # Validate the response structure
                if self._validate_location_response(location_data):
                    print(f"🎯 Location extracted: {location_data}")
                    return location_data
                    
        except Exception as e:
            print(f"❌ AI location extraction failed: {e}")
        
        # Fallback to regex-based extraction
        return self._fallback_location_extraction(message)
    
    def _extract_json_from_response(self, text):
        """Extract JSON from AI response text"""
        # Find JSON block in the response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return text.strip()
    
    def _validate_location_response(self, data):
        """Validate location response structure"""
        required_keys = ['has_location', 'city', 'country', 'confidence', 'extracted_phrase']
        return all(key in data for key in required_keys)
    
    def _fallback_location_extraction(self, message):
        """Simple regex-based location extraction as fallback"""
        print("🔄 Using fallback location extraction")
        
        # Common city patterns
        city_patterns = [
            r'\bin\s+([A-Z][a-zA-Z\s]+?)(?:\s*,|\s*\?|\s*$)',
            r'about\s+([A-Z][a-zA-Z\s]+?)(?:\s*,|\s*\?|\s*$)',
            r'weather\s+in\s+([A-Z][a-zA-Z\s]+?)(?:\s*,|\s*\?|\s*$)',
            r'farming\s+in\s+([A-Z][a-zA-Z\s]+?)(?:\s*,|\s*\?|\s*$)'
        ]
        
        # Known cities mapping
        known_cities = {
            'mumbai': {'city': 'Mumbai', 'country': 'IN'},
            'delhi': {'city': 'Delhi', 'country': 'IN'},
            'london': {'city': 'London', 'country': 'GB'},
            'paris': {'city': 'Paris', 'country': 'FR'},
            'berlin': {'city': 'Berlin', 'country': 'DE'},
            'tokyo': {'city': 'Tokyo', 'country': 'JP'},
            'new york': {'city': 'New York', 'country': 'US'},
            'bangkok': {'city': 'Bangkok', 'country': 'TH'},
            'sydney': {'city': 'Sydney', 'country': 'AU'},
            'cairo': {'city': 'Cairo', 'country': 'EG'}
        }
        
        message_lower = message.lower()
        
        for city_key, city_info in known_cities.items():
            if city_key in message_lower:
                return {
                    'has_location': True,
                    'city': city_info['city'],
                    'country': city_info['country'],
                    'confidence': 0.8,
                    'extracted_phrase': city_key.title()
                }
        
        # Try regex patterns
        for pattern in city_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                location_text = match.group(1).strip()
                if location_text.lower() in known_cities:
                    city_info = known_cities[location_text.lower()]
                    return {
                        'has_location': True,
                        'city': city_info['city'],
                        'country': city_info['country'],
                        'confidence': 0.7,
                        'extracted_phrase': location_text
                    }
        
        return {
            'has_location': False,
            'city': None,
            'country': None,
            'confidence': 0.0,
            'extracted_phrase': None
        }
    
    def get_location_confirmation_message(self, location_data, language='japanese'):
        """Generate confirmation message when location is detected"""
        if not location_data['has_location']:
            return None
            
        city = location_data['city']
        country = location_data['country']
        
        if language.lower() == 'japanese':
            return f"📍 {city}の天気と農業情報を取得しています... / Getting weather and agricultural info for {city}..."
        else:
            return f"📍 Fetching weather and agricultural information for {city}..."