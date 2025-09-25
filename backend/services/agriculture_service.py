"""
Agriculture Service
Provides domain-specific agricultural logic, analysis, and recommendations
"""

from datetime import datetime, timedelta
from config import Config
import math

class AgricultureService:
    def __init__(self):
        self.crop_data = self._load_crop_data()
        self.pest_patterns = self._load_pest_patterns()
        self.planting_schedules = self._load_planting_schedules()
    
    def _load_crop_data(self):
        """Load crop-specific data and thresholds"""
        return {
            'rice': {
                'growth_stages': ['seedling', 'vegetative', 'reproductive', 'ripening'],
                'water_needs': {'high': [1, 2], 'medium': [0, 3], 'low': []},
                'pest_susceptibility': ['stem_borer', 'blast_disease', 'brown_planthopper'],
                'optimal_ph': {'min': 5.5, 'max': 7.0},
                'nitrogen_needs': {'high': ['vegetative'], 'medium': ['reproductive'], 'low': ['ripening']}
            },
            'wheat': {
                'growth_stages': ['germination', 'tillering', 'stem_extension', 'flowering', 'grain_filling'],
                'water_needs': {'high': [2, 3], 'medium': [1, 4], 'low': [0]},
                'pest_susceptibility': ['aphids', 'rust_disease', 'powdery_mildew'],
                'optimal_ph': {'min': 6.0, 'max': 7.5},
                'nitrogen_needs': {'high': ['tillering', 'stem_extension'], 'medium': ['flowering'], 'low': ['grain_filling']}
            },
            'corn': {
                'growth_stages': ['emergence', 'vegetative', 'pollination', 'grain_filling', 'maturity'],
                'water_needs': {'high': [2, 3], 'medium': [1, 4], 'low': [0]},
                'pest_susceptibility': ['corn_borer', 'armyworm', 'leaf_blight'],
                'optimal_ph': {'min': 6.0, 'max': 6.8},
                'nitrogen_needs': {'high': ['vegetative', 'pollination'], 'medium': ['grain_filling'], 'low': ['maturity']}
            },
            'tomato': {
                'growth_stages': ['seedling', 'vegetative', 'flowering', 'fruiting', 'harvest'],
                'water_needs': {'high': [1, 2, 3], 'medium': [4], 'low': [0]},
                'pest_susceptibility': ['whitefly', 'aphids', 'blight', 'hornworm'],
                'optimal_ph': {'min': 6.0, 'max': 6.8},
                'nitrogen_needs': {'high': ['vegetative'], 'medium': ['flowering', 'fruiting'], 'low': ['harvest']}
            },
            'potato': {
                'growth_stages': ['planting', 'emergence', 'vegetative', 'tuber_formation', 'maturity'],
                'water_needs': {'high': [2, 3], 'medium': [1], 'low': [0, 4]},
                'pest_susceptibility': ['colorado_beetle', 'late_blight', 'aphids'],
                'optimal_ph': {'min': 5.0, 'max': 6.0},
                'nitrogen_needs': {'high': ['vegetative'], 'medium': ['tuber_formation'], 'low': ['maturity']}
            }
        }
    
    def _load_pest_patterns(self):
        """Load pest and disease patterns based on weather conditions"""
        return {
            'high_humidity_pests': {
                'threshold': 80,
                'pests': ['fungal_diseases', 'slug', 'snail', 'powdery_mildew'],
                'prevention': ['improve_ventilation', 'reduce_watering', 'apply_fungicide']
            },
            'hot_weather_pests': {
                'threshold': 30,
                'pests': ['spider_mites', 'aphids', 'whitefly', 'thrips'],
                'prevention': ['increase_watering', 'provide_shade', 'release_beneficial_insects']
            },
            'wet_conditions': {
                'threshold': 10,  # mm precipitation
                'pests': ['root_rot', 'damping_off', 'bacterial_diseases'],
                'prevention': ['improve_drainage', 'reduce_irrigation', 'apply_copper_spray']
            },
            'cool_moist': {
                'temp_max': 20,
                'humidity_min': 70,
                'pests': ['gray_mold', 'downy_mildew', 'black_spot'],
                'prevention': ['increase_spacing', 'improve_airflow', 'preventive_spraying']
            }
        }
    
    def _load_planting_schedules(self):
        """Load planting schedules by crop and region"""
        return {
            'temperate': {
                'rice': {'plant': [4, 5], 'harvest': [9, 10]},
                'wheat': {'plant': [9, 10, 11], 'harvest': [6, 7]},
                'corn': {'plant': [4, 5, 6], 'harvest': [9, 10]},
                'tomato': {'plant': [3, 4, 5], 'harvest': [7, 8, 9]},
                'potato': {'plant': [3, 4], 'harvest': [7, 8]}
            }
        }
    
    def enhance_crop_recommendations(self, recommendations, weather_data):
        """Enhance basic crop recommendations with detailed agricultural analysis"""
        if not recommendations.get('success') or not recommendations.get('recommendations'):
            return recommendations
        
        enhanced = []
        weather = weather_data.get('weather') or weather_data.get('data', {})
        
        for rec in recommendations['recommendations']:
            crop_type = rec['crop']
            crop_info = self.crop_data.get(crop_type, {})
            
            # Add detailed analysis
            enhanced_rec = rec.copy()
            enhanced_rec.update({
                'growth_stages': crop_info.get('growth_stages', []),
                'water_requirements': self._analyze_water_needs(crop_type, weather),
                'nutrient_recommendations': self._get_nutrient_recommendations(crop_type),
                'pest_risk_factors': self._assess_crop_pest_risk(crop_type, weather),
                'planting_timing': self._get_planting_timing(crop_type),
                'expected_yield': self._estimate_yield_potential(crop_type, weather)
            })
            
            enhanced.append(enhanced_rec)
        
        return {
            'success': True,
            'recommendations': enhanced,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def add_scientific_context(self, analysis, crop_type, growth_stage):
        """Add scientific agricultural context to crop analysis"""
        if not analysis.get('success'):
            return analysis
        
        crop_info = self.crop_data.get(crop_type, {})
        
        scientific_context = {
            'physiological_stage': self._get_physiological_insights(crop_type, growth_stage),
            'nutrient_cycling': self._get_nutrient_cycling_info(crop_type, growth_stage),
            'environmental_stress_factors': self._assess_stress_factors(analysis.get('weather_conditions', {})),
            'optimal_management_practices': self._get_management_practices(crop_type, growth_stage),
            'scientific_references': self._get_relevant_research(crop_type, growth_stage)
        }
        
        enhanced_analysis = analysis.copy()
        enhanced_analysis['scientific_context'] = scientific_context
        
        return enhanced_analysis
    
    def add_seasonal_tasks(self, advice, month):
        """Add practical seasonal tasks and calendar items"""
        if not advice.get('success'):
            return advice
        
        season = self._get_season(month)
        seasonal_tasks = {
            'spring': [
                'Prepare seed beds and planting areas',
                'Check and repair irrigation systems',
                'Apply pre-planting fertilizers',
                'Start seedling production',
                'Plan crop rotation schedule'
            ],
            'summer': [
                'Monitor irrigation and water management',
                'Implement pest and disease control',
                'Side-dress crops with nitrogen',
                'Harvest early summer crops',
                'Maintain equipment and tools'
            ],
            'autumn': [
                'Harvest main season crops',
                'Prepare fields for winter cover crops',
                'Store seeds and equipment properly',
                'Plan next year crop selections',
                'Apply compost and organic matter'
            ],
            'winter': [
                'Plan crop rotations for next year',
                'Maintain and repair equipment',
                'Attend agricultural education programs',
                'Order seeds and supplies',
                'Analyze previous season performance'
            ]
        }
        
        enhanced_advice = advice.copy()
        enhanced_advice['seasonal_tasks'] = seasonal_tasks.get(season, [])
        enhanced_advice['priority_tasks'] = self._get_priority_tasks(month)
        
        return enhanced_advice
    
    def assess_pest_risk(self, weather_data, crop_type):
        """Assess pest and disease risk based on weather conditions"""
        weather = weather_data.get('weather') or weather_data.get('data', {})
        
        risk_assessment = {
            'overall_risk': 'low',
            'specific_risks': [],
            'prevention_measures': [],
            'monitoring_recommendations': []
        }
        
        temp = weather.get('temperature', 20)
        humidity = weather.get('humidity', 50)
        precipitation = weather.get('precipitation', 0)
        
        # Assess different risk factors
        risk_factors = []
        
        # High humidity risks
        if humidity > self.pest_patterns['high_humidity_pests']['threshold']:
            risk_factors.extend(self.pest_patterns['high_humidity_pests']['pests'])
            risk_assessment['prevention_measures'].extend(
                self.pest_patterns['high_humidity_pests']['prevention']
            )
        
        # Hot weather risks
        if temp > self.pest_patterns['hot_weather_pests']['threshold']:
            risk_factors.extend(self.pest_patterns['hot_weather_pests']['pests'])
            risk_assessment['prevention_measures'].extend(
                self.pest_patterns['hot_weather_pests']['prevention']
            )
        
        # Wet conditions risks
        if precipitation > self.pest_patterns['wet_conditions']['threshold']:
            risk_factors.extend(self.pest_patterns['wet_conditions']['pests'])
            risk_assessment['prevention_measures'].extend(
                self.pest_patterns['wet_conditions']['prevention']
            )
        
        # Cool and moist conditions
        cool_moist = self.pest_patterns['cool_moist']
        if temp < cool_moist['temp_max'] and humidity > cool_moist['humidity_min']:
            risk_factors.extend(cool_moist['pests'])
            risk_assessment['prevention_measures'].extend(cool_moist['prevention'])
        
        # Crop-specific risks
        if crop_type in self.crop_data:
            crop_pests = self.crop_data[crop_type].get('pest_susceptibility', [])
            risk_factors.extend(crop_pests)
        
        # Determine overall risk level
        risk_count = len(set(risk_factors))
        if risk_count > 5:
            risk_assessment['overall_risk'] = 'high'
        elif risk_count > 2:
            risk_assessment['overall_risk'] = 'medium'
        
        risk_assessment['specific_risks'] = list(set(risk_factors))
        risk_assessment['prevention_measures'] = list(set(risk_assessment['prevention_measures']))
        
        # Add monitoring recommendations
        risk_assessment['monitoring_recommendations'] = [
            'Check plants daily for early signs of pests',
            'Monitor weather forecasts for risk conditions',
            'Inspect undersides of leaves for eggs',
            'Look for changes in plant color or growth'
        ]
        
        return {
            'success': True,
            'crop_type': crop_type,
            'weather_conditions': weather,
            'risk_assessment': risk_assessment,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_irrigation_recommendations(self, weather_data, crop_type, soil_type):
        """Generate irrigation recommendations based on conditions"""
        weather = weather_data.get('weather') or weather_data.get('data', {})
        agricultural_analysis = weather_data.get('agricultural_analysis', {})
        
        irrigation_advice = {
            'irrigation_needed': agricultural_analysis.get('irrigation_needed', False),
            'water_amount': 'medium',
            'frequency': 'daily',
            'timing': 'early_morning',
            'method': 'drip_irrigation',
            'considerations': []
        }
        
        temp = weather.get('temperature', 20)
        humidity = weather.get('humidity', 50)
        precipitation = weather.get('precipitation', 0)
        wind_speed = weather.get('wind_speed', 0)
        
        # Adjust based on temperature
        if temp > 30:
            irrigation_advice['water_amount'] = 'high'
            irrigation_advice['frequency'] = 'twice_daily'
            irrigation_advice['considerations'].append('High temperature increases water needs')
        elif temp < 15:
            irrigation_advice['water_amount'] = 'low'
            irrigation_advice['frequency'] = 'every_other_day'
            irrigation_advice['considerations'].append('Cool weather reduces water needs')
        
        # Adjust for recent precipitation
        if precipitation > 10:
            irrigation_advice['irrigation_needed'] = False
            irrigation_advice['considerations'].append('Recent rainfall provides adequate moisture')
        elif precipitation > 5:
            irrigation_advice['water_amount'] = 'low'
            irrigation_advice['considerations'].append('Recent light rain reduces irrigation needs')
        
        # Adjust for humidity
        if humidity < 40:
            irrigation_advice['water_amount'] = 'high'
            irrigation_advice['considerations'].append('Low humidity increases evaporation')
        elif humidity > 80:
            irrigation_advice['frequency'] = 'as_needed'
            irrigation_advice['considerations'].append('High humidity reduces water loss')
        
        # Adjust for wind
        if wind_speed > 15:
            irrigation_advice['considerations'].append('Strong winds increase water loss - irrigate more frequently')
        
        # Crop-specific adjustments
        if crop_type in self.crop_data:
            crop_info = self.crop_data[crop_type]
            # Add crop-specific water needs logic here
        
        # Soil type adjustments
        soil_adjustments = {
            'clay': {'frequency': 'less_frequent', 'amount': 'more_per_session'},
            'sand': {'frequency': 'more_frequent', 'amount': 'less_per_session'},
            'loam': {'frequency': 'moderate', 'amount': 'moderate'}
        }
        
        if soil_type in soil_adjustments:
            adjustment = soil_adjustments[soil_type]
            irrigation_advice['soil_specific_advice'] = adjustment
        
        return {
            'success': True,
            'crop_type': crop_type,
            'soil_type': soil_type,
            'weather_conditions': weather,
            'irrigation_recommendations': irrigation_advice,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_planting_calendar(self, city, country, crop_type, year):
        """Generate planting calendar for specified location and crops"""
        calendar_data = {
            'year': year,
            'location': f"{city}, {country}",
            'crops': {},
            'monthly_tasks': {}
        }
        
        # Determine climate zone (simplified)
        climate_zone = 'temperate'  # Default, could be enhanced with actual climate data
        
        if crop_type == 'all':
            crops_to_include = list(self.crop_data.keys())
        else:
            crops_to_include = [crop_type] if crop_type in self.crop_data else []
        
        planting_schedule = self.planting_schedules.get(climate_zone, {})
        
        for crop in crops_to_include:
            if crop in planting_schedule:
                schedule = planting_schedule[crop]
                calendar_data['crops'][crop] = {
                    'planting_months': schedule.get('plant', []),
                    'harvest_months': schedule.get('harvest', []),
                    'growth_duration': len(schedule.get('harvest', [])) + len(schedule.get('plant', [])),
                    'care_schedule': self._generate_care_schedule(crop)
                }
        
        # Generate monthly tasks
        for month in range(1, 13):
            month_name = datetime(year, month, 1).strftime('%B')
            tasks = []
            
            for crop, schedule in calendar_data['crops'].items():
                if month in schedule['planting_months']:
                    tasks.append(f"Plant {crop}")
                if month in schedule['harvest_months']:
                    tasks.append(f"Harvest {crop}")
            
            calendar_data['monthly_tasks'][month_name] = tasks
        
        return {
            'success': True,
            'calendar': calendar_data,
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_soil_conditions(self, soil_data, weather_data):
        """Analyze soil conditions and provide improvement recommendations"""
        analysis = {
            'soil_health_score': 0,
            'nutrient_status': {},
            'ph_analysis': {},
            'recommendations': [],
            'amendments_needed': []
        }
        
        # Analyze pH
        ph = soil_data.get('ph', 6.5)
        analysis['ph_analysis'] = {
            'current_ph': ph,
            'status': 'optimal' if 6.0 <= ph <= 7.0 else ('acidic' if ph < 6.0 else 'alkaline'),
            'recommendations': self._get_ph_recommendations(ph)
        }
        
        # Analyze nutrients
        nutrients = ['nitrogen', 'phosphorus', 'potassium']
        for nutrient in nutrients:
            level = soil_data.get(nutrient, 'medium')
            analysis['nutrient_status'][nutrient] = {
                'level': level,
                'status': 'adequate' if level == 'medium' else level,
                'recommendations': self._get_nutrient_recommendations_specific(nutrient, level)
            }
        
        # Calculate soil health score
        score = 70  # Base score
        if 6.0 <= ph <= 7.0:
            score += 10
        if soil_data.get('organic_matter', 'low') in ['medium', 'high']:
            score += 10
        if soil_data.get('drainage', 'poor') == 'good':
            score += 10
        
        analysis['soil_health_score'] = min(score, 100)
        
        # General recommendations
        analysis['recommendations'] = [
            'Test soil annually for nutrients and pH',
            'Add compost regularly to improve soil structure',
            'Practice crop rotation to maintain soil health',
            'Avoid walking on wet soil to prevent compaction'
        ]
        
        return {
            'success': True,
            'soil_analysis': analysis,
            'weather_context': weather_data,
            'timestamp': datetime.now().isoformat()
        }
    
    # Helper methods
    def _analyze_water_needs(self, crop_type, weather):
        """Analyze water needs for specific crop and weather"""
        base_needs = 'medium'
        temp = weather.get('temperature', 20)
        humidity = weather.get('humidity', 50)
        
        if temp > 30:
            base_needs = 'high'
        elif temp < 15:
            base_needs = 'low'
        
        if humidity < 40:
            base_needs = 'high'
        
        return base_needs
    
    def _get_nutrient_recommendations(self, crop_type):
        """Get nutrient recommendations for crop"""
        crop_info = self.crop_data.get(crop_type, {})
        return {
            'primary_nutrients': 'NPK (Nitrogen, Phosphorus, Potassium)',
            'timing': 'Apply before planting and during growth phases',
            'specific_needs': crop_info.get('nitrogen_needs', {})
        }
    
    def _assess_crop_pest_risk(self, crop_type, weather):
        """Assess pest risk for specific crop"""
        crop_info = self.crop_data.get(crop_type, {})
        pests = crop_info.get('pest_susceptibility', [])
        
        humidity = weather.get('humidity', 50)
        temp = weather.get('temperature', 20)
        
        risk_level = 'low'
        if humidity > 80 or temp > 30:
            risk_level = 'medium'
        if humidity > 90 and temp > 25:
            risk_level = 'high'
        
        return {
            'level': risk_level,
            'common_pests': pests[:3],  # Top 3 pests
            'prevention': 'Monitor regularly and use integrated pest management'
        }
    
    def _get_planting_timing(self, crop_type):
        """Get optimal planting timing"""
        schedule = self.planting_schedules.get('temperate', {}).get(crop_type, {})
        return {
            'optimal_months': schedule.get('plant', []),
            'harvest_months': schedule.get('harvest', []),
            'note': 'Timing may vary based on local climate conditions'
        }
    
    def _estimate_yield_potential(self, crop_type, weather):
        """Estimate yield potential based on conditions"""
        temp = weather.get('temperature', 20)
        
        # Simplified yield estimation
        if crop_type in Config.CROP_TEMP_THRESHOLDS:
            thresholds = Config.CROP_TEMP_THRESHOLDS[crop_type]
            if thresholds['min'] <= temp <= thresholds['max']:
                if abs(temp - thresholds['optimal']) <= 3:
                    return 'high'
                else:
                    return 'medium'
            else:
                return 'low'
        
        return 'medium'
    
    def _get_physiological_insights(self, crop_type, growth_stage):
        """Get physiological insights for crop and growth stage"""
        return f"During {growth_stage} stage, {crop_type} focuses on specific metabolic processes"
    
    def _get_nutrient_cycling_info(self, crop_type, growth_stage):
        """Get nutrient cycling information"""
        return f"Nutrient uptake patterns for {crop_type} during {growth_stage} stage"
    
    def _assess_stress_factors(self, weather_conditions):
        """Assess environmental stress factors"""
        stress_factors = []
        temp = weather_conditions.get('temperature', 20)
        
        if temp > 35:
            stress_factors.append('Heat stress')
        if temp < 5:
            stress_factors.append('Cold stress')
        
        return stress_factors
    
    def _get_management_practices(self, crop_type, growth_stage):
        """Get optimal management practices"""
        return [
            f"Monitor {crop_type} regularly during {growth_stage}",
            "Adjust irrigation based on growth needs",
            "Apply appropriate fertilizers for current growth stage"
        ]
    
    def _get_relevant_research(self, crop_type, growth_stage):
        """Get relevant research references"""
        return [
            f"Research on {crop_type} cultivation practices",
            f"Studies on {growth_stage} optimization",
            "Climate-smart agriculture techniques"
        ]
    
    def _get_season(self, month):
        """Get season from month number"""
        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'autumn'
        else:
            return 'winter'
    
    def _get_priority_tasks(self, month):
        """Get priority tasks for the month"""
        season = self._get_season(month)
        priority_tasks = {
            'spring': ['Soil preparation', 'Seed planting', 'Irrigation setup'],
            'summer': ['Pest monitoring', 'Water management', 'Nutrient application'],
            'autumn': ['Harvest planning', 'Storage preparation', 'Field cleanup'],
            'winter': ['Equipment maintenance', 'Planning for next season', 'Education and training']
        }
        return priority_tasks.get(season, [])
    
    def _generate_care_schedule(self, crop):
        """Generate care schedule for crop"""
        return {
            'weekly_tasks': ['Monitor growth', 'Check for pests', 'Assess water needs'],
            'monthly_tasks': ['Fertilizer application', 'Pruning if needed', 'Soil testing'],
            'seasonal_tasks': ['Major fertilization', 'Equipment maintenance', 'Harvest preparation']
        }
    
    def _get_ph_recommendations(self, ph):
        """Get pH adjustment recommendations"""
        if ph < 6.0:
            return ['Add lime to raise pH', 'Use wood ash for alkalinity', 'Avoid acid-forming fertilizers']
        elif ph > 7.0:
            return ['Add sulfur to lower pH', 'Use acid-forming fertilizers', 'Add organic matter']
        else:
            return ['Maintain current pH with balanced fertilizers']
    
    def _get_nutrient_recommendations_specific(self, nutrient, level):
        """Get specific nutrient recommendations"""
        recommendations = {
            'nitrogen': {
                'low': ['Apply nitrogen-rich fertilizer', 'Use compost or manure', 'Plant nitrogen-fixing cover crops'],
                'high': ['Reduce nitrogen applications', 'Plant nitrogen-using crops', 'Avoid high-nitrogen fertilizers']
            },
            'phosphorus': {
                'low': ['Apply phosphate fertilizer', 'Use bone meal', 'Add rock phosphate'],
                'high': ['Avoid phosphate fertilizers', 'Plant phosphorus-accumulating plants', 'Test soil regularly']
            },
            'potassium': {
                'low': ['Apply potash fertilizer', 'Use wood ash', 'Add granite dust'],
                'high': ['Reduce potassium applications', 'Leach excess with water', 'Plant potassium-using crops']
            }
        }
        
        return recommendations.get(nutrient, {}).get(level, ['Maintain current levels'])