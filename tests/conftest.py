"""
Test configuration and fixtures
"""
import pytest
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.patient import Patient
from app.models.vitals import VitalSigns
from app.models.insights import PatientInsight, ChatMessage
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        _create_test_data()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()


def _create_test_data():
    """Create test data for all tests"""
    # Create test users
    patient_user = User(
        username='testpatient',
        email='patient@test.com',
        password_hash=generate_password_hash('password123'),
        role='patient'
    )
    doctor_user = User(
        username='testdoctor',
        email='doctor@test.com',
        password_hash=generate_password_hash('password123'),
        role='doctor'
    )
    caregiver_user = User(
        username='testcaregiver',
        email='caregiver@test.com',
        password_hash=generate_password_hash('password123'),
        role='caregiver'
    )
    
    db.session.add_all([patient_user, doctor_user, caregiver_user])
    db.session.commit()
    
    # Create test patient profile
    patient = Patient(
        user_id=patient_user.id,
        first_name='Test',
        last_name='Patient',
        date_of_birth=datetime(1980, 1, 1).date(),
        gender='male',
        phone='+1-555-0100',
        emergency_contact='Emergency Contact - +1-555-0101',
        conditions='{"hypertension": true}',
        medications='{"lisinopril": "10mg daily"}',
        allergies='{}',
        bp_systolic_max=140,
        bp_diastolic_max=90,
        heart_rate_min=60,
        heart_rate_max=100,
        spo2_min=95
    )
    db.session.add(patient)
    db.session.commit()
    
    # Create test vitals
    for i in range(10):
        vitals = VitalSigns(
            patient_id=patient.id,
            heart_rate=75 + i,
            systolic_bp=120 + i,
            diastolic_bp=80 + i,
            spo2=97.0 + i * 0.1,
            temperature=98.6,
            steps=1000 * i,
            calories_burned=50 * i,
            timestamp=datetime.utcnow() - timedelta(hours=i),
            source='test'
        )
        db.session.add(vitals)
    
    db.session.commit()


@pytest.fixture
def auth_headers(client):
    """Get authentication headers for API tests"""
    # Login as patient
    response = client.post('/auth/login', data={
        'username': 'testpatient',
        'password': 'password123'
    }, follow_redirects=True)
    
    return {}  # Cookies are handled by the client automatically
