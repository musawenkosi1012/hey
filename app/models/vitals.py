from app import db
from datetime import datetime
import json

class VitalSigns(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    
    # Vital measurements
    heart_rate = db.Column(db.Integer, nullable=True)
    systolic_bp = db.Column(db.Integer, nullable=True)
    diastolic_bp = db.Column(db.Integer, nullable=True)
    spo2 = db.Column(db.Float, nullable=True)  # Oxygen saturation
    temperature = db.Column(db.Float, nullable=True)  # Body temperature
    
    # Activity data
    steps = db.Column(db.Integer, default=0)
    calories_burned = db.Column(db.Integer, default=0)
    
    # Sleep data
    sleep_hours = db.Column(db.Float, nullable=True)
    sleep_quality = db.Column(db.String(20), nullable=True)  # poor, fair, good, excellent
    
    # Metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    source = db.Column(db.String(50), default='simulator')  # simulator, device, manual
    is_anomaly = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<VitalSigns Patient:{self.patient_id} Time:{self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'heart_rate': self.heart_rate,
            'systolic_bp': self.systolic_bp,
            'diastolic_bp': self.diastolic_bp,
            'spo2': self.spo2,
            'temperature': self.temperature,
            'steps': self.steps,
            'calories_burned': self.calories_burned,
            'sleep_hours': self.sleep_hours,
            'sleep_quality': self.sleep_quality,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'is_anomaly': self.is_anomaly
        }

class RiskPrediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    
    # Risk scores (0-100)
    risk_6h = db.Column(db.Float, nullable=False)
    risk_24h = db.Column(db.Float, nullable=False)
    risk_72h = db.Column(db.Float, nullable=False)
    
    # Risk factors (JSON)
    risk_factors = db.Column(db.Text, nullable=True)
    recommendations = db.Column(db.Text, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    model_version = db.Column(db.String(20), default='v1.0')
    
    def __repr__(self):
        return f'<RiskPrediction Patient:{self.patient_id} 24h:{self.risk_24h}%>'