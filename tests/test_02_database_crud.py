"""
Test Suite 2: Database CRUD Operations
Tests all database Create, Read, Update, Delete operations
"""
import pytest
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.patient import Patient
from app.models.vitals import VitalSigns
from app.models.insights import PatientInsight, ChatMessage
from werkzeug.security import generate_password_hash


class TestDatabaseCRUD:
    """Test database CRUD operations"""
    
    def test_create_user(self, app):
        """Test 2.1: Create new user"""
        with app.app_context():
            user = User(
                username='newuser',
                email='newuser@test.com',
                password_hash=generate_password_hash('password'),
                role='patient'
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'newuser'
    
    def test_read_user(self, app):
        """Test 2.2: Read user from database"""
        with app.app_context():
            user = User.query.filter_by(username='testpatient').first()
            assert user is not None
            assert user.email == 'patient@test.com'
            assert user.role == 'patient'
    
    def test_update_user(self, app):
        """Test 2.3: Update user information"""
        with app.app_context():
            user = User.query.filter_by(username='testpatient').first()
            user.email = 'updated@test.com'
            db.session.commit()
            
            updated_user = User.query.filter_by(username='testpatient').first()
            assert updated_user.email == 'updated@test.com'
    
    def test_delete_vitals(self, app):
        """Test 2.4: Delete vitals record"""
        with app.app_context():
            vitals = VitalSigns.query.first()
            vitals_id = vitals.id
            db.session.delete(vitals)
            db.session.commit()
            
            deleted = VitalSigns.query.get(vitals_id)
            assert deleted is None
    
    def test_create_patient(self, app):
        """Test 2.5: Create patient profile"""
        with app.app_context():
            user = User(
                username='newpatient',
                email='newpatient@test.com',
                password_hash=generate_password_hash('password'),
                role='patient'
            )
            db.session.add(user)
            db.session.commit()
            
            patient = Patient(
                user_id=user.id,
                first_name='New',
                last_name='Patient',
                date_of_birth=datetime(1990, 1, 1).date(),
                gender='female'
            )
            db.session.add(patient)
            db.session.commit()
            
            assert patient.id is not None
            assert patient.first_name == 'New'
    
    def test_read_vitals(self, app):
        """Test 2.6: Read vitals from database"""
        with app.app_context():
            vitals = VitalSigns.query.filter_by(patient_id=1).all()
            assert len(vitals) > 0
            assert vitals[0].heart_rate is not None
    
    def test_update_patient(self, app):
        """Test 2.7: Update patient information"""
        with app.app_context():
            patient = Patient.query.filter_by(id=1).first()
            patient.phone = '+1-555-9999'
            db.session.commit()
            
            updated = Patient.query.get(1)
            assert updated.phone == '+1-555-9999'
    
    def test_create_vitals(self, app):
        """Test 2.8: Create new vitals record"""
        with app.app_context():
            vitals = VitalSigns(
                patient_id=1,
                heart_rate=80,
                systolic_bp=125,
                diastolic_bp=85,
                spo2=98.5,
                temperature=98.6,
                timestamp=datetime.utcnow()
            )
            db.session.add(vitals)
            db.session.commit()
            
            assert vitals.id is not None
    
    def test_create_insight(self, app):
        """Test 2.9: Create patient insight"""
        with app.app_context():
            insight = PatientInsight(
                patient_id=1,
                title='Test Insight',
                content='This is a test insight',
                insight_type='daily',
                severity='info'
            )
            db.session.add(insight)
            db.session.commit()
            
            assert insight.id is not None
            assert insight.title == 'Test Insight'
    
    def test_create_chat_message(self, app):
        """Test 2.10: Create chat message"""
        with app.app_context():
            message = ChatMessage(
                patient_id=1,
                role='user',
                content='Test message',
                session_id='test-session'
            )
            db.session.add(message)
            db.session.commit()
            
            assert message.id is not None
            assert message.content == 'Test message'
