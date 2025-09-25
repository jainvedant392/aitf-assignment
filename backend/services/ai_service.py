from google import genai
from google.genai import types
from config import Config
import json

class AIService:
    def __init__(self):
        """Initialize the AI service with Google GenAI SDK"""
        try:
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
            self.primary_model = "gemini-2.5-flash"
            self.fallback_model = "gemini-2.0-flash"
            
            print(f"✅ Enhanced AI Service initialized")
            
        except Exception as e:
            print(f"❌ AI Service initialization failed: {e}")
            self.client = None

    def generate_intelligent_response(self, message, query_classification, location_data=None, weather_data=None, language='japanese'):
        """
        Generate response based on query intelligence classification
        """
        if not self.client:
            return self._get_fallback_response(message, language)

        # Route to appropriate response generator based on classification
        query_type = query_classification.get('query_type', 'general_knowledge')
        
        if query_type == 'weather_dependent':
            return self._generate_weather_dependent_advice(message, location_data, weather_data, language)
        elif query_type == 'general_knowledge':
            return self._generate_knowledge_response(message, location_data, language)
        elif query_type == 'technical_advice':
            return self._generate_technical_advice(message, location_data, language)
        elif query_type == 'seasonal_planning':
            return self._generate_seasonal_advice(message, location_data, language)
        else:
            # Default to comprehensive response
            return self._generate_comprehensive_advice(message, location_data, weather_data, language)

    def _generate_knowledge_response(self, message, location_data, language):
        """Generate comprehensive agricultural knowledge response"""
        location_context = ""
        if location_data and location_data.get('city'):
            location_context = f"Location context: {location_data['city']}, {location_data['country']}"

        if language.lower() == 'japanese':
            prompt = f"""あなたは農業の百科事典的な専門家です。以下の質問に対して、包括的で詳細な農業知識を提供してください。

{location_context}

質問: {message}

以下の観点から詳しく回答してください：
1. 基本的な農業知識と事実
2. 作物の種類、品種、特徴
3. 栽培方法と技術
4. 地域による違いや適応性
5. 歴史的背景や文化的側面
6. 現代の農業技術との関連

情報は正確で実用的なものにし、農家や学習者にとって価値のある内容にしてください。500文字以内で回答し、最後に英語の要約も追加してください。"""
        else:
            prompt = f"""You are an encyclopedic agricultural expert. Provide comprehensive and detailed agricultural knowledge for this question.

{location_context}

Question: {message}

Address these aspects thoroughly:
1. Fundamental agricultural knowledge and facts
2. Crop types, varieties, and characteristics
3. Cultivation methods and techniques
4. Regional differences and adaptations
5. Historical background and cultural aspects
6. Modern agricultural technology connections

Ensure information is accurate and practical, valuable for farmers and learners. Keep under 400 words."""

        return self._generate_with_models(prompt)

    def _generate_technical_advice(self, message, location_data, language):
        """Generate specific technical solutions"""
        location_context = ""
        if location_data and location_data.get('city'):
            location_context = f"Location context: {location_data['city']}, {location_data['country']}"

        if language.lower() == 'japanese':
            prompt = f"""あなたは農業技術の専門家です。以下の技術的問題に対して、科学的根拠に基づいた具体的な解決策を提供してください。

{location_context}

技術的課題: {message}

以下の要素を含む詳細な回答をしてください：
1. 問題の科学的分析と原因
2. 段階的な解決方法
3. 必要な資材・薬剤・設備
4. 実施時期とスケジュール
5. 予防策と管理方法
6. コスト効果と代替手段
7. リスク管理と安全対策

実践的で科学的な根拠に基づいたアドバイスを500文字以内で提供し、最後に英語の要約も追加してください。"""
        else:
            prompt = f"""You are an agricultural technology expert. Provide scientifically-based, specific solutions for this technical challenge.

{location_context}

Technical challenge: {message}

Include these detailed elements:
1. Scientific analysis and root causes
2. Step-by-step solution methods
3. Required materials, chemicals, equipment
4. Implementation timing and schedule
5. Prevention strategies and management
6. Cost-effectiveness and alternatives
7. Risk management and safety measures

Provide practical, science-based advice under 400 words."""

        return self._generate_with_models(prompt)

    def _generate_seasonal_advice(self, message, location_data, language):
        """Generate seasonal planning and timing advice"""
        location_context = ""
        if location_data and location_data.get('city'):
            location_context = f"Location context: {location_data['city']}, {location_data['country']}"

        if language.lower() == 'japanese':
            prompt = f"""あなたは農業計画の専門家です。季節と時期に関する農業計画について、包括的なアドバイスを提供してください。

{location_context}

計画相談: {message}

以下の要素を含む詳細な計画を提示してください：
1. 最適なタイミングと季節スケジュール
2. 地域の気候特性による調整
3. 作物ローテーションと輪作計画
4. 各段階での作業内容
5. リスク管理と代替計画
6. 市場性と経済性の考慮
7. 持続可能性と環境配慮

実用的で長期的視点に立った計画アドバイスを500文字以内で提供し、最後に英語の要約も追加してください。"""
        else:
            prompt = f"""You are an agricultural planning expert. Provide comprehensive seasonal planning and timing advice.

{location_context}

Planning inquiry: {message}

Include these detailed planning elements:
1. Optimal timing and seasonal schedules
2. Regional climate adjustments
3. Crop rotation and succession planning
4. Stage-specific activities
5. Risk management and contingency plans
6. Market considerations and economics
7. Sustainability and environmental factors

Provide practical, long-term planning advice under 400 words."""

        return self._generate_with_models(prompt)

    def _generate_weather_dependent_advice(self, message, location_data, weather_data, language):
        """Generate immediate weather-based advice"""
        # Build weather context
        weather_context = ""
        if weather_data and weather_data.get('success'):
            data = weather_data.get('data', {})
            weather_context = f"""現在の気象情報:
- 場所: {data.get('location', '不明')}
- 気温: {data.get('temperature', 'N/A')}°C (体感温度: {data.get('feels_like', 'N/A')}°C)
- 湿度: {data.get('humidity', 'N/A')}%
- 天候: {data.get('description', 'N/A')}
- 風速: {data.get('wind_speed', 'N/A')} m/s
- 降水量: {data.get('precipitation', 0)}mm"""

        if language.lower() == 'japanese':
            prompt = f"""あなたは農業気象の専門家です。現在の天候条件を詳細に分析し、immediate農業アドバイスを提供してください。

{weather_context}

質問: {message}

以下の観点から具体的なアドバイスを提供してください：
1. 現在の天候が農作物に与える影響
2. 今日実行すべき緊急作業
3. 今週の推奨作業スケジュール
4. 天候に基づくリスク評価
5. 病害虫発生の可能性
6. 灌漑・水管理の調整
7. 天候変化への準備対策

現在の天候条件に基づいた実践的で緊急性のあるアドバイスを500文字以内で提供し、最後に英語の要約も追加してください。"""
        else:
            prompt = f"""You are an agricultural meteorology expert. Analyze current weather conditions in detail and provide immediate agricultural advice.

{weather_context}

Question: {message}

Provide specific advice covering:
1. Current weather impact on crops
2. Urgent tasks to perform today
3. Recommended work schedule this week
4. Weather-based risk assessment
5. Pest and disease probability
6. Irrigation and water management adjustments
7. Preparation for weather changes

Provide practical, time-sensitive advice under 400 words based on current weather conditions."""

        return self._generate_with_models(prompt)

    def _generate_comprehensive_advice(self, message, location_data, weather_data, language):
        """Generate comprehensive response covering all aspects"""
        context_parts = []
        
        if location_data and location_data.get('city'):
            context_parts.append(f"Location: {location_data['city']}, {location_data['country']}")
        
        if weather_data and weather_data.get('success'):
            data = weather_data.get('data', {})
            context_parts.append(f"Current weather: {data.get('temperature', 'N/A')}°C, {data.get('humidity', 'N/A')}% humidity, {data.get('description', 'N/A')}")
        
        context_text = "\n".join(context_parts)

        if language.lower() == 'japanese':
            prompt = f"""あなたは総合的な農業アドバイザーです。以下の質問に対して、あらゆる角度から包括的な農業アドバイスを提供してください。

{context_text}

質問: {message}

以下の全ての観点から総合的に回答してください：
1. 一般的な農業知識
2. 技術的な解決方法
3. 季節・時期的な考慮事項
4. 天候・環境要因
5. 地域特性への適応
6. 経済的・実用的側面
7. 持続可能性と将来性

農業のあらゆる側面を考慮した包括的で実用的なアドバイスを500文字以内で提供し、最後に英語の要約も追加してください。"""
        else:
            prompt = f"""You are a comprehensive agricultural advisor. Provide holistic agricultural advice covering all relevant aspects for this question.

{context_text}

Question: {message}

Address all relevant aspects comprehensively:
1. General agricultural knowledge
2. Technical solutions
3. Seasonal and timing considerations
4. Weather and environmental factors
5. Regional adaptations
6. Economic and practical aspects
7. Sustainability and future considerations

Provide comprehensive, practical advice considering all aspects of agriculture, under 400 words."""

        return self._generate_with_models(prompt)

    def _generate_with_models(self, prompt):
        """Generate response trying multiple models"""
        models_to_try = [self.primary_model, self.fallback_model]
        
        for model_name in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        max_output_tokens=700,
                        top_p=0.9
                    )
                )
                
                if response and hasattr(response, 'text') and response.text:
                    return {
                        'success': True,
                        'advice': response.text.strip(),
                        'model_used': model_name
                    }
                
            except Exception as e:
                print(f"❌ Model {model_name} failed: {str(e)}")
                continue
        
        # All models failed
        return {
            'success': False,
            'advice': 'AI models are temporarily unavailable',
            'error': 'All models failed'
        }

    def _get_fallback_response(self, message, language):
        """Simple fallback when AI is unavailable"""
        if language.lower() == 'japanese':
            advice = f"""申し訳ございませんが、AIサービスに一時的な問題が発生しています。

「{message}」について：

基本的なガイダンス:
・地域の農業普及センターに相談することをお勧めします
・農業関連の信頼できるウェブサイトで情報を確認してください
・地元の農家や農業組合からアドバイスを求めてください

後ほど再度お試しください。

---
[English] Sorry for the temporary AI service issue. For "{message}", we recommend consulting local agricultural extension services, checking reliable agricultural websites, or seeking advice from local farmers and agricultural cooperatives."""
        else:
            advice = f"""Sorry, there's a temporary AI service issue. 

For your question about "{message}":

Basic guidance:
• Consult local agricultural extension services
• Check reliable agricultural websites
• Seek advice from local farmers and cooperatives

Please try again later."""
        
        return {
            'success': True,
            'advice': advice,
            'model_used': 'fallback-response'
        }

    # Keep existing methods for backward compatibility
    def generate_agricultural_advice(self, user_input, weather_data, language='japanese'):
        """Legacy method - routes to comprehensive advice"""
        return self._generate_comprehensive_advice(user_input, None, weather_data, language)

    def get_crop_recommendations(self, weather_data, season='current'):
        """Get crop recommendations based on weather conditions"""
        if not weather_data or not weather_data.get('success'):
            return {'success': False, 'error': 'Invalid weather data'}
        
        temp = weather_data.get('data', {}).get('temperature', 20)
        
        recommendations = []
        
        for crop, thresholds in Config.CROP_TEMP_THRESHOLDS.items():
            if thresholds['min'] <= temp <= thresholds['max']:
                suitability_score = 100 - abs(temp - thresholds['optimal']) * 5
                recommendations.append({
                    'crop': crop,
                    'suitability_score': max(suitability_score, 0),
                    'reason': f"Current temperature ({temp}°C) is suitable for {crop}"
                })
        
        recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return {
            'success': True,
            'recommendations': recommendations[:5]
        }