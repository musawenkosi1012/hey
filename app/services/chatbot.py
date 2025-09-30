import os
import json
import random
from datetime import datetime, timedelta, timezone
from app.models.vitals import VitalSigns, RiskPrediction
from app.models.patient import Patient
from app.models.insights import ChatMessage
from app import db
from app.services.web_scraper import scraper

# Helper function for naive UTC datetime (for DB compatibility)
def utc_now():
    return datetime.utcnow()

class HealthChatbot:
    def __init__(self):
        self.openai_available = bool(os.getenv('OPENAI_API_KEY'))
        if self.openai_available:
            try:
                import openai
                openai.api_key = os.getenv('OPENAI_API_KEY')
                self.openai = openai
            except ImportError:
                self.openai_available = False
        
        # Fallback responses for demo
        self.responses = {
            'greeting': [
                "Hello! I'm your AI health coach. How can I help you today?",
                "Hi there! I'm here to help you with your health questions.",
                "Welcome! I have access to your vitals and can provide personalized health advice."
            ],
            'blood_pressure': [
                "Based on your recent readings, your blood pressure is {bp_status}. {bp_advice}",
                "Your current blood pressure is {current_bp}. {bp_advice}",
                "I see your blood pressure averaging {avg_bp} today. {bp_advice}"
            ],
            'diet': [
                "For better health with your current vitals, I recommend a low-sodium diet with plenty of vegetables.",
                "Given your blood pressure readings, try to limit processed foods and increase your intake of potassium-rich foods like bananas and spinach.",
                "A Mediterranean-style diet would be great for your health profile - lots of fish, olive oil, and fresh vegetables."
            ],
            'exercise': [
                "I see you've walked {steps} steps today. Try to aim for at least 6,000 steps daily for cardiovascular health.",
                "Light exercise like walking or swimming can help improve your blood pressure and overall health.",
                "Based on your heart rate patterns, gentle cardio exercises would be beneficial."
            ],
            'medication': [
                "Please remember to take your medications as prescribed by your doctor.",
                "If you have concerns about your medications, please consult with your healthcare provider.",
                "Medication adherence is crucial for managing chronic conditions effectively."
            ],
            'stress': [
                "Stress can affect your blood pressure. Try deep breathing exercises or meditation.",
                "Consider stress-reduction techniques like yoga or mindfulness meditation.",
                "Managing stress is important for your overall health. Try to get adequate sleep and exercise regularly."
            ],
            'default': [
                "That's a great question! Based on your health profile, I recommend consulting with your healthcare provider for personalized advice.",
                "I'm here to provide general health guidance. For specific medical concerns, please speak with your doctor.",
                "Your health data looks good overall. Keep up with regular monitoring and healthy lifestyle choices."
            ]
        }
        
    def get_patient_context(self, patient_id):
        """Get recent vitals and patient info for context"""
        try:
            # Get patient info
            patient = Patient.query.get(patient_id)
            if not patient:
                return {}
            
            # Get recent vitals (last 24 hours)
            recent_vitals = VitalSigns.query.filter(
                VitalSigns.patient_id == patient_id,
                VitalSigns.timestamp >= utc_now() - timedelta(hours=24)
            ).order_by(VitalSigns.timestamp.desc()).limit(20).all()
            
            # Calculate averages
            if recent_vitals:
                avg_bp_sys = sum(v.systolic_bp for v in recent_vitals if v.systolic_bp) / len([v for v in recent_vitals if v.systolic_bp])
                avg_bp_dia = sum(v.diastolic_bp for v in recent_vitals if v.diastolic_bp) / len([v for v in recent_vitals if v.diastolic_bp])
                avg_hr = sum(v.heart_rate for v in recent_vitals if v.heart_rate) / len([v for v in recent_vitals if v.heart_rate])
                avg_spo2 = sum(v.spo2 for v in recent_vitals if v.spo2) / len([v for v in recent_vitals if v.spo2])
                total_steps = sum(v.steps for v in recent_vitals if v.steps)
                
                latest_vitals = recent_vitals[0] if recent_vitals else None
            else:
                avg_bp_sys = avg_bp_dia = avg_hr = avg_spo2 = total_steps = 0
                latest_vitals = None
            
            context = {
                'patient_name': patient.first_name,
                'conditions': patient.conditions,
                'latest_vitals': {
                    'blood_pressure': f"{latest_vitals.systolic_bp}/{latest_vitals.diastolic_bp}" if latest_vitals and latest_vitals.systolic_bp else "No data",
                    'heart_rate': latest_vitals.heart_rate if latest_vitals else "No data",
                    'spo2': latest_vitals.spo2 if latest_vitals else "No data",
                    'timestamp': latest_vitals.timestamp.strftime("%Y-%m-%d %H:%M") if latest_vitals else "No data"
                },
                'daily_averages': {
                    'blood_pressure': f"{avg_bp_sys:.0f}/{avg_bp_dia:.0f}" if avg_bp_sys else "No data",
                    'heart_rate': f"{avg_hr:.0f}" if avg_hr else "No data",
                    'spo2': f"{avg_spo2:.1f}%" if avg_spo2 else "No data",
                    'total_steps': int(total_steps)
                },
                'alert_thresholds': {
                    'bp_max': f"{patient.bp_systolic_max}/{patient.bp_diastolic_max}",
                    'hr_range': f"{patient.heart_rate_min}-{patient.heart_rate_max}",
                    'spo2_min': f"{patient.spo2_min}%"
                }
            }
            
            return context
            
        except Exception as e:
            print(f"Error getting patient context: {e}")
            return {}
    
    def generate_response_with_openai(self, patient_id, message, context):
        """Generate AI response using OpenAI"""
        try:
            context_str = f"""
            Patient Information:
            - Name: {context.get('patient_name', 'Patient')}
            - Conditions: {context.get('conditions', 'Not specified')}
            
            Current Vitals:
            - Blood Pressure: {context.get('latest_vitals', {}).get('blood_pressure', 'No data')}
            - Heart Rate: {context.get('latest_vitals', {}).get('heart_rate', 'No data')} bpm
            - Oxygen Saturation: {context.get('latest_vitals', {}).get('spo2', 'No data')}%
            
            Daily Averages:
            - Blood Pressure: {context.get('daily_averages', {}).get('blood_pressure', 'No data')}
            - Heart Rate: {context.get('daily_averages', {}).get('heart_rate', 'No data')} bpm
            - Total Steps: {context.get('daily_averages', {}).get('total_steps', 0)}
            """
            
            system_prompt = """You are a helpful AI health coach. Provide practical health advice based on the patient's vitals. 
            Be encouraging and remind patients to consult healthcare providers for medical decisions."""
            
            response = self.openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "system", "content": f"Patient context: {context_str}"},
                    {"role": "user", "content": message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            return None
    
    def generate_fallback_response(self, message, context):
        """Generate response using rule-based system with web-scraped knowledge"""
        message_lower = message.lower()
        
        # Try to get web-scraped knowledge first for better responses
        web_knowledge = None
        
        # Identify key health topics in the message
        health_topics = ['hypertension', 'blood pressure', 'diabetes', 'diet', 'exercise', 
                        'stress', 'medication', 'heart rate', 'sleep', 'sodium', 'weight']
        
        for topic in health_topics:
            if topic in message_lower or topic.replace(' ', '') in message_lower:
                web_knowledge = scraper.scrape_health_topic(topic, max_length=400)
                if web_knowledge:
                    break
        
        # If we have web-scraped knowledge, use it
        if web_knowledge:
            # Personalize with patient vitals if relevant
            current_bp = context.get('latest_vitals', {}).get('blood_pressure', 'unknown')
            if 'blood pressure' in message_lower and current_bp != 'unknown':
                response = f"Based on current medical guidelines: {web_knowledge}\n\n"
                response += f"Your current blood pressure is {current_bp}. "
                
                if '/' in current_bp:
                    try:
                        sys_bp = int(current_bp.split('/')[0])
                        if sys_bp > 140:
                            response += "This is elevated. Please follow the recommendations above and consult your healthcare provider."
                        elif sys_bp > 130:
                            response += "This is in the Stage 1 hypertension range. The lifestyle changes mentioned above can help."
                        else:
                            response += "This is within normal range. Keep up the good work with your healthy lifestyle!"
                    except:
                        pass
                
                return response
            
            # For other topics, return web knowledge with encouragement
            return f"{web_knowledge}\n\nRemember, I'm here to support you. If you have specific concerns about your condition, please consult with your healthcare provider."
        
        # Fall back to original rule-based responses if no web knowledge found
        # Determine response category
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
            responses = self.responses['greeting']
        elif any(word in message_lower for word in ['blood pressure', 'bp', 'hypertension']):
            responses = self.responses['blood_pressure']
            # Customize with actual data
            current_bp = context.get('latest_vitals', {}).get('blood_pressure', 'unknown')
            avg_bp = context.get('daily_averages', {}).get('blood_pressure', 'unknown')
            
            if current_bp != 'unknown' and '/' in current_bp:
                sys_bp = int(current_bp.split('/')[0])
                if sys_bp > 140:
                    bp_advice = "Consider reducing sodium intake and increasing physical activity."
                    bp_status = "elevated"
                else:
                    bp_advice = "Keep up the good work with your healthy lifestyle."
                    bp_status = "within normal range"
            else:
                bp_advice = "Please ensure regular monitoring."
                bp_status = "being monitored"
                
            response = random.choice(responses).format(
                current_bp=current_bp,
                avg_bp=avg_bp,
                bp_advice=bp_advice,
                bp_status=bp_status
            )
            return response
            
        elif any(word in message_lower for word in ['diet', 'food', 'eat', 'nutrition']):
            responses = self.responses['diet']
        elif any(word in message_lower for word in ['exercise', 'walk', 'activity', 'steps']):
            responses = self.responses['exercise']
            steps = context.get('daily_averages', {}).get('total_steps', 0)
            response = random.choice(responses).format(steps=steps)
            return response
        elif any(word in message_lower for word in ['medication', 'medicine', 'pills']):
            responses = self.responses['medication']
        elif any(word in message_lower for word in ['stress', 'anxiety', 'worried']):
            responses = self.responses['stress']
        else:
            responses = self.responses['default']
        
        return random.choice(responses)
    
    def generate_response(self, patient_id, message, session_id=None):
        """Generate AI response to patient message"""
        try:
            # Get patient context
            context = self.get_patient_context(patient_id)
            
            # Try OpenAI first if available
            ai_response = None
            if self.openai_available:
                ai_response = self.generate_response_with_openai(patient_id, message, context)
            
            # Use fallback if OpenAI failed or not available
            if not ai_response:
                ai_response = self.generate_fallback_response(message, context)
            
            # Save chat message to database
            chat_message = ChatMessage(
                patient_id=patient_id,
                message=message,
                response=ai_response,
                vitals_context=json.dumps(context),
                session_id=session_id
            )
            
            db.session.add(chat_message)
            db.session.commit()
            
            return {
                'success': True,
                'response': ai_response,
                'context_used': context
            }
            
        except Exception as e:
            print(f"Error generating chatbot response: {e}")
            
            # Fallback response
            fallback_response = "I'm sorry, I'm having trouble right now. Please try again in a moment, or contact your healthcare provider if you have urgent concerns."
            
            return {
                'success': False,
                'response': fallback_response,
                'error': str(e)
            }
    
    def get_chat_history(self, patient_id, limit=10):
        """Get recent chat history for a patient"""
        try:
            messages = ChatMessage.query.filter_by(
                patient_id=patient_id
            ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
            
            return [{
                'id': msg.id,
                'message': msg.message,
                'response': msg.response,
                'timestamp': msg.timestamp.isoformat()
            } for msg in reversed(messages)]
            
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
    
    def generate_quick_responses(self, patient_id):
        """Generate quick response suggestions based on current vitals"""
        try:
            context = self.get_patient_context(patient_id)
            latest_vitals = context.get('latest_vitals', {})
            patient = Patient.query.get(patient_id)
            
            suggestions = []
            
            # Check BP
            bp = latest_vitals.get('blood_pressure', '')
            if bp and bp != "No data":
                try:
                    sys_bp = int(bp.split('/')[0]) if '/' in bp else 0
                    if sys_bp > 140:
                        suggestions.append("What can I do about my high blood pressure?")
                    elif sys_bp < 120:
                        suggestions.append("How can I maintain my healthy blood pressure?")
                except:
                    pass
            
            # Check steps
            daily_avg = context.get('daily_averages', {})
            steps = daily_avg.get('total_steps', 0)
            if steps < 5000:
                suggestions.append("How can I increase my daily activity?")
            
            # Condition-specific suggestions
            if patient and patient.conditions:
                conditions_lower = patient.conditions.lower()
                if 'hypertension' in conditions_lower or 'blood pressure' in conditions_lower:
                    suggestions.append("What foods help lower blood pressure?")
                if 'diabetes' in conditions_lower:
                    suggestions.append("How should I manage my blood sugar?")
            
            # General suggestions
            suggestions.extend([
                "What should I eat today?",
                "How can I manage stress better?",
                "Tell me about my health trends this week"
            ])
            
            return suggestions[:4]  # Return top 4 suggestions
            
        except Exception as e:
            print(f"Error generating quick responses: {e}")
            return [
                "What should I eat today?",
                "How can I manage stress better?", 
                "How can I improve my daily activity?",
                "Tell me about my health trends"
            ]
    
    def get_health_tips(self, patient_id, category='general'):
        """Get personalized health tips using web scraper"""
        try:
            patient = Patient.query.get(patient_id)
            if not patient:
                return []
            
            # Determine primary condition
            condition = 'general'
            if patient.conditions:
                conditions_lower = patient.conditions.lower()
                if 'hypertension' in conditions_lower or 'blood pressure' in conditions_lower:
                    condition = 'hypertension'
                elif 'diabetes' in conditions_lower:
                    condition = 'diabetes'
            
            # Get tips from web scraper
            tips = scraper.search_health_tips(condition, category)
            
            return tips
            
        except Exception as e:
            print(f"Error getting health tips: {e}")
            return []

# Global chatbot instance
chatbot = HealthChatbot()