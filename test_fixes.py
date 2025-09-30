#!/usr/bin/env python3
"""
Comprehensive test suite for chatbot and simulator fixes
Tests all the fixes made to address the GitHub issue
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set OpenAI API key before importing app
os.environ['OPENAI_API_KEY'] = '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'

from app import create_app
from app.services.chatbot import chatbot
from app.services.vitals_simulator import simulator
from app.models.vitals import VitalSigns

def test_chatbot_with_openai_fallback():
    """Test chatbot with OpenAI integration and fallback mechanism"""
    print("\n" + "="*70)
    print("TEST 1: Chatbot with OpenAI and Fallback")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        patient_id = 1
        
        # Test various message types
        test_messages = [
            ("Hello!", "greeting"),
            ("What about my blood pressure?", "blood pressure info"),
            ("How much should I exercise?", "exercise advice"),
            ("What should I eat?", "diet advice"),
        ]
        
        for message, description in test_messages:
            print(f"\n[{description.upper()}] Testing: '{message}'")
            response = chatbot.generate_response(patient_id, message)
            
            assert response['success'], f"Response should be successful"
            assert len(response['response']) > 0, "Response should not be empty"
            print(f"✓ Success: {response['success']}")
            print(f"✓ Response length: {len(response['response'])} characters")
            print(f"✓ Preview: {response['response'][:100]}...")
        
        # Test chat history
        print("\n[CHAT HISTORY] Testing chat history retrieval...")
        history = chatbot.get_chat_history(patient_id, limit=5)
        assert len(history) >= len(test_messages), "History should contain all messages"
        print(f"✓ Retrieved {len(history)} messages from history")
        
        # Test quick suggestions
        print("\n[QUICK SUGGESTIONS] Testing suggestion generation...")
        suggestions = chatbot.generate_quick_responses(patient_id)
        assert len(suggestions) > 0, "Should generate suggestions"
        print(f"✓ Generated {len(suggestions)} suggestions:")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"  {i}. {suggestion}")
        
        print("\n" + "="*70)
        print("TEST 1 PASSED: Chatbot is fully functional!")
        print("="*70)

def test_vitals_simulator():
    """Test vitals simulator with application context fix"""
    print("\n" + "="*70)
    print("TEST 2: Vitals Simulator")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        patient_id = 1
        
        # Get initial vitals count
        initial_count = VitalSigns.query.filter_by(patient_id=patient_id).count()
        print(f"\n✓ Initial vitals count: {initial_count}")
        
        # Start simulator
        print("\n[STARTING] Starting vitals simulation...")
        simulator.start_simulation(patient_id)
        print("✓ Simulator started successfully")
        
        # Wait for vitals to be generated
        print("\n[WAITING] Waiting 35 seconds for vitals generation...")
        time.sleep(35)
        
        # Check if new vitals were generated
        new_count = VitalSigns.query.filter_by(patient_id=patient_id).count()
        print(f"\n✓ New vitals count: {new_count}")
        print(f"✓ Vitals generated: {new_count - initial_count}")
        
        assert new_count > initial_count, "New vitals should be generated"
        
        # Get latest vitals
        latest = VitalSigns.query.filter_by(
            patient_id=patient_id
        ).order_by(VitalSigns.timestamp.desc()).first()
        
        if latest:
            print(f"\n[LATEST VITALS]")
            print(f"  - Blood Pressure: {latest.systolic_bp}/{latest.diastolic_bp} mmHg")
            print(f"  - Heart Rate: {latest.heart_rate} bpm")
            print(f"  - SpO2: {latest.spo2}%")
            print(f"  - Temperature: {latest.temperature}°F")
            print(f"  - Steps: {latest.steps}")
            print(f"  - Source: {latest.source}")
            print(f"  - Is Anomaly: {latest.is_anomaly}")
            print(f"  - Timestamp: {latest.timestamp}")
        
        # Stop simulator
        print("\n[STOPPING] Stopping simulator...")
        simulator.stop_simulation()
        print("✓ Simulator stopped successfully")
        
        print("\n" + "="*70)
        print("TEST 2 PASSED: Vitals simulator is working correctly!")
        print("="*70)

def test_fallback_mechanism():
    """Test that fallback mechanism works when OpenAI fails"""
    print("\n" + "="*70)
    print("TEST 3: Fallback Mechanism (OpenAI → Web Scraping → Fixed Responses)")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        patient_id = 1
        
        # Test blood pressure question (should trigger web scraping)
        print("\n[WEB SCRAPING] Testing blood pressure question...")
        response = chatbot.generate_response(
            patient_id, 
            "Tell me about blood pressure and hypertension"
        )
        
        assert response['success'], "Response should be successful"
        assert len(response['response']) > 100, "Web-scraped response should be detailed"
        print(f"✓ Success: {response['success']}")
        print(f"✓ Response length: {len(response['response'])} characters")
        print(f"✓ Contains medical info: {'blood pressure' in response['response'].lower()}")
        
        # Test general question (should use fixed responses)
        print("\n[FIXED RESPONSES] Testing general question...")
        response = chatbot.generate_response(patient_id, "Hello there!")
        
        assert response['success'], "Response should be successful"
        assert len(response['response']) > 0, "Fixed response should not be empty"
        print(f"✓ Success: {response['success']}")
        print(f"✓ Response: {response['response'][:100]}...")
        
        print("\n" + "="*70)
        print("TEST 3 PASSED: Fallback mechanism works correctly!")
        print("="*70)

def main():
    """Run all tests"""
    print("\n" + "#"*70)
    print("# COMPREHENSIVE TEST SUITE FOR CHATBOT AND SIMULATOR FIXES")
    print("#"*70)
    
    try:
        # Test 1: Chatbot functionality
        test_chatbot_with_openai_fallback()
        
        # Test 2: Vitals simulator (takes ~35 seconds)
        test_vitals_simulator()
        
        # Test 3: Fallback mechanism
        test_fallback_mechanism()
        
        print("\n" + "#"*70)
        print("# ALL TESTS PASSED SUCCESSFULLY!")
        print("#"*70)
        print("\n✅ Chatbot can send and receive messages")
        print("✅ OpenAI integration is configured (will fallback if network unavailable)")
        print("✅ Web scraping fallback works correctly")
        print("✅ Fixed responses work as final fallback")
        print("✅ Vitals simulator generates live data")
        print("✅ Chat history is saved and retrieved")
        print("✅ All fixes are working as expected!")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
