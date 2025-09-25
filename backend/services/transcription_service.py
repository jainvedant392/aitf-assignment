"""
Transcription Service for Agriculture Helper API
Handles audio-to-text conversion using Deepgram API
"""

import requests
import json
from datetime import datetime
from config import Config
import logging

logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self):
        """Initialize Deepgram transcription service"""
        self.api_key = Config.DEEPGRAM_API_KEY
        self.api_url = "https://api.deepgram.com/v1/listen"
        self.supported_formats = ['audio/webm', 'audio/wav', 'audio/mp3', 'audio/m4a', 'audio/ogg']
        
        if not self.api_key:
            logger.warning("⚠️ DEEPGRAM_API_KEY not found - transcription will not work")
        else:
            logger.info("✅ Transcription Service initialized with Deepgram")
    
    def transcribe_audio(self, audio_data, content_type='audio/webm', language='ja', options=None):
        """
        Transcribe audio data using Deepgram API
        
        Args:
            audio_data (bytes): Raw audio data
            content_type (str): MIME type of audio data
            language (str): Language code (ja, en, etc.)
            options (dict, optional): Additional Deepgram options
            
        Returns:
            dict: Transcription result with success status and transcript
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'Deepgram API key not configured',
                'error_code': 'NO_API_KEY'
            }
        
        if not audio_data:
            return {
                'success': False,
                'error': 'No audio data provided',
                'error_code': 'EMPTY_AUDIO'
            }
        
        if content_type not in self.supported_formats:
            logger.warning(f"Unsupported format: {content_type}, proceeding anyway")
        
        try:
            # Prepare headers
            headers = {
                'Authorization': f'Token {self.api_key}',
                'Content-Type': content_type
            }
            
            # Prepare query parameters with defaults optimized for agricultural context
            params = {
                'model': 'nova-2',  # Good balance of accuracy and cost
                'language': language,
                'smart_format': 'true',
                'punctuate': 'true',
                'diarize': 'false',  # Single speaker for agricultural queries
                'utterances': 'true',  # Get confidence scores
                'detect_language': 'false',  # We specify language
                'filler_words': 'false',  # Clean transcription
                'multichannel': 'false'  # Mono audio expected
            }
            
            # Add custom options if provided
            if options:
                params.update(options)
            
            logger.info(f"🎙️ Transcribing {len(audio_data)} bytes of {content_type} audio in {language}")
            
            # Make API request to Deepgram
            response = requests.post(
                self.api_url,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=30  # 30 second timeout for longer audio files
            )
            
            # Handle HTTP errors
            if response.status_code != 200:
                error_detail = self._parse_deepgram_error(response)
                logger.error(f"❌ Deepgram API error {response.status_code}: {error_detail}")
                return {
                    'success': False,
                    'error': f'Deepgram API error: {error_detail}',
                    'error_code': f'HTTP_{response.status_code}',
                    'status_code': response.status_code
                }
            
            # Parse successful response
            result = response.json()
            
            # Debug: Log the response structure
            logger.info(f"🔍 Deepgram response type: {type(result)}")
            logger.info(f"🔍 Deepgram response keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
            
            transcript_data = self._extract_transcript(result)
            
            if transcript_data['transcript']:
                logger.info(f"✅ Transcription successful: '{transcript_data['transcript'][:50]}...'")
                return {
                    'success': True,
                    'transcript': transcript_data['transcript'],
                    'confidence': transcript_data['confidence'],
                    'language_detected': language,
                    'processing_time': transcript_data.get('processing_time', 0),
                    'word_count': len(transcript_data['transcript'].split()),
                    'alternatives': transcript_data.get('alternatives', []),
                    'metadata': {
                        'model': params['model'],
                        'audio_duration': result.get('metadata', {}).get('duration', 0),
                        'channels': result.get('metadata', {}).get('channels', 1)
                    },
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.warning("⚠️ No transcript generated from audio")
                return {
                    'success': False,
                    'error': 'No speech detected in audio',
                    'error_code': 'NO_SPEECH',
                    'confidence': 0.0
                }
                
        except requests.exceptions.Timeout:
            logger.error("❌ Transcription timeout")
            return {
                'success': False,
                'error': 'Transcription request timed out',
                'error_code': 'TIMEOUT'
            }
            
        except requests.exceptions.ConnectionError:
            logger.error("❌ Connection error to Deepgram")
            return {
                'success': False,
                'error': 'Unable to connect to transcription service',
                'error_code': 'CONNECTION_ERROR'
            }
            
        except json.JSONDecodeError:
            logger.error("❌ Invalid JSON response from Deepgram")
            return {
                'success': False,
                'error': 'Invalid response from transcription service',
                'error_code': 'INVALID_RESPONSE'
            }
            
        except Exception as e:
            logger.error(f"❌ Unexpected transcription error: {str(e)}")
            return {
                'success': False,
                'error': f'Transcription service error: {str(e)}',
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def _extract_transcript(self, deepgram_response):
        """
        Extract transcript and metadata from Deepgram response
        
        Args:
            deepgram_response: Raw response from Deepgram API (should be dict)
            
        Returns:
            dict: Extracted transcript data
        """
        try:
            # Check if response is actually a dictionary
            if not isinstance(deepgram_response, dict):
                logger.error(f"❌ Expected dict, got {type(deepgram_response)}: {deepgram_response}")
                return {'transcript': '', 'confidence': 0.0}
            
            # Check for error in response
            if 'error' in deepgram_response:
                logger.error(f"❌ Deepgram API error in response: {deepgram_response['error']}")
                return {'transcript': '', 'confidence': 0.0}
            
            results = deepgram_response.get('results')
            if not results:
                logger.warning("⚠️ No 'results' in Deepgram response")
                return {'transcript': '', 'confidence': 0.0}
            
            # Check if results is actually a dict
            if not isinstance(results, dict):
                logger.error(f"❌ Expected 'results' to be dict, got {type(results)}: {results}")
                return {'transcript': '', 'confidence': 0.0}
            
            channels = results.get('channels', [])
            if not channels:
                logger.warning("⚠️ No 'channels' in results")
                logger.info(f"🔍 Available results keys: {list(results.keys()) if isinstance(results, dict) else 'N/A'}")
                return {'transcript': '', 'confidence': 0.0}
            
            # Get first channel (mono audio)
            channel = channels[0]
            logger.info(f"🔍 Channel type: {type(channel)}")
            logger.info(f"🔍 Channel content: {channel}")
            
            if not isinstance(channel, dict):
                logger.error(f"❌ Expected channel to be dict, got {type(channel)}: {channel}")
                return {'transcript': '', 'confidence': 0.0}
            
            alternatives = channel.get('alternatives', [])
            logger.info(f"🔍 Alternatives count: {len(alternatives)}")
            
            if not alternatives:
                logger.warning("⚠️ No 'alternatives' in channel")
                logger.info(f"🔍 Available channel keys: {list(channel.keys())}")
                return {'transcript': '', 'confidence': 0.0}
            
            # Get best alternative (highest confidence)
            best_alternative = alternatives[0]
            transcript = best_alternative.get('transcript', '').strip()
            confidence = best_alternative.get('confidence', 0.0)
            
            logger.info(f"📝 Extracted transcript: '{transcript}' (confidence: {confidence})")
            
            # Extract additional alternatives for fallback
            alternative_transcripts = []
            for alt in alternatives[1:3]:  # Get up to 2 additional alternatives
                if alt.get('transcript') and alt.get('confidence', 0) > 0.5:
                    alternative_transcripts.append({
                        'transcript': alt['transcript'].strip(),
                        'confidence': alt['confidence']
                    })
            
            # Get processing metadata
            metadata = deepgram_response.get('metadata', {})
            processing_time = 0
            if isinstance(metadata, dict):
                processing_time = metadata.get('duration', 0)
            
            return {
                'transcript': transcript,
                'confidence': confidence,
                'alternatives': alternative_transcripts,
                'processing_time': processing_time,
                'word_count': len(transcript.split()) if transcript else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting transcript: {str(e)}")
            logger.error(f"❌ Response type: {type(deepgram_response)}")
            logger.error(f"❌ Response content: {deepgram_response}")
            return {'transcript': '', 'confidence': 0.0}
    
    def _parse_deepgram_error(self, response):
        """
        Parse error details from Deepgram API response
        
        Args:
            response: HTTP response object
            
        Returns:
            str: Human-readable error message
        """
        try:
            error_data = response.json()
            return error_data.get('err_msg', f'HTTP {response.status_code}')
        except:
            # Common HTTP status code meanings for Deepgram
            status_messages = {
                400: 'Invalid audio format or parameters',
                401: 'Invalid or missing API key',
                402: 'Insufficient credits or payment required',
                403: 'Access forbidden - check API key permissions',
                413: 'Audio file too large',
                429: 'Rate limit exceeded',
                500: 'Deepgram service error'
            }
            return status_messages.get(response.status_code, f'HTTP {response.status_code}')
    
    def validate_audio_format(self, content_type, file_size=None):
        """
        Validate audio format and size
        
        Args:
            content_type (str): MIME type of audio
            file_size (int, optional): Size in bytes
            
        Returns:
            dict: Validation result
        """
        validation_result = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check content type
        if content_type not in self.supported_formats:
            validation_result['warnings'].append(f'Format {content_type} may not be optimal. Supported: {", ".join(self.supported_formats)}')
        
        # Check file size (Deepgram limit is typically 500MB)
        if file_size:
            max_size = 500 * 1024 * 1024  # 500MB
            if file_size > max_size:
                validation_result['valid'] = False
                validation_result['errors'].append(f'File too large: {file_size / 1024 / 1024:.1f}MB (max: 500MB)')
            elif file_size < 1024:  # Less than 1KB
                validation_result['warnings'].append('Very small audio file - may not contain speech')
        
        return validation_result
    
    def get_supported_languages(self):
        """
        Get list of supported languages for transcription
        
        Returns:
            dict: Supported languages with codes and names
        """
        return {
            'success': True,
            'languages': {
                'ja': 'Japanese',
                'en': 'English',
                'zh': 'Chinese (Mandarin)',
                'ko': 'Korean',
                'hi': 'Hindi',
                'es': 'Spanish',
                'fr': 'French',
                'de': 'German',
                'pt': 'Portuguese',
                'ru': 'Russian',
                'it': 'Italian',
                'th': 'Thai',
                'vi': 'Vietnamese'
            },
            'default': 'ja',
            'agricultural_optimized': ['ja', 'en', 'hi', 'zh'],  # Languages with good agricultural vocabulary
            'note': 'Language detection available but manual specification recommended for best results'
        }
    
    def get_service_status(self):
        """
        Check service status and configuration
        
        Returns:
            dict: Service status information
        """
        status = {
            'service': 'TranscriptionService',
            'provider': 'Deepgram',
            'configured': bool(self.api_key),
            'timestamp': datetime.now().isoformat()
        }
        
        if self.api_key:
            status.update({
                'status': 'ready',
                'api_endpoint': self.api_url,
                'supported_formats': self.supported_formats,
                'default_model': 'nova-2',
                'max_file_size': '500MB',
                'timeout': '30 seconds'
            })
        else:
            status.update({
                'status': 'not_configured',
                'error': 'DEEPGRAM_API_KEY environment variable not set'
            })
        
        return status