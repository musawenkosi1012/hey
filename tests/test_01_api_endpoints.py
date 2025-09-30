"""
Test Suite 1: API Endpoint Tests (GET, POST, PUT, DELETE)
Tests all REST API endpoints with various HTTP methods
"""
import json
import pytest
from datetime import datetime


class TestAPIEndpoints:
    """Test all API endpoints with different HTTP methods"""
    
    def test_health_check_endpoint(self, client):
        """Test 1.1: Health check endpoint (GET)"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'ChroniSense API'
        assert data['database'] == 'connected'
    
    def test_get_vitals_unauthenticated(self, client):
        """Test 1.2: GET vitals without authentication should fail"""
        response = client.get('/api/vitals/1')
        assert response.status_code == 401 or response.status_code == 302
    
    def test_get_vitals_authenticated(self, client):
        """Test 1.3: GET vitals with authentication"""
        # Login first
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        response = client.get('/api/vitals/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
    
    def test_post_vitals_ingestion(self, client):
        """Test 1.4: POST vitals data ingestion"""
        vitals_data = {
            'patient_id': 1,
            'heart_rate': 75,
            'systolic_bp': 120,
            'diastolic_bp': 80,
            'spo2': 98.0,
            'temperature': 98.6
        }
        
        response = client.post('/api/vitals',
            data=json.dumps(vitals_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'id' in data
    
    def test_post_vitals_missing_fields(self, client):
        """Test 1.5: POST vitals with missing required fields"""
        incomplete_data = {
            'patient_id': 1,
            'heart_rate': 75
            # Missing systolic_bp and diastolic_bp
        }
        
        response = client.post('/api/vitals',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_chat_endpoint_post(self, client):
        """Test 1.6: POST to chat endpoint"""
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        chat_data = {
            'message': 'Hello, how is my health?'
        }
        
        response = client.post('/api/chat',
            data=json.dumps(chat_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'response' in data
    
    def test_chat_history_get(self, client):
        """Test 1.7: GET chat history"""
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        response = client.get('/api/chat/history')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'history' in data
    
    def test_simulator_start_post(self, client):
        """Test 1.8: POST to start simulator"""
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        response = client.post('/api/simulator/start',
            data=json.dumps({'patient_id': 1}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_simulator_stop_post(self, client):
        """Test 1.9: POST to stop simulator"""
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        response = client.post('/api/simulator/stop',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_health_summary_report_get(self, client):
        """Test 1.10: GET health summary report"""
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        response = client.get('/api/reports/health-summary/1?days=7')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'patient' in data
        assert 'statistics' in data
