import random
import time
import json
from datetime import datetime, timedelta, timezone
from threading import Thread
from app import db, socketio
from app.models.vitals import VitalSigns
from app.models.patient import Patient
import requests

# Helper function for naive UTC datetime (for DB compatibility)
def utc_now():
    return datetime.utcnow()

class VitalsSimulator:
    def __init__(self):
        self.running = False
        self.base_vitals = {
            'heart_rate': 75,
            'systolic_bp': 120,
            'diastolic_bp': 80,
            'spo2': 98.0,
            'temperature': 98.6
        }
        
    def start_simulation(self, patient_id=1):
        """Start continuous vitals simulation for a patient"""
        self.running = True
        self.patient_id = patient_id
        
        def simulate():
            while self.running:
                try:
                    vitals = self.generate_realistic_vitals()
                    self.save_vitals(vitals)
                    self.emit_realtime_data(vitals)
                    
                    # Sleep for 30 seconds (simulate data every 30s)
                    time.sleep(30)
                except Exception as e:
                    print(f"Simulation error: {e}")
                    time.sleep(5)
        
        thread = Thread(target=simulate)
        thread.daemon = True
        thread.start()
        
    def generate_realistic_vitals(self):
        """Generate realistic vital signs with some variation"""
        current_time = utc_now()
        hour = current_time.hour
        
        # Simulate circadian rhythm effects
        if 6 <= hour <= 18:  # Daytime
            activity_factor = 1.2
        else:  # Nighttime
            activity_factor = 0.8
            
        # Add some random variation
        vitals = {
            'heart_rate': int(self.base_vitals['heart_rate'] * activity_factor + random.randint(-10, 15)),
            'systolic_bp': int(self.base_vitals['systolic_bp'] + random.randint(-15, 20)),
            'diastolic_bp': int(self.base_vitals['diastolic_bp'] + random.randint(-10, 15)),
            'spo2': round(self.base_vitals['spo2'] + random.uniform(-2, 1), 1),
            'temperature': round(self.base_vitals['temperature'] + random.uniform(-1, 1), 1),
            'steps': random.randint(0, 100) if hour >= 6 and hour <= 22 else 0,
            'calories_burned': random.randint(0, 50),
            'timestamp': current_time
        }
        
        # Occasionally simulate anomalies
        if random.random() < 0.05:  # 5% chance of anomaly
            vitals['is_anomaly'] = True
            vitals['systolic_bp'] += random.randint(30, 50)
            vitals['heart_rate'] += random.randint(20, 40)
        else:
            vitals['is_anomaly'] = False
            
        return vitals
    
    def save_vitals(self, vitals_data):
        """Save vitals to database"""
        try:
            vitals = VitalSigns(
                patient_id=self.patient_id,
                heart_rate=vitals_data['heart_rate'],
                systolic_bp=vitals_data['systolic_bp'],
                diastolic_bp=vitals_data['diastolic_bp'],
                spo2=vitals_data['spo2'],
                temperature=vitals_data['temperature'],
                steps=vitals_data['steps'],
                calories_burned=vitals_data['calories_burned'],
                timestamp=vitals_data['timestamp'],
                is_anomaly=vitals_data.get('is_anomaly', False),
                source='simulator'
            )
            
            db.session.add(vitals)
            db.session.commit()
            
        except Exception as e:
            print(f"Error saving vitals: {e}")
            db.session.rollback()
    
    def emit_realtime_data(self, vitals_data):
        """Emit real-time data via WebSocket"""
        try:
            data = {
                'patient_id': self.patient_id,
                'vitals': vitals_data,
                'timestamp': vitals_data['timestamp'].isoformat()
            }
            socketio.emit('vitals_update', data, namespace='/realtime')
            
            # Check for alerts
            if self.check_alert_conditions(vitals_data):
                alert_data = {
                    'patient_id': self.patient_id,
                    'alert_type': 'critical_vitals',
                    'message': self.generate_alert_message(vitals_data),
                    'vitals': vitals_data,
                    'timestamp': vitals_data['timestamp'].isoformat()
                }
                socketio.emit('critical_alert', alert_data, namespace='/alerts')
                
        except Exception as e:
            print(f"Error emitting real-time data: {e}")
    
    def check_alert_conditions(self, vitals):
        """Check if vitals trigger any alerts"""
        # Basic alert conditions
        if (vitals['systolic_bp'] > 180 or 
            vitals['diastolic_bp'] > 110 or
            vitals['heart_rate'] > 120 or
            vitals['heart_rate'] < 50 or
            vitals['spo2'] < 90):
            return True
        return False
    
    def generate_alert_message(self, vitals):
        """Generate human-readable alert message"""
        alerts = []
        
        if vitals['systolic_bp'] > 180:
            alerts.append(f"High blood pressure: {vitals['systolic_bp']}/{vitals['diastolic_bp']}")
        if vitals['heart_rate'] > 120:
            alerts.append(f"High heart rate: {vitals['heart_rate']} bpm")
        if vitals['heart_rate'] < 50:
            alerts.append(f"Low heart rate: {vitals['heart_rate']} bpm")
        if vitals['spo2'] < 90:
            alerts.append(f"Low oxygen saturation: {vitals['spo2']}%")
            
        return "; ".join(alerts)
    
    def inject_anomaly(self, anomaly_type="hypertension"):
        """Manually inject an anomaly for testing"""
        if anomaly_type == "hypertension":
            self.base_vitals['systolic_bp'] = 190
            self.base_vitals['diastolic_bp'] = 110
        elif anomaly_type == "tachycardia":
            self.base_vitals['heart_rate'] = 130
        elif anomaly_type == "hypoxia":
            self.base_vitals['spo2'] = 85
            
        # Reset after 5 minutes
        def reset_vitals():
            time.sleep(300)  # 5 minutes
            self.base_vitals = {
                'heart_rate': 75,
                'systolic_bp': 120,
                'diastolic_bp': 80,
                'spo2': 98.0,
                'temperature': 98.6
            }
            
        Thread(target=reset_vitals, daemon=True).start()
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False

# Global simulator instance
simulator = VitalsSimulator()