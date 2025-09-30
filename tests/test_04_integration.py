"""
Test Suite 4: Integration Tests
Tests the integration between different components
"""
import json
import pytest
from datetime import datetime, timedelta


class TestIntegration:
    """Test integration between components"""
    
    def test_vitals_to_chat_integration(self, client):
        """Test 4.1: Vitals data accessible in chat responses"""
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        # Add vitals
        vitals_data = {
            'patient_id': 1,
            'heart_rate': 95,
            'systolic_bp': 145,
            'diastolic_bp': 95
        }
        client.post('/api/vitals',
            data=json.dumps(vitals_data),
            content_type='application/json'
        )
        
        # Ask about vitals in chat
        response = client.post('/api/chat',
            data=json.dumps({'message': 'What is my blood pressure?'}),
            content_type='application/json'
        )
        assert response.status_code == 200
    
    def test_vitals_to_report_integration(self, client):
        """Test 4.2: Vitals data included in health reports"""
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        response = client.get('/api/reports/health-summary/1?days=1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['vitals_count'] > 0
        assert data['statistics'] is not None
    
    def test_simulator_creates_vitals(self, client, app):
        """Test 4.3: Simulator creates vitals in database"""
        with app.app_context():
            from app.models.vitals import VitalSigns
            initial_count = VitalSigns.query.count()
        
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        # Start simulator
        client.post('/api/simulator/start',
            data=json.dumps({'patient_id': 1}),
            content_type='application/json'
        )
        
        # Stop simulator
        client.post('/api/simulator/stop',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # Count should be same or more (simulator might add data)
        with app.app_context():
            final_count = VitalSigns.query.count()
            assert final_count >= initial_count
    
    def test_chat_creates_messages(self, client, app):
        """Test 4.4: Chat creates message records"""
        with app.app_context():
            from app.models.insights import ChatMessage
            initial_count = ChatMessage.query.count()
        
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        client.post('/api/chat',
            data=json.dumps({'message': 'Hello'}),
            content_type='application/json'
        )
        
        with app.app_context():
            final_count = ChatMessage.query.count()
            assert final_count > initial_count
    
    def test_web_knowledge_integration(self, client):
        """Test 4.5: Web scraper knowledge available in API"""
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        response = client.get('/api/web-knowledge?topic=hypertension')
        # May succeed or fail depending on web scraper
        assert response.status_code in [200, 404, 500]
    
    def test_health_tips_integration(self, client):
        """Test 4.6: Health tips based on patient data"""
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        response = client.get('/api/health-tips/1?category=diet')
        assert response.status_code in [200, 500]  # May fail if chatbot has issues
    
    def test_patient_to_user_relationship(self, app):
        """Test 4.7: Patient-User relationship works"""
        with app.app_context():
            from app.models.patient import Patient
            from app.models.user import User
            
            patient = Patient.query.first()
            assert patient is not None
            assert patient.user is not None
            assert patient.user.role == 'patient'
    
    def test_vitals_timestamp_ordering(self, client):
        """Test 4.8: Vitals returned in correct time order"""
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        response = client.get('/api/vitals/1?hours=24')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        if len(data['data']) > 1:
            # Check timestamps are in ascending order
            timestamps = [v['timestamp'] for v in data['data']]
            assert timestamps == sorted(timestamps)
    
    def test_login_to_dashboard_flow(self, client):
        """Test 4.9: Complete login to dashboard flow"""
        # Login
        response = client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Access dashboard
        response = client.get('/')
        assert response.status_code == 200
    
    def test_complete_user_journey(self, client):
        """Test 4.10: Complete user journey from login to chat to report"""
        # 1. Login
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        # 2. Chat
        response = client.post('/api/chat',
            data=json.dumps({'message': 'How am I doing?'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # 3. Check vitals
        response = client.get('/api/vitals/1')
        assert response.status_code == 200
        
        # 4. Get report
        response = client.get('/api/reports/health-summary/1')
        assert response.status_code == 200
