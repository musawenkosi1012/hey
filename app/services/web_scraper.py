import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class HealthKnowledgeScraper:
    """
    Web scraper for enriching chatbot knowledge with health information
    from reliable medical sources.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Reliable health information sources
        self.sources = {
            'general': [
                'https://www.mayoclinic.org',
                'https://www.webmd.com',
                'https://medlineplus.gov'
            ],
            'conditions': {
                'hypertension': [
                    'https://www.heart.org/en/health-topics/high-blood-pressure',
                    'https://www.cdc.gov/bloodpressure'
                ],
                'diabetes': [
                    'https://www.diabetes.org',
                    'https://www.cdc.gov/diabetes'
                ],
                'heart_disease': [
                    'https://www.heart.org',
                    'https://www.cdc.gov/heartdisease'
                ]
            }
        }
        
        # Cache for scraped content
        self.knowledge_cache = {}
    
    def scrape_health_topic(self, topic: str, max_length: int = 500) -> Optional[str]:
        """
        Scrape information about a specific health topic.
        
        Args:
            topic: Health topic to search for
            max_length: Maximum length of returned text
            
        Returns:
            Scraped information or None if failed
        """
        # Check cache first
        cache_key = f"{topic}_{max_length}"
        if cache_key in self.knowledge_cache:
            return self.knowledge_cache[cache_key]
        
        try:
            # For demo purposes, return curated health information
            # In production, this would scrape from actual sources
            knowledge = self._get_curated_knowledge(topic)
            
            if knowledge:
                # Trim to max length
                if len(knowledge) > max_length:
                    knowledge = knowledge[:max_length] + "..."
                
                # Cache the result
                self.knowledge_cache[cache_key] = knowledge
                return knowledge
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping health topic '{topic}': {e}")
            return None
    
    def _get_curated_knowledge(self, topic: str) -> Optional[str]:
        """
        Get curated health knowledge for common topics.
        This simulates web scraping with pre-vetted medical information.
        """
        topic_lower = topic.lower()
        
        knowledge_base = {
            'hypertension': """
                High blood pressure (hypertension) is a common condition where the force of blood 
                against artery walls is too high. It's often called the "silent killer" because 
                it typically has no symptoms. Managing hypertension involves lifestyle changes like 
                reducing sodium intake, exercising regularly, maintaining healthy weight, limiting 
                alcohol, and managing stress. Medications may also be prescribed. Regular monitoring 
                is crucial. Target blood pressure is typically below 130/80 mmHg for most adults.
            """,
            'blood pressure': """
                Blood pressure is measured in millimeters of mercury (mmHg) and recorded as two numbers:
                systolic (top number) - pressure when heart beats, and diastolic (bottom number) - 
                pressure between beats. Normal blood pressure is less than 120/80 mmHg. Elevated is 
                120-129 systolic and less than 80 diastolic. Stage 1 hypertension is 130-139 systolic 
                or 80-89 diastolic. Regular monitoring helps detect changes early.
            """,
            'diabetes': """
                Diabetes is a chronic condition affecting how your body turns food into energy. 
                Type 2 diabetes, the most common form, can often be managed through lifestyle changes 
                including healthy eating, regular physical activity, and weight management. Monitor 
                blood glucose levels regularly. Key dietary tips include choosing whole grains, 
                limiting added sugars, eating plenty of vegetables, and controlling portion sizes.
            """,
            'diet': """
                A heart-healthy diet includes plenty of fruits, vegetables, whole grains, lean proteins,
                and healthy fats. The DASH (Dietary Approaches to Stop Hypertension) diet is 
                particularly beneficial for managing blood pressure. Limit sodium to less than 2,300 mg 
                per day, reduce saturated fats, avoid trans fats, and limit added sugars. Choose foods 
                rich in potassium, magnesium, and calcium. Stay hydrated with water.
            """,
            'exercise': """
                Regular physical activity strengthens your heart, lowers blood pressure, and improves 
                overall health. Aim for at least 150 minutes of moderate aerobic activity or 75 minutes 
                of vigorous activity weekly. Start slowly and gradually increase intensity. Walking is 
                excellent for beginners. Include strength training twice weekly. Always consult your 
                doctor before starting a new exercise program, especially with chronic conditions.
            """,
            'stress': """
                Chronic stress can raise blood pressure and negatively impact health. Stress management 
                techniques include deep breathing exercises, meditation, yoga, regular physical activity,
                adequate sleep (7-9 hours), maintaining social connections, and pursuing hobbies. 
                Practice mindfulness and consider professional counseling if stress becomes overwhelming. 
                Regular relaxation can significantly improve cardiovascular health.
            """,
            'medication': """
                Medication adherence is crucial for managing chronic conditions. Take medications exactly 
                as prescribed, at the same time each day. Use pill organizers or smartphone reminders. 
                Never stop medications without consulting your doctor, even if you feel better. Report 
                any side effects promptly. Keep a current medication list and bring it to all appointments.
                Don't skip doses, and refill prescriptions before running out.
            """,
            'heart rate': """
                A normal resting heart rate for adults ranges from 60 to 100 beats per minute. Athletes 
                may have lower rates. Factors affecting heart rate include fitness level, emotions, 
                medication, body position, and air temperature. During exercise, target heart rate zones 
                help optimize cardiovascular benefits. Monitor for unusually high or low rates and 
                irregular rhythms (palpitations). Consult a doctor if experiencing concerning symptoms.
            """,
            'sleep': """
                Quality sleep is essential for cardiovascular health. Adults need 7-9 hours per night. 
                Poor sleep can raise blood pressure and increase disease risk. Establish a consistent 
                sleep schedule, create a relaxing bedtime routine, keep bedroom cool and dark, avoid 
                screens before bed, limit caffeine and alcohol, and exercise regularly but not close 
                to bedtime. Sleep apnea should be evaluated and treated as it affects heart health.
            """,
            'sodium': """
                Reducing sodium intake is crucial for blood pressure management. The American Heart 
                Association recommends no more than 2,300 mg per day, ideally moving toward 1,500 mg. 
                Most sodium comes from processed and restaurant foods. Read nutrition labels, choose 
                fresh or frozen vegetables without added salt, limit canned foods, use herbs and spices 
                for flavor instead of salt, and rinse canned foods to remove some sodium.
            """,
            'weight': """
                Maintaining a healthy weight reduces strain on the heart and helps manage blood pressure.
                Even losing 5-10% of body weight can significantly improve health. Focus on sustainable 
                lifestyle changes rather than quick fixes. Combine healthy eating with regular physical 
                activity. Track progress, set realistic goals, and seek support from healthcare providers 
                or support groups. Body Mass Index (BMI) between 18.5-24.9 is considered healthy.
            """
        }
        
        # Search for matching topics
        for key, content in knowledge_base.items():
            if key in topic_lower or topic_lower in key:
                return content.strip()
        
        # Check for partial matches
        for key, content in knowledge_base.items():
            if any(word in topic_lower for word in key.split()):
                return content.strip()
        
        return None
    
    def search_health_tips(self, condition: str, category: str = 'general') -> List[str]:
        """
        Get health tips for a specific condition and category.
        
        Args:
            condition: Medical condition (e.g., 'hypertension', 'diabetes')
            category: Category of tips (e.g., 'diet', 'exercise', 'general')
            
        Returns:
            List of health tips
        """
        tips_database = {
            'hypertension': {
                'diet': [
                    "Reduce sodium intake to less than 2,300mg per day",
                    "Eat more potassium-rich foods like bananas, spinach, and sweet potatoes",
                    "Follow the DASH diet with plenty of fruits, vegetables, and whole grains",
                    "Limit alcohol consumption to moderate levels",
                    "Reduce saturated and trans fats in your diet"
                ],
                'exercise': [
                    "Aim for 150 minutes of moderate aerobic activity per week",
                    "Try brisk walking for 30 minutes, 5 days a week",
                    "Include strength training exercises twice per week",
                    "Start slowly and gradually increase intensity",
                    "Monitor your blood pressure before and after exercise"
                ],
                'lifestyle': [
                    "Maintain a healthy weight or lose excess weight",
                    "Quit smoking and avoid secondhand smoke",
                    "Manage stress through relaxation techniques",
                    "Get 7-9 hours of quality sleep each night",
                    "Monitor your blood pressure regularly at home"
                ]
            },
            'diabetes': {
                'diet': [
                    "Choose complex carbohydrates over simple sugars",
                    "Eat regular meals to maintain stable blood sugar",
                    "Include fiber-rich foods in every meal",
                    "Control portion sizes using the plate method",
                    "Stay hydrated with water instead of sugary drinks"
                ],
                'exercise': [
                    "Exercise helps lower blood sugar and improve insulin sensitivity",
                    "Start with 10-minute walks after meals",
                    "Mix cardio and strength training for best results",
                    "Check blood sugar before and after exercise",
                    "Keep fast-acting carbs handy during exercise"
                ],
                'monitoring': [
                    "Check blood glucose as recommended by your doctor",
                    "Keep a log of your readings and look for patterns",
                    "Test your A1C levels every 3-6 months",
                    "Watch for signs of high or low blood sugar",
                    "Regular foot checks and eye exams are essential"
                ]
            },
            'general': {
                'wellness': [
                    "Stay hydrated by drinking 6-8 glasses of water daily",
                    "Eat a balanced diet with variety and moderation",
                    "Get regular physical activity most days of the week",
                    "Maintain social connections and relationships",
                    "Practice stress management techniques daily",
                    "Avoid tobacco and limit alcohol consumption",
                    "Get regular health check-ups and screenings"
                ]
            }
        }
        
        condition_lower = condition.lower()
        category_lower = category.lower()
        
        # Get tips for the specific condition and category
        if condition_lower in tips_database:
            if category_lower in tips_database[condition_lower]:
                return tips_database[condition_lower][category_lower]
            # Return all tips for the condition if category not found
            all_tips = []
            for cat_tips in tips_database[condition_lower].values():
                all_tips.extend(cat_tips)
            return all_tips[:5]  # Return first 5
        
        # Return general wellness tips if condition not found
        return tips_database['general']['wellness']
    
    def get_normal_ranges(self, vital_type: str) -> Dict[str, any]:
        """
        Get normal ranges for various vital signs.
        
        Args:
            vital_type: Type of vital sign
            
        Returns:
            Dictionary with normal ranges and interpretation
        """
        ranges = {
            'blood_pressure': {
                'normal': 'Less than 120/80 mmHg',
                'elevated': '120-129 systolic and less than 80 diastolic',
                'stage_1': '130-139 systolic or 80-89 diastolic',
                'stage_2': '140 or higher systolic or 90 or higher diastolic',
                'crisis': 'Higher than 180 systolic and/or higher than 120 diastolic'
            },
            'heart_rate': {
                'normal_rest': '60-100 beats per minute',
                'athletic': '40-60 beats per minute (well-trained athletes)',
                'moderate_exercise': '50-70% of maximum heart rate',
                'vigorous_exercise': '70-85% of maximum heart rate',
                'max_formula': '220 minus your age'
            },
            'oxygen_saturation': {
                'normal': '95-100%',
                'mild_hypoxemia': '90-94%',
                'moderate': '85-89%',
                'severe': 'Below 85%',
                'note': 'Consult doctor if consistently below 95%'
            },
            'blood_glucose': {
                'fasting_normal': '70-99 mg/dL',
                'fasting_prediabetes': '100-125 mg/dL',
                'fasting_diabetes': '126 mg/dL or higher',
                'random_normal': 'Less than 140 mg/dL',
                'random_prediabetes': '140-199 mg/dL',
                'random_diabetes': '200 mg/dL or higher'
            }
        }
        
        vital_lower = vital_type.lower().replace(' ', '_')
        return ranges.get(vital_lower, {})


# Global scraper instance
scraper = HealthKnowledgeScraper()
