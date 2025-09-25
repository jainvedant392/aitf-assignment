"""
Intelligent Chat API routes with comprehensive agricultural knowledge
"""

from flask import Blueprint, request, jsonify, session
from services.ai_service import AIService
from services.weather_service import WeatherService
from services.location_service import LocationService
from services.query_intelligence_service import QueryIntelligenceService
from services.transcription_service import TranscriptionService
from datetime import datetime
import uuid

# Create blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Initialize services
ai_service = AIService()
weather_service = WeatherService()
location_service = LocationService()
query_intelligence = QueryIntelligenceService()
transcription_service = TranscriptionService()


# In-memory session storage (use Redis in production)
user_sessions = {}

def get_or_create_session(session_id=None):
    """Get or create user session for context tracking"""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            'session_id': session_id,
            'current_location': {'city': 'Tokyo', 'country': 'JP'},
            'location_history': [],
            'query_history': [],
            'context_type': 'general',  # general, location_specific, weather_dependent
            'message_count': 0,
            'created_at': datetime.now().isoformat()
        }
    
    return user_sessions[session_id]

@chat_bp.route('/', methods=['POST'])
def intelligent_chat():
    """
    Intelligent chat endpoint with comprehensive agricultural knowledge
    """
    try:
        data = request.get_json()
        print(f"🧠 Intelligent chat request: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'Request body is required'}), 400
        
        user_input = data.get('message', '').strip()
        if not user_input:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        session_id = data.get('session_id')
        language = data.get('language', 'japanese')
        
        # Get or create user session
        user_session = get_or_create_session(session_id)
        user_session['message_count'] += 1
        
        print(f"👤 Session: {user_session['session_id'][:8]}... (message #{user_session['message_count']})")
        
        # STEP 1: Classify the query using AI intelligence
        query_classification = query_intelligence.classify_query(user_input)
        print(f"🎯 Query classified: {query_classification}")
        
        # Store query in history
        user_session['query_history'].append({
            'query': user_input,
            'classification': query_classification,
            'timestamp': datetime.now().isoformat()
        })
        
        # STEP 2: Extract location if needed
        location_data = None
        location_changed = False
        
        if query_classification.get('needs_location', False):
            # Try to extract location from current message
            location_extracted = location_service.extract_location_from_message(user_input)
            
            if location_extracted['has_location'] and location_extracted['confidence'] > 0.6:
                new_location = {
                    'city': location_extracted['city'],
                    'country': location_extracted['country']
                }
                
                # Check if location changed
                if (new_location['city'] != user_session['current_location']['city'] or 
                    new_location['country'] != user_session['current_location']['country']):
                    
                    user_session['location_history'].append({
                        'location': user_session['current_location'].copy(),
                        'timestamp': datetime.now().isoformat()
                    })
                    user_session['current_location'] = new_location
                    location_changed = True
                    
                    print(f"📍 Location changed to: {new_location}")
            
            location_data = user_session['current_location']
        
        # STEP 3: Get weather data if needed
        weather_data = None
        if query_classification.get('needs_weather', False) and location_data:
            try:
                weather_data = weather_service.get_current_weather(
                    location_data['city'], 
                    location_data['country']
                )
                
                if weather_data and weather_data.get('success'):
                    # Add agricultural analysis for weather-dependent queries
                    enhanced_weather = weather_service.analyze_weather_for_agriculture(weather_data)
                    if enhanced_weather:
                        weather_data = enhanced_weather
                
                print(f"🌤️ Weather data: {weather_data.get('success', False) if weather_data else False}")
                    
            except Exception as e:
                print(f"⚠️ Weather fetch failed: {e}")
                weather_data = None
        
        # STEP 4: Generate intelligent AI response based on classification
        try:
            ai_response = ai_service.generate_intelligent_response(
                user_input,
                query_classification,
                location_data,
                weather_data,
                language
            )
            
            print(f"🤖 AI response: {ai_response.get('success', False)}")
            
            # Update session context
            user_session['context_type'] = query_classification['query_type']
            
        except Exception as e:
            print(f"❌ AI response error: {e}")
            ai_response = {
                'success': False,
                'advice': 'AI response generation failed',
                'error': str(e)
            }
        
        # STEP 5: Get crop recommendations for relevant queries
        crop_recommendations = None
        if (weather_data and weather_data.get('success') and 
            query_classification['query_type'] in ['weather_dependent', 'seasonal_planning']):
            try:
                crop_recommendations = ai_service.get_crop_recommendations(weather_data)
                print(f"🌾 Crop recommendations: {crop_recommendations.get('success', False) if crop_recommendations else False}")
            except Exception as e:
                print(f"⚠️ Crop recommendations failed: {e}")
        
        # STEP 6: Prepare comprehensive response
        response_data = {
            'success': True,
            'response': ai_response.get('advice', 'No response generated'),
            'session_id': user_session['session_id'],
            'query_intelligence': {
                'classification': query_classification,
                'context_type': user_session['context_type'],
                'reasoning': query_classification.get('reasoning', '')
            },
            'location_info': {
                'current_location': location_data,
                'location_changed': location_changed,
                'location_needed': query_classification.get('needs_location', False)
            } if location_data else None,
            'weather': weather_data if query_classification.get('needs_weather', False) else None,
            'crop_recommendations': crop_recommendations,
            'model_used': ai_response.get('model_used', 'unknown'),
            'message_count': user_session['message_count'],
            'capabilities_used': {
                'query_classification': True,
                'location_extraction': query_classification.get('needs_location', False),
                'weather_analysis': query_classification.get('needs_weather', False),
                'agricultural_knowledge': True
            },
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ Comprehensive response prepared")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"💥 Intelligent chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Intelligent chat error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@chat_bp.route('/analyze', methods=['POST'])
def analyze_query():
    """Standalone endpoint to analyze query capabilities"""
    try:
        data = request.get_json()
        message = data.get('message', '') if data else ''
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Classify the query
        classification = query_intelligence.classify_query(message)
        
        # Extract location if mentioned
        location_data = location_service.extract_location_from_message(message)
        
        return jsonify({
            'success': True,
            'query': message,
            'classification': classification,
            'location_extraction': location_data,
            'capabilities_needed': {
                'weather_data': classification.get('needs_weather', False),
                'location_context': classification.get('needs_location', False),
                'general_knowledge': classification['query_type'] == 'general_knowledge',
                'technical_expertise': classification['query_type'] == 'technical_advice',
                'seasonal_planning': classification['query_type'] == 'seasonal_planning'
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Query analysis error: {str(e)}'
        }), 500

@chat_bp.route('/session/<session_id>/context', methods=['GET'])
def get_session_context(session_id):
    """Get detailed session context and history"""
    try:
        if session_id in user_sessions:
            session_data = user_sessions[session_id].copy()
            
            # Add summary statistics
            query_types = [q['classification']['query_type'] for q in session_data['query_history']]
            session_data['statistics'] = {
                'total_queries': len(query_types),
                'query_type_distribution': {
                    'general_knowledge': query_types.count('general_knowledge'),
                    'technical_advice': query_types.count('technical_advice'),
                    'weather_dependent': query_types.count('weather_dependent'),
                    'seasonal_planning': query_types.count('seasonal_planning')
                },
                'location_changes': len(session_data['location_history'])
            }
            
            return jsonify({
                'success': True,
                'session_context': session_data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Context retrieval error: {str(e)}'
        }), 500

@chat_bp.route('/capabilities', methods=['GET'])
def get_capabilities():
    """Return system capabilities and sample queries"""
    return jsonify({
        'success': True,
        'system_capabilities': {
            'query_types': {
                'general_knowledge': {
                    'description': 'Comprehensive agricultural knowledge and facts',
                    'examples': [
                        'What crops are grown in India during winter?',
                        'Types of rice varieties in Asia',
                        'Organic farming principles'
                    ]
                },
                'technical_advice': {
                    'description': 'Specific problem-solving and technical solutions',
                    'examples': [
                        'How to control aphids in tomatoes?',
                        'Best fertilizer for wheat crop?',
                        'Soil pH correction methods'
                    ]
                },
                'weather_dependent': {
                    'description': 'Immediate advice based on current weather',
                    'examples': [
                        'Should I water my crops today?',
                        'Is it good weather for harvesting?',
                        'Pest risk assessment for today'
                    ]
                },
                'seasonal_planning': {
                    'description': 'Long-term planning and timing advice',
                    'examples': [
                        'When to plant wheat in Punjab?',
                        'Crop rotation schedule for next year',
                        'Monsoon preparation strategies'
                    ]
                }
            },
            'features': {
                'intelligent_query_classification': True,
                'automatic_location_extraction': True,
                'weather_integration': True,
                'multilingual_support': ['Japanese', 'English'],
                'session_context_tracking': True,
                'comprehensive_agricultural_knowledge': True
            }
        },
        'usage_tips': [
            'Ask specific questions like "How to grow tomatoes in Mumbai?"',
            'Use general queries like "What is crop rotation?"',
            'Request immediate advice: "Should I irrigate today?"',
            'Plan ahead: "When to plant rice in Thailand?"'
        ],
        'timestamp': datetime.now().isoformat()
    })

@chat_bp.route('/voice/process', methods=['POST'])
def process_voice_input():
    """
    Process voice input through Deepgram transcription and intelligent chat
    
    Expects:
        - Multipart form data with 'audio' file
        - Optional: session_id, language
        
    Returns:
        JSON: Transcription result + intelligent agricultural advice
    """
    try:
        print("🎤 Voice processing request received")
        
        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided',
                'error_code': 'NO_AUDIO_FILE'
            }), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty audio file',
                'error_code': 'EMPTY_FILE'
            }), 400
        
        # Get optional parameters
        session_id = request.form.get('session_id')
        language = request.form.get('language', 'ja')  # Default to Japanese
        
        # Read audio data
        audio_data = audio_file.read()
        content_type = audio_file.content_type or 'audio/webm'
        
        print(f"🎵 Processing {len(audio_data)} bytes of {content_type} audio")
        
        # Validate audio format and size
        validation = transcription_service.validate_audio_format(content_type, len(audio_data))
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': f"Invalid audio: {', '.join(validation['errors'])}",
                'error_code': 'INVALID_AUDIO',
                'validation': validation
            }), 400
        
        # STEP 1: Transcribe audio using Deepgram
        print("🔍 Starting Deepgram transcription...")
        transcription_result = transcription_service.transcribe_audio(
            audio_data=audio_data,
            content_type=content_type,
            language=language,
            options={
                'model': 'nova-2',
                'smart_format': 'true',
                'punctuate': 'true'
            }
        )
        
        if not transcription_result['success']:
            print(f"❌ Transcription failed: {transcription_result['error']}")
            return jsonify({
                'success': False,
                'error': f"Transcription failed: {transcription_result['error']}",
                'error_code': transcription_result.get('error_code', 'TRANSCRIPTION_ERROR'),
                'transcription_details': transcription_result
            }), 500
        
        transcript = transcription_result['transcript']
        confidence = transcription_result['confidence']
        
        print(f"✅ Transcription successful: '{transcript}' (confidence: {confidence:.2f})")
        
        # Low confidence warning
        if confidence < 0.6:
            print(f"⚠️ Low confidence transcription: {confidence:.2f}")
        
        # STEP 2: Process transcribed text through intelligent chat
        print("🧠 Processing transcribed text through intelligent chat...")
        
        # Prepare chat request data
        chat_data = {
            'message': transcript,
            'session_id': session_id,
            'language': 'japanese' if language == 'ja' else 'english'
        }
        
        # Get or create session
        user_session = get_or_create_session(session_id)
        user_session['message_count'] += 1
        
        # Add voice input context to session
        user_session['last_voice_input'] = {
            'transcript': transcript,
            'confidence': confidence,
            'audio_duration': transcription_result.get('metadata', {}).get('audio_duration', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"👤 Voice session: {user_session['session_id'][:8]}... (message #{user_session['message_count']})")
        
        # STEP 3: Use existing intelligent chat logic
        try:
            # Classify the query using AI intelligence
            query_classification = query_intelligence.classify_query(transcript)
            print(f"🎯 Voice query classified: {query_classification}")
            
            # Store query in history
            user_session['query_history'].append({
                'query': transcript,
                'classification': query_classification,
                'input_type': 'voice',
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            })
            
            # Extract location if needed
            location_data = None
            location_changed = False
            
            if query_classification.get('needs_location', False):
                location_extracted = location_service.extract_location_from_message(transcript)
                
                if location_extracted['has_location'] and location_extracted['confidence'] > 0.6:
                    new_location = {
                        'city': location_extracted['city'],
                        'country': location_extracted['country']
                    }
                    
                    # Check if location changed
                    if (new_location['city'] != user_session['current_location']['city'] or 
                        new_location['country'] != user_session['current_location']['country']):
                        
                        user_session['location_history'].append({
                            'location': user_session['current_location'].copy(),
                            'timestamp': datetime.now().isoformat()
                        })
                        user_session['current_location'] = new_location
                        location_changed = True
                        
                        print(f"📍 Voice location changed to: {new_location}")
                
                location_data = user_session['current_location']
            
            # Get weather data if needed
            weather_data = None
            if query_classification.get('needs_weather', False) and location_data:
                try:
                    weather_data = weather_service.get_current_weather(
                        location_data['city'], 
                        location_data['country']
                    )
                    
                    if weather_data and weather_data.get('success'):
                        enhanced_weather = weather_service.analyze_weather_for_agriculture(weather_data)
                        if enhanced_weather:
                            weather_data = enhanced_weather
                    
                    print(f"🌤️ Voice weather data: {weather_data.get('success', False) if weather_data else False}")
                        
                except Exception as e:
                    print(f"⚠️ Voice weather fetch failed: {e}")
                    weather_data = None
            
            # Generate intelligent AI response
            ai_response = ai_service.generate_intelligent_response(
                transcript,
                query_classification,
                location_data,
                weather_data,
                'japanese' if language == 'ja' else 'english'
            )
            
            print(f"🤖 Voice AI response: {ai_response.get('success', False)}")
            
            # Get crop recommendations for relevant queries
            crop_recommendations = None
            if (weather_data and weather_data.get('success') and 
                query_classification['query_type'] in ['weather_dependent', 'seasonal_planning']):
                try:
                    crop_recommendations = ai_service.get_crop_recommendations(weather_data)
                    print(f"🌾 Voice crop recommendations: {crop_recommendations.get('success', False) if crop_recommendations else False}")
                except Exception as e:
                    print(f"⚠️ Voice crop recommendations failed: {e}")
            
            # Update session context
            user_session['context_type'] = query_classification['query_type']
            
        except Exception as e:
            print(f"❌ Voice chat processing error: {e}")
            import traceback
            traceback.print_exc()
            
            ai_response = {
                'success': False,
                'advice': 'Voice chat processing failed',
                'error': str(e)
            }
        
        # STEP 4: Prepare comprehensive voice response
        response_data = {
            'success': True,
            'transcription': {
                'transcript': transcript,
                'confidence': confidence,
                'language_detected': language,
                'processing_time': transcription_result.get('processing_time', 0),
                'word_count': transcription_result.get('word_count', 0),
                'alternatives': transcription_result.get('alternatives', [])
            },
            'chat_response': {
                'response': ai_response.get('advice', 'No response generated'),
                'model_used': ai_response.get('model_used', 'unknown'),
                'success': ai_response.get('success', False)
            },
            'session_id': user_session['session_id'],
            'query_intelligence': {
                'classification': query_classification,
                'context_type': user_session['context_type'],
                'reasoning': query_classification.get('reasoning', '')
            },
            'location_info': {
                'current_location': location_data,
                'location_changed': location_changed,
                'location_needed': query_classification.get('needs_location', False)
            } if location_data else None,
            'weather': weather_data if query_classification.get('needs_weather', False) else None,
            'crop_recommendations': crop_recommendations,
            'voice_metadata': {
                'audio_size_bytes': len(audio_data),
                'audio_format': content_type,
                'processing_chain': ['deepgram_transcription', 'query_classification', 'ai_response'],
                'total_processing_time': transcription_result.get('processing_time', 0)
            },
            'message_count': user_session['message_count'],
            'capabilities_used': {
                'voice_transcription': True,
                'query_classification': True,
                'location_extraction': query_classification.get('needs_location', False),
                'weather_analysis': query_classification.get('needs_weather', False),
                'agricultural_knowledge': True
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Add warnings for low confidence
        if confidence < 0.6:
            response_data['warnings'] = [
                f'Low transcription confidence ({confidence:.2f}). Please speak clearly or try again.'
            ]
        
        if validation.get('warnings'):
            response_data.setdefault('warnings', []).extend(validation['warnings'])
        
        print(f"✅ Voice processing completed successfully")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"💥 Voice processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Voice processing failed: {str(e)}',
            'error_code': 'VOICE_PROCESSING_ERROR',
            'timestamp': datetime.now().isoformat()
        }), 500

@chat_bp.route('/voice/status', methods=['GET'])
def get_voice_status():
    """Get voice processing capabilities and status"""
    try:
        transcription_status = transcription_service.get_service_status()
        supported_languages = transcription_service.get_supported_languages()
        
        return jsonify({
            'success': True,
            'voice_capabilities': {
                'transcription_service': transcription_status,
                'supported_languages': supported_languages,
                'supported_formats': transcription_service.supported_formats,
                'max_file_size': '500MB',
                'recommended_format': 'audio/webm',
                'processing_timeout': '30 seconds'
            },
            'integration_features': {
                'automatic_chat_processing': True,
                'session_management': True,
                'query_classification': True,
                'location_extraction': True,
                'weather_integration': True,
                'agricultural_knowledge': True,
                'multilingual_support': True
            },
            'usage_examples': [
                'Record: "今日の天気はどうですか？" (How is today\'s weather?)',
                'Record: "東京でトマトを育てるアドバイスください" (Please give advice on growing tomatoes in Tokyo)',
                'Record: "今植えるのに最適な作物は何ですか？" (What are the best crops to plant now?)'
            ],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Voice status error: {str(e)}'
        }), 500
    
@chat_bp.route('/debug/deepgram', methods=['POST'])
def debug_deepgram():
    """Debug endpoint to test Deepgram API directly"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file'}), 400
            
        audio_file = request.files['audio']
        audio_data = audio_file.read()
        
        print(f"🎵 Debug: Audio size: {len(audio_data)} bytes")
        print(f"🎵 Debug: Audio type: {audio_file.content_type}")
        
        # Test raw Deepgram API call
        import requests
        import os
        
        deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
        if not deepgram_api_key:
            return jsonify({'error': 'No Deepgram API key'}), 500
            
        url = "https://api.deepgram.com/v1/listen"
        headers = {
            "Authorization": f"Token {deepgram_api_key}",
            "Content-Type": audio_file.content_type or 'audio/webm'
        }
        
        params = {
            "model": "nova-2",
            "language": "ja",
            "smart_format": "true",
            "punctuate": "true"
        }
        
        print(f"🚀 Debug: Calling Deepgram API...")
        response = requests.post(url, headers=headers, params=params, data=audio_data, timeout=30)
        
        print(f"📊 Debug: Status code: {response.status_code}")
        print(f"📊 Debug: Response headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"❌ Debug: Error response: {response.text}")
            return jsonify({
                'success': False,
                'status_code': response.status_code,
                'error': response.text
            })
            
        result = response.json()
        print(f"✅ Debug: Full response: {result}")
        
        # Try to extract transcript manually
        transcript = ""
        confidence = 0.0
        
        try:
            if 'results' in result:
                results = result['results']
                print(f"🔍 Debug: Results type: {type(results)}")
                print(f"🔍 Debug: Results content: {results}")
                
                if isinstance(results, dict) and 'channels' in results:
                    channels = results['channels']
                    print(f"🔍 Debug: Channels: {channels}")
                    
                    if channels and len(channels) > 0:
                        channel = channels[0]
                        print(f"🔍 Debug: First channel: {channel}")
                        
                        if isinstance(channel, dict) and 'alternatives' in channel:
                            alternatives = channel['alternatives']
                            print(f"🔍 Debug: Alternatives: {alternatives}")
                            
                            if alternatives and len(alternatives) > 0:
                                best_alt = alternatives[0]
                                transcript = best_alt.get('transcript', '')
                                confidence = best_alt.get('confidence', 0.0)
                                print(f"✅ Debug: Extracted transcript: '{transcript}' (confidence: {confidence})")
        
        except Exception as extract_error:
            print(f"❌ Debug: Extract error: {extract_error}")
            
        return jsonify({
            'success': True,
            'raw_response': result,
            'extracted_transcript': transcript,
            'extracted_confidence': confidence,
            'debug_info': {
                'audio_size': len(audio_data),
                'content_type': audio_file.content_type,
                'status_code': response.status_code
            }
        })
        
    except Exception as e:
        print(f"💥 Debug: Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500