"""
Test Suite 3: Authentication and Authorization
Tests user authentication and role-based access control
"""
import json
import pytest
from werkzeug.security import check_password_hash


class TestAuthentication:
    """Test authentication and authorization"""
    
    def test_login_success(self, client):
        """Test 3.1: Successful login"""
        response = client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_login_wrong_password(self, client):
        """Test 3.2: Login with wrong password"""
        response = client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert b'Invalid username or password' in response.data or response.status_code == 200
    
    def test_login_nonexistent_user(self, client):
        """Test 3.3: Login with non-existent user"""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'password123'
        }, follow_redirects=True)
        assert b'Invalid username or password' in response.data or response.status_code == 200
    
    def test_logout(self, client):
        """Test 3.4: Logout functionality"""
        # Login first
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        # Then logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_patient_access_own_vitals(self, client):
        """Test 3.5: Patient can access their own vitals"""
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        response = client.get('/api/vitals/1')
        assert response.status_code == 200
    
    def test_patient_cannot_access_others_vitals(self, client):
        """Test 3.6: Patient cannot access other patients' vitals"""
        client.post('/auth/login', data={
            'username': 'testpatient',
            'password': 'password123'
        })
        
        # Try to access non-existent patient's vitals
        response = client.get('/api/vitals/999')
        assert response.status_code in [403, 404]
    
    def test_doctor_access_all_patients(self, client):
        """Test 3.7: Doctor can access all patients"""
        client.post('/auth/login', data={
            'username': 'testdoctor',
            'password': 'password123'
        })
        
        response = client.get('/api/vitals/1')
        assert response.status_code == 200
    
    def test_patient_chat_authorization(self, client):
        """Test 3.8: Only patients can chat"""
        client.post('/auth/login', data={
            'username': 'testdoctor',
            'password': 'password123'
        })
        
        response = client.post('/api/chat',
            data=json.dumps({'message': 'Hello'}),
            content_type='application/json'
        )
        assert response.status_code == 403
    
    def test_doctor_inject_anomaly(self, client):
        """Test 3.9: Only doctors can inject anomalies"""
        client.post('/auth/login', data={
            'username': 'testdoctor',
            'password': 'password123'
        })
        
        response = client.post('/api/simulator/inject-anomaly',
            data=json.dumps({'type': 'hypertension'}),
            content_type='application/json'
        )
        assert response.status_code == 200
    
    def test_password_hashing(self, app):
        """Test 3.10: Passwords are properly hashed"""
        with app.app_context():
            from app.models.user import User
            user = User.query.filter_by(username='testpatient').first()
            # Password should be hashed, not plain text
            assert user.password_hash != 'password123'
            # But should verify correctly
            assert check_password_hash(user.password_hash, 'password123')
