#!/usr/bin/env python3
"""
Database initialization script for ChroniSense
Creates tables and sample data for testing
"""

from app import create_app, db
from app.models.user import User
from app.models.patient import Patient
from app.models.vitals import VitalSigns, RiskPrediction
from app.models.insights import PatientInsight, ChatMessage
from werkzeug.security import generate_password_hash
from datetime import date, datetime, timedelta
import random

def create_sample_data():
    """Create sample users and data for testing"""
    
    # Create sample users
    users_data = [
        {
            'username': 'patient',
            'email': 'patient@chronisense.com',
            'password': 'password123',
            'role': 'patient'
        },
        {
            'username': 'doctor',
            'email': 'doctor@chronisense.com', 
            'password': 'password123',
            'role': 'doctor'
        },
        {
            'username': 'caregiver',
            'email': 'caregiver@chronisense.com',
            'password': 'password123', 
            'role': 'caregiver'
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=generate_password_hash(user_data['password']),
            role=user_data['role']
        )
        users.append(user)
        db.session.add(user)
    
    db.session.commit()
    
    # Create patient profile for the patient user
    patient_user = User.query.filter_by(username='patient').first()
    if patient_user:
        patient = Patient(
            user_id=patient_user.id,
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1975, 5, 15),
            gender='male',
            phone='+1-555-0123',
            emergency_contact='Jane Doe - +1-555-0124',
            conditions='{"hypertension": true, "diabetes": true}',
            medications='{"lisinopril": "10mg daily", "metformin": "500mg twice daily"}',
            allergies='{"penicillin": "mild rash"}',
            bp_systolic_max=140,
            bp_diastolic_max=90,
            heart_rate_min=60,
            heart_rate_max=100,
            spo2_min=95
        )
        db.session.add(patient)
        db.session.commit()
        
        # Create sample vitals data (last 7 days)
        create_sample_vitals(patient.id)
        
        # Create sample insights
        create_sample_insights(patient.id)
    
    print("✅ Sample data created successfully!")
    print("\nDemo login credentials:")
    print("Patient: username=patient, password=password123")
    print("Doctor: username=doctor, password=password123")
    print("Caregiver: username=caregiver, password=password123")

def create_sample_vitals(patient_id):
    """Create sample vitals data for the last 7 days"""
    
    base_vitals = {
        'heart_rate': 75,
        'systolic_bp': 125,
        'diastolic_bp': 82,
        'spo2': 97.5,
        'temperature': 98.6
    }
    
    start_date = datetime.utcnow() - timedelta(days=7)
    
    for day in range(7):
        for hour in range(0, 24, 2):  # Every 2 hours
            timestamp = start_date + timedelta(days=day, hours=hour)
            
            # Add some realistic variation
            variation = random.uniform(0.8, 1.2)
            time_factor = 1.1 if 6 <= hour <= 18 else 0.9  # Higher during day
            
            vitals = VitalSigns(
                patient_id=patient_id,
                heart_rate=int(base_vitals['heart_rate'] * variation * time_factor + random.randint(-10, 15)),
                systolic_bp=int(base_vitals['systolic_bp'] * variation + random.randint(-15, 20)),
                diastolic_bp=int(base_vitals['diastolic_bp'] * variation + random.randint(-10, 15)),
                spo2=round(base_vitals['spo2'] * variation + random.uniform(-2, 1), 1),
                temperature=round(base_vitals['temperature'] + random.uniform(-1, 1), 1),
                steps=random.randint(0, 500) if hour >= 6 and hour <= 22 else 0,
                calories_burned=random.randint(0, 50),
                timestamp=timestamp,
                source='simulator'
            )
            
            # Occasionally add anomalies
            if random.random() < 0.02:  # 2% chance
                vitals.is_anomaly = True
                vitals.systolic_bp += 30
                vitals.heart_rate += 25
            
            db.session.add(vitals)
    
    db.session.commit()
    print(f"✅ Created sample vitals data for patient {patient_id}")

def create_sample_insights(patient_id):
    """Create sample insights for the patient"""
    
    insights_data = [
        {
            'title': 'Weekly Health Summary',
            'content': 'Your blood pressure has been averaging 125/82 this week, which is within healthy ranges. Your heart rate shows good variability between rest and activity. Consider increasing your daily steps from 4,200 to 6,000 for optimal cardiovascular health.',
            'insight_type': 'weekly',
            'severity': 'info',
            'period_start': datetime.utcnow() - timedelta(days=7),
            'period_end': datetime.utcnow()
        },
        {
            'title': 'Daily Activity Reminder',
            'content': 'You completed 3,800 steps today, which is below your target of 6,000. Try taking a 20-minute walk after dinner to reach your goal.',
            'insight_type': 'daily',
            'severity': 'info',
            'period_start': datetime.utcnow() - timedelta(days=1),
            'period_end': datetime.utcnow()
        },
        {
            'title': 'Blood Pressure Trend Alert',
            'content': 'Your blood pressure readings have been slightly elevated over the past 2 days (averaging 138/88). Consider reducing sodium intake and increasing hydration.',
            'insight_type': 'alert',
            'severity': 'warning',
            'period_start': datetime.utcnow() - timedelta(days=2),
            'period_end': datetime.utcnow()
        }
    ]
    
    for insight_data in insights_data:
        insight = PatientInsight(
            patient_id=patient_id,
            title=insight_data['title'],
            content=insight_data['content'],
            insight_type=insight_data['insight_type'],
            severity=insight_data['severity'],
            period_start=insight_data['period_start'],
            period_end=insight_data['period_end']
        )
        db.session.add(insight)
    
    db.session.commit()
    print(f"✅ Created sample insights for patient {patient_id}")

def init_database():
    """Initialize database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Initializing ChroniSense database...")
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created")
        
        # Check if data already exists
        if User.query.first():
            print("ℹ️  Sample data already exists, skipping creation")
            return
        
        # Create sample data
        create_sample_data()
        
        print("🎉 Database initialization complete!")

if __name__ == '__main__':
    init_database()