#!/usr/bin/env python3
"""
Logging Demonstration Script for ChroniSense

This script demonstrates the comprehensive logging system implemented
throughout the ChroniSense application.
"""

import os
os.environ['LOG_LEVEL'] = 'INFO'

from app import create_app
from app.services.chatbot import chatbot
from app.services.vitals_simulator import simulator

def main():
    print("\n" + "="*70)
    print("  ChroniSense Logging System Demonstration")
    print("="*70 + "\n")
    
    # Create app
    print("1. Creating Flask Application...")
    print("-" * 70)
    app = create_app()
    
    with app.app_context():
        print("\n2. Testing Chatbot Service with Logging...")
        print("-" * 70)
        
        # Test chatbot context retrieval
        context = chatbot.get_patient_context(1)
        print(f"✓ Retrieved context for: {context.get('patient_name', 'Unknown')}")
        
        # Test chatbot response generation
        print("\n3. Testing Chatbot Response Generation...")
        print("-" * 70)
        response = chatbot.generate_response(1, "How is my blood pressure?", "demo-session")
        print(f"✓ Generated response: {response['response'][:100]}...")
        
        print("\n4. Testing Vitals Simulator...")
        print("-" * 70)
        print("✓ Vitals simulator initialized")
        print("  (Check logs above to see simulator initialization)")
        
    print("\n" + "="*70)
    print("  Demonstration Complete!")
    print("="*70 + "\n")
    
    print("Log Files:")
    print(f"  Location: logs/chronisense.log")
    print(f"  Format: [timestamp] LEVEL [module.function:line] message")
    print("\nCheck the console output above to see:")
    print("  • Application initialization logs")
    print("  • Service initialization logs")
    print("  • Function entry/exit logs")
    print("  • Patient context retrieval")
    print("  • Response generation")
    print("\nTo view logs:")
    print("  tail -f logs/chronisense.log")
    print("  grep ERROR logs/chronisense.log")
    print("  grep \"app.services.chatbot\" logs/chronisense.log")
    print("\nTo change log level:")
    print("  LOG_LEVEL=DEBUG python3 demo_logging.py")
    print("  LOG_LEVEL=WARNING python3 demo_logging.py")
    print("\n")

if __name__ == '__main__':
    main()
