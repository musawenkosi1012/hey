from app import db
from datetime import datetime

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    emergency_contact = db.Column(db.String(100), nullable=True)
    
    # Medical Information
    conditions = db.Column(db.Text, nullable=True)  # JSON string of conditions
    medications = db.Column(db.Text, nullable=True)  # JSON string of medications
    allergies = db.Column(db.Text, nullable=True)
    
    # Thresholds for alerts
    bp_systolic_max = db.Column(db.Integer, default=140)
    bp_diastolic_max = db.Column(db.Integer, default=90)
    heart_rate_min = db.Column(db.Integer, default=60)
    heart_rate_max = db.Column(db.Integer, default=100)
    spo2_min = db.Column(db.Integer, default=95)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vitals = db.relationship('VitalSigns', backref='patient', lazy=True)
    insights = db.relationship('PatientInsight', backref='patient', lazy=True)
    
    def __repr__(self):
        return f'<Patient {self.first_name} {self.last_name}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"