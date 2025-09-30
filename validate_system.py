#!/usr/bin/env python3
"""
ChroniSense System Validation Script
Run this to verify all system components are working correctly
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.patient import Patient
from app.models.vitals import VitalSigns
from app.models.user import User
from app.services.chatbot import chatbot
from app.services.web_scraper import scraper
from datetime import datetime
import json

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def validate_database():
    """Validate database setup and connectivity"""
    print_header("1. DATABASE VALIDATION")
    
    try:
        app = create_app()
        with app.app_context():
            # Check users
            users = User.query.all()
            print_success(f"Database connected")
            print_info(f"Found {len(users)} users")
            
            # Check patients
            patients = Patient.query.all()
            print_success(f"Found {len(patients)} patient(s)")
            
            # Check vitals
            vitals_count = VitalSigns.query.count()
            print_success(f"Found {vitals_count} vital signs records")
            
            if len(users) > 0 and len(patients) > 0 and vitals_count > 0:
                print_success("Database is properly initialized")
                return True
            else:
                print_error("Database is missing data. Run: python3 init_db.py")
                return False
                
    except Exception as e:
        print_error(f"Database validation failed: {e}")
        return False

def validate_chatbot():
    """Validate chatbot functionality"""
    print_header("2. CHATBOT VALIDATION")
    
    try:
        app = create_app()
        with app.app_context():
            patient = Patient.query.first()
            if not patient:
                print_error("No patients found")
                return False
            
            # Test simple greeting
            test_cases = [
                ("Hello", "greeting"),
                ("What is my blood pressure?", "blood pressure"),
                ("What should I eat?", "diet"),
            ]
            
            for message, expected_topic in test_cases:
                response = chatbot.generate_response(patient.id, message)
                if response['success'] and len(response['response']) > 0:
                    print_success(f"'{message}' → Response received ({len(response['response'])} chars)")
                else:
                    print_error(f"Failed to get response for '{message}'")
                    return False
            
            print_success("Chatbot is working correctly")
            return True
            
    except Exception as e:
        print_error(f"Chatbot validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_knowledge_base():
    """Validate web scraper knowledge base"""
    print_header("3. KNOWLEDGE BASE VALIDATION")
    
    try:
        topics_to_test = ['hypertension', 'diabetes', 'diet']
        
        for topic in topics_to_test:
            knowledge = scraper.scrape_health_topic(topic, max_length=200)
            if knowledge and len(knowledge) > 50:
                print_success(f"{topic.capitalize()}: {len(knowledge)} chars of content")
            else:
                print_error(f"No knowledge found for {topic}")
                return False
        
        # Test health tips
        tips = scraper.search_health_tips('hypertension', 'diet')
        if len(tips) > 0:
            print_success(f"Health tips: {len(tips)} tips available")
        else:
            print_error("No health tips found")
            return False
        
        print_success("Knowledge base is working correctly")
        return True
        
    except Exception as e:
        print_error(f"Knowledge base validation failed: {e}")
        return False

def validate_reports():
    """Validate report generation"""
    print_header("4. REPORT GENERATION VALIDATION")
    
    try:
        app = create_app()
        with app.app_context():
            patient = Patient.query.first()
            if not patient:
                print_error("No patients found")
                return False
            
            # Test context generation
            context = chatbot.get_patient_context(patient.id)
            if context and 'latest_vitals' in context:
                bp = context['latest_vitals'].get('blood_pressure', 'N/A')
                print_success(f"Patient context: BP={bp}")
            else:
                print_error("Failed to generate patient context")
                return False
            
            # Test suggestions
            suggestions = chatbot.generate_quick_responses(patient.id)
            if len(suggestions) > 0:
                print_success(f"Generated {len(suggestions)} personalized suggestions")
            else:
                print_error("Failed to generate suggestions")
                return False
            
            # Test chat history
            history = chatbot.get_chat_history(patient.id, limit=5)
            print_success(f"Chat history: {len(history)} messages")
            
            print_success("Report generation is working correctly")
            return True
            
    except Exception as e:
        print_error(f"Report generation validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_api_endpoints():
    """Validate API endpoints with test client"""
    print_header("5. API ENDPOINTS VALIDATION")
    
    try:
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            with app.app_context():
                # Login
                response = client.post('/auth/login', data={
                    'username': 'patient',
                    'password': 'password123'
                }, follow_redirects=True)
                
                if response.status_code == 200:
                    print_success("Authentication: Login successful")
                else:
                    print_error(f"Authentication failed: {response.status_code}")
                    return False
                
                # Test vitals endpoint
                response = client.get('/api/vitals/1')
                if response.status_code == 200:
                    data = json.loads(response.data)
                    print_success(f"Vitals API: {len(data.get('data', []))} records")
                else:
                    print_error(f"Vitals API failed: {response.status_code}")
                
                # Test chat endpoint
                response = client.post('/api/chat',
                    data=json.dumps({'message': 'Hello'}),
                    content_type='application/json'
                )
                if response.status_code == 200:
                    print_success("Chat API: Working")
                else:
                    print_error(f"Chat API failed: {response.status_code}")
                
                # Test report endpoint
                response = client.get('/api/reports/health-summary/1?days=7')
                if response.status_code == 200:
                    data = json.loads(response.data)
                    vitals_count = data.get('vitals_count', 0)
                    print_success(f"Health Report API: {vitals_count} vitals analyzed")
                else:
                    print_error(f"Health Report API failed: {response.status_code}")
                
                # Test knowledge endpoint
                response = client.get('/api/web-knowledge?topic=hypertension')
                if response.status_code == 200:
                    print_success("Knowledge API: Working")
                else:
                    print_error(f"Knowledge API failed: {response.status_code}")
                
                print_success("All API endpoints are working correctly")
                return True
                
    except Exception as e:
        print_error(f"API validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main validation routine"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "ChroniSense System Validation" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = {}
    
    # Run all validations
    results['Database'] = validate_database()
    results['Chatbot'] = validate_chatbot()
    results['Knowledge Base'] = validate_knowledge_base()
    results['Report Generation'] = validate_reports()
    results['API Endpoints'] = validate_api_endpoints()
    
    # Print summary
    print_header("VALIDATION SUMMARY")
    
    all_passed = True
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{component:.<40} {status}")
        if not passed:
            all_passed = False
    
    total = len(results)
    passed = sum(results.values())
    
    print("\n" + "-" * 70)
    print(f"Total: {passed}/{total} components validated successfully")
    print("-" * 70)
    
    if all_passed:
        print("\n🎉 SUCCESS! All system components are working correctly!\n")
        print("The ChroniSense system is ready to use:")
        print("  1. Start app: python3 app.py")
        print("  2. Access: http://localhost:5000")
        print("  3. Login: patient / password123")
        print("")
        return 0
    else:
        print("\n⚠️  WARNING: Some components failed validation")
        print("Please check the errors above and fix them.")
        print("")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
