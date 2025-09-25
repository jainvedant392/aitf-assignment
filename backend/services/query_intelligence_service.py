from google import genai
from google.genai import types
from config import Config
import json
import re

class QueryIntelligenceService:
    def __init__(self):
        """Initialize query intelligence service"""
        try:
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
            self.model = "gemini-2.5-flash"
            print("✅ Query Intelligence Service initialized")
        except Exception as e:
            print(f"❌ Query Intelligence Service initialization failed: {e}")
            self.client = None

    def classify_query(self, message):
        """
        Classify the type of agricultural query to determine response strategy
        
        Returns:
        {
            'query_type': 'weather_dependent' | 'general_knowledge' | 'technical_advice' | 'seasonal_planning',
            'needs_weather': bool,
            'needs_location': bool,
            'scope': 'local' | 'regional' | 'global',
            'topics': ['irrigation', 'pests', 'crops', etc.],
            'confidence': float
        }
        """
        if not self.client:
            return self._fallback_classify_query(message)

        classification_prompt = f"""Analyze this agricultural query and classify it to determine the best response strategy.

User query: "{message}"

Classify the query and return ONLY valid JSON in this exact format:
{{
    "query_type": "weather_dependent" | "general_knowledge" | "technical_advice" | "seasonal_planning",
    "needs_weather": boolean,
    "needs_location": boolean,
    "scope": "local" | "regional" | "global",
    "topics": ["topic1", "topic2"],
    "confidence": float_between_0_and_1,
    "reasoning": "brief explanation"
}}

Query Type Definitions:
- "weather_dependent": Requires current weather data (irrigation, daily farm work, immediate pest risks)
- "general_knowledge": Broad agricultural facts, crop information, farming practices
- "technical_advice": Specific problems, diseases, fertilizers, techniques
- "seasonal_planning": Long-term planning, planting schedules, crop rotation

Examples:
- "Should I water my crops today?" → weather_dependent, needs_weather=true, needs_location=true
- "What crops are grown in India during winter?" → general_knowledge, needs_weather=false, needs_location=false
- "How to control aphids in tomatoes?" → technical_advice, needs_weather=false, needs_location=false
- "When to plant wheat in Punjab?" → seasonal_planning, needs_weather=false, needs_location=true
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=classification_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=300
                )
            )
            
            if response and response.text:
                json_text = self._extract_json_from_response(response.text)
                classification = json.loads(json_text)
                
                if self._validate_classification(classification):
                    print(f"🧠 Query classified: {classification['query_type']} (confidence: {classification['confidence']})")
                    return classification
                    
        except Exception as e:
            print(f"❌ Query classification failed: {e}")
        
        return self._fallback_classify_query(message)

    def generate_comprehensive_response(self, message, classification, location_data=None, weather_data=None, language='japanese'):
        """
        Generate intelligent response based on query classification
        """
        if not self.client:
            return self._generate_fallback_response(message, language)

        # Build context based on classification
        context_sections = []
        
        # Add location context if needed and available
        if classification.get('needs_location') and location_data:
            context_sections.append(f"Location Context: {location_data.get('city', 'Unknown')}, {location_data.get('country', 'Unknown')}")
        
        # Add weather context if needed and available
        if classification.get('needs_weather') and weather_data and weather_data.get('success'):
            weather_info = weather_data.get('data', {})
            context_sections.append(f"""Current Weather Context:
- Temperature: {weather_info.get('temperature', 'N/A')}°C
- Humidity: {weather_info.get('humidity', 'N/A')}%
- Conditions: {weather_info.get('description', 'N/A')}
- Precipitation: {weather_info.get('precipitation', 0)}mm""")

        context_text = "\n\n".join(context_sections) if context_sections else ""

        # Generate response based on query type
        if classification['query_type'] == 'general_knowledge':
            return self._generate_knowledge_response(message, context_text, language)
        elif classification['query_type'] == 'technical_advice':
            return self._generate_technical_response(message, context_text, language)
        elif classification['query_type'] == 'seasonal_planning':
            return self._generate_seasonal_response(message, context_text, language)
        else:  # weather_dependent
            return self._generate_weather_dependent_response(message, context_text, language)

    def _generate_knowledge_response(self, message, context, language):
        """Generate comprehensive agricultural knowledge response"""
        if language.lower() == 'japanese':
            prompt = f"""あなたは農業の専門家です。以下の質問に対して、包括的で詳細な農業知識に基づいて回答してください。

{context}

質問: {message}

以下の観点から詳しく回答してください：
1. 基本的な農業知識・事実
2. 地域や気候による違い（該当する場合）
3. 実践的なアドバイス
4. 関連する重要なポイント

回答は実用的で詳細なものにし、400文字以内にまとめてください。最後に英語の要約も追加してください。"""
        else:
            prompt = f"""You are an agricultural expert. Provide a comprehensive response based on extensive agricultural knowledge.

{context}

Question: {message}

Address these aspects:
1. Fundamental agricultural knowledge and facts
2. Regional or climatic variations (if applicable)
3. Practical recommendations
4. Related important considerations

Keep the response detailed yet practical, under 300 words."""

        return self._generate_with_model(prompt)

    def _generate_technical_response(self, message, context, language):
        """Generate specific technical agricultural advice"""
        if language.lower() == 'japanese':
            prompt = f"""あなたは農業技術の専門家です。以下の技術的な農業問題に対して、科学的根拠に基づいた具体的な解決策を提供してください。

{context}

