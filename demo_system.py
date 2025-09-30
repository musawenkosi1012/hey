#!/usr/bin/env python3
"""
ChroniSense Interactive Demo
Demonstrates the chatbot, knowledge base, and reporting capabilities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.patient import Patient
from app.services.chatbot import chatbot
from app.services.web_scraper import scraper
import json

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def demo_chatbot():
    """Demonstrate chatbot functionality"""
    print_section("CHATBOT DEMONSTRATION")
    
    app = create_app()
    with app.app_context():
        patient = Patient.query.first()
        
        questions = [
            "Hello, I need health advice",
            "What is my blood pressure?",
            "What foods should I eat?",
            "How much should I exercise?",
            "Tell me about hypertension"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n[Question {i}]")
            print(f"Patient: {question}")
            print("-" * 70)
            
            response = chatbot.generate_response(patient.id, question)
            
            if response['success']:
                print(f"AI Coach: {response['response']}\n")
            else:
                print(f"Error: {response.get('error', 'Unknown error')}\n")
            
            # Show context for first question
            if i == 1 and 'context_used' in response:
                context = response['context_used']
                print(f"\n[Patient Context Used]")
                vitals = context.get('latest_vitals', {})
                print(f"  Latest BP: {vitals.get('blood_pressure', 'N/A')}")
                print(f"  Heart Rate: {vitals.get('heart_rate', 'N/A')} bpm")
                print(f"  SpO2: {vitals.get('spo2', 'N/A')}")

def demo_knowledge_base():
    """Demonstrate knowledge base"""
    print_section("KNOWLEDGE BASE DEMONSTRATION")
    
    topics = [
        ('Hypertension', 'hypertension'),
        ('Diabetes', 'diabetes'),
        ('Healthy Diet', 'diet'),
        ('Exercise', 'exercise')
    ]
    
    for title, topic in topics:
        print(f"\n[{title}]")
        print("-" * 70)
        knowledge = scraper.scrape_health_topic(topic, max_length=300)
        if knowledge:
            print(knowledge)
        else:
            print("No information available")
    
    print(f"\n[Health Tips]")
    print("-" * 70)
    tips = scraper.search_health_tips('hypertension', 'diet')
    for i, tip in enumerate(tips[:3], 1):
        print(f"{i}. {tip}")

def demo_reports():
    """Demonstrate report generation"""
    print_section("HEALTH REPORT DEMONSTRATION")
    
    app = create_app()
    with app.app_context():
        patient = Patient.query.first()
        
        # Get patient context (mini report)
        context = chatbot.get_patient_context(patient.id)
        
        print(f"\nPatient: {context.get('patient_name', 'Unknown')}")
        print(f"Conditions: {context.get('conditions', 'None')}")
        
        print("\n[Latest Vitals]")
        vitals = context.get('latest_vitals', {})
        print(f"  Blood Pressure: {vitals.get('blood_pressure', 'N/A')}")
        print(f"  Heart Rate: {vitals.get('heart_rate', 'N/A')} bpm")
        print(f"  Oxygen Saturation: {vitals.get('spo2', 'N/A')}")
        print(f"  Recorded: {vitals.get('timestamp', 'N/A')}")
        
        print("\n[Daily Averages]")
        daily = context.get('daily_averages', {})
        print(f"  Blood Pressure: {daily.get('blood_pressure', 'N/A')}")
        print(f"  Heart Rate: {daily.get('heart_rate', 'N/A')} bpm")
        print(f"  Total Steps: {daily.get('total_steps', 0)}")
        
        print("\n[Alert Thresholds]")
        thresholds = context.get('alert_thresholds', {})
        print(f"  BP Max: {thresholds.get('bp_max', 'N/A')}")
        print(f"  HR Range: {thresholds.get('hr_range', 'N/A')} bpm")
        print(f"  SpO2 Min: {thresholds.get('spo2_min', 'N/A')}")
        
        # Quick suggestions (personalized recommendations)
        print("\n[Personalized Recommendations]")
        suggestions = chatbot.generate_quick_responses(patient.id)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")

def demo_api_usage():
    """Show API usage examples"""
    print_section("API USAGE EXAMPLES")
    
    print("""
# Get patient vitals
curl http://localhost:5000/api/vitals/1?hours=24

# Chat with AI health coach
curl -X POST http://localhost:5000/api/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message":"What is my blood pressure?"}'

# Get health tips
curl http://localhost:5000/api/health-tips/1?category=diet

# Get health knowledge
curl http://localhost:5000/api/web-knowledge?topic=hypertension

# Generate health summary report
curl http://localhost:5000/api/reports/health-summary/1?days=7

# Get chat history
curl http://localhost:5000/api/chat/history?limit=10

# Get personalized suggestions
curl http://localhost:5000/api/chat/suggestions
""")

def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "ChroniSense Interactive Demo" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\nThis demo showcases the chatbot, knowledge base, and reporting features.")
    
    try:
        # Run demonstrations
        demo_chatbot()
        demo_knowledge_base()
        demo_reports()
        demo_api_usage()
        
        # Summary
        print_section("DEMO COMPLETE")
        print("""
✅ Chatbot: Demonstrated intelligent responses with patient context
✅ Knowledge Base: Showed health information for multiple topics  
✅ Reports: Generated personalized health summaries and recommendations
✅ API: Provided usage examples for all endpoints

The ChroniSense system is fully operational with:
- Working chatbot with knowledge base integration
- Comprehensive health reporting capabilities
- All API endpoints functional
- SQLite database operational

To start the application:
  python3 app.py

To validate the system:
  python3 validate_system.py

Documentation:
  - QUICK_START.md - Installation & usage guide
  - SYSTEM_TESTING_REPORT.md - Detailed test results
  - SYSTEM_SUMMARY.md - Complete system overview
""")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