技術的な質問: {message}

以下の観点から回答してください：
1. 問題の原因と診断
2. 具体的な解決方法・対策
3. 予防策
4. 使用する資材や技術
5. 注意点とリスク管理

科学的で実践的なアドバイスを400文字以内で提供し、最後に英語の要約も追加してください。"""
        else:
            prompt = f"""You are an agricultural technology expert. Provide specific, scientifically-based solutions for this technical farming issue.

{context}

Technical question: {message}

Address:
1. Problem diagnosis and causes
2. Specific solutions and treatments
3. Prevention strategies
4. Required materials or techniques
5. Precautions and risk management

Provide scientific and practical advice in under 300 words."""

        return self._generate_with_model(prompt)

    def _generate_seasonal_response(self, message, context, language):
        """Generate seasonal planning and timing advice"""
        if language.lower() == 'japanese':
            prompt = f"""あなたは農業計画の専門家です。以下の季節・時期に関する農業計画について、詳細なアドバイスを提供してください。

{context}

計画に関する質問: {message}

以下の観点から回答してください：
1. 最適なタイミングとスケジュール
2. 季節に応じた作業内容
3. 気候や地域による調整ポイント
4. 計画実行時の注意事項
5. 代替案や柔軟性

実用的な計画アドバイスを400文字以内で提供し、最後に英語の要約も追加してください。"""
        else:
            prompt = f"""You are an agricultural planning expert. Provide detailed seasonal planning and timing advice.

{context}

Planning question: {message}

Address:
1. Optimal timing and schedules
2. Season-appropriate activities
3. Regional and climatic adjustments
4. Implementation considerations
5. Alternative approaches and flexibility

Provide practical planning advice in under 300 words."""

        return self._generate_with_model(prompt)

    def _generate_weather_dependent_response(self, message, context, language):
        """Generate weather-dependent immediate advice"""
        if language.lower() == 'japanese':
            prompt = f"""あなたは農業気象の専門家です。現在の天候条件を考慮して、immediate agricultural advice を提供してください。

{context}

天候関連の質問: {message}

以下の観点から回答してください：
1. 現在の天候条件の農業への影響
2. 今日・今週の推奨作業
3. 天候に基づくリスク評価
4. 緊急対応が必要な事項
5. 天候変化への準備

現在の天候に基づいた実践的なアドバイスを400文字以内で提供し、最後に英語の要約も追加してください。"""
        else:
            prompt = f"""You are an agricultural meteorology expert. Provide immediate advice based on current weather conditions.

{context}

Weather-related question: {message}

Address:
1. Current weather impact on agriculture
2. Recommended activities for today/this week
3. Weather-based risk assessment
4. Urgent actions required
5. Preparation for weather changes

Provide practical weather-based advice in under 300 words."""

        return self._generate_with_model(prompt)

    def _generate_with_model(self, prompt):
        """Generate response using AI model"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=600
                )
            )
            
            if response and response.text:
                return {
                    'success': True,
                    'advice': response.text.strip(),
                    'model_used': self.model
                }
        except Exception as e:
            print(f"❌ Response generation failed: {e}")
        
        return {
            'success': False,
            'advice': 'AI response generation failed',
            'error': 'Model generation error'
        }

    def _extract_json_from_response(self, text):
        """Extract JSON from AI response"""
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return text.strip()

    def _validate_classification(self, data):
        """Validate classification response structure"""
        required_keys = ['query_type', 'needs_weather', 'needs_location', 'scope', 'topics', 'confidence']
        valid_types = ['weather_dependent', 'general_knowledge', 'technical_advice', 'seasonal_planning']
        
        return (all(key in data for key in required_keys) and 
                data['query_type'] in valid_types and
                isinstance(data['confidence'], (int, float)))

    def _fallback_classify_query(self, message):
        """Simple pattern-based classification fallback"""
        message_lower = message.lower()
        
        # Weather-dependent patterns
        weather_patterns = ['should i', 'today', 'now', 'water', 'irrigate', 'spray', 'harvest today']
        if any(pattern in message_lower for pattern in weather_patterns):
            return {
                'query_type': 'weather_dependent',
                'needs_weather': True,
                'needs_location': True,
                'scope': 'local',
                'topics': ['weather'],
                'confidence': 0.7,
                'reasoning': 'Pattern-based classification'
            }
        
        # General knowledge patterns
        knowledge_patterns = ['what', 'which crops', 'grown in', 'types of', 'varieties', 'generally']
        if any(pattern in message_lower for pattern in knowledge_patterns):
            return {
                'query_type': 'general_knowledge',
                'needs_weather': False,
                'needs_location': False,
                'scope': 'global',
                'topics': ['crops'],
                'confidence': 0.6,
                'reasoning': 'Pattern-based classification'
            }
        
        # Default to general knowledge
        return {
            'query_type': 'general_knowledge',
            'needs_weather': False,
            'needs_location': False,
            'scope': 'global',
            'topics': ['agriculture'],
            'confidence': 0.5,
            'reasoning': 'Default classification'
        }

    def _generate_fallback_response(self, message, language):
        """Simple fallback response"""
        if language.lower() == 'japanese':
            advice = f"申し訳ございませんが、AIサービスに問題があります。「{message}」についての基本的な農業情報をお調べください。"
        else:
            advice = f"Sorry, there's an AI service issue. Please research basic agricultural information about '{message}'."
        
        return {
            'success': True,
            'advice': advice,
            'model_used': 'fallback'
        }