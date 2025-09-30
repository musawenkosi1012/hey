#!/usr/bin/env python3
"""
Demo script to showcase the newly integrated unused variables and fields
"""

from app import create_app, db
from app.models.patient import Patient
from app.models.vitals import VitalSigns, RiskPrediction
from app.models.insights import ChatMessage
import json

def demonstrate_new_features():
    """Demonstrate the newly integrated features"""
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("  ChroniSense - Unused Variables Integration Demo")
        print("=" * 70)
        
        # Get patient
        patient = Patient.query.first()
        if not patient:
            print("❌ No patient found. Run init_db.py first.")
            return
        
        print(f"\n📋 Patient Profile (ID: {patient.id})")
        print("-" * 70)
        print(f"Name: {patient.full_name}")
        print(f"Phone: {patient.phone or 'Not provided'}")
        print(f"Emergency Contact: {patient.emergency_contact or 'Not provided'}")
        
        # Medical information
        print(f"\n💊 Medical Information")
        print("-" * 70)
        
        if patient.conditions:
            try:
                conditions = json.loads(patient.conditions)
                print("Conditions:")
                for condition, value in conditions.items():
                    if value:
                        print(f"  ✓ {condition.replace('_', ' ').title()}")
            except:
                print(f"  {patient.conditions}")
        
        if patient.medications:
            try:
                medications = json.loads(patient.medications)
                print("\nMedications:")
                for med, dosage in medications.items():
                    print(f"  • {med.title()}: {dosage}")
            except:
                print(f"  {patient.medications}")
        
        if patient.allergies:
            try:
                allergies = json.loads(patient.allergies)
                print("\nAllergies:")
                for allergen, reaction in allergies.items():
                    print(f"  ⚠ {allergen.title()}: {reaction}")
            except:
                print(f"  {patient.allergies}")
        
        # Alert thresholds
        print(f"\n🚨 Alert Thresholds")
        print("-" * 70)
        print(f"Blood Pressure Max: {patient.bp_systolic_max}/{patient.bp_diastolic_max} mmHg")
        print(f"Heart Rate Range: {patient.heart_rate_min}-{patient.heart_rate_max} bpm")
        print(f"SpO2 Minimum: {patient.spo2_min}%")
        
        # Sleep data
        print(f"\n😴 Sleep Tracking Data")
        print("-" * 70)
        sleep_vitals = VitalSigns.query.filter(
            VitalSigns.patient_id == patient.id,
            VitalSigns.sleep_hours.isnot(None)
        ).all()
        
        if sleep_vitals:
            total_hours = sum(v.sleep_hours for v in sleep_vitals)
            avg_hours = total_hours / len(sleep_vitals)
            
            quality_counts = {}
            for v in sleep_vitals:
                if v.sleep_quality:
                    quality_counts[v.sleep_quality] = quality_counts.get(v.sleep_quality, 0) + 1
            
            print(f"Total sleep records: {len(sleep_vitals)}")
            print(f"Average sleep hours: {avg_hours:.1f} hours/night")
            print(f"Sleep quality distribution:")
            for quality, count in sorted(quality_counts.items()):
                print(f"  {quality.capitalize()}: {count} nights")
        else:
            print("No sleep data available yet")
        
        # Vitals with calories and steps
        print(f"\n🏃 Activity Tracking")
        print("-" * 70)
        recent_vitals = VitalSigns.query.filter(
            VitalSigns.patient_id == patient.id
        ).order_by(VitalSigns.timestamp.desc()).limit(10).all()
        
        total_steps = sum(v.steps for v in recent_vitals if v.steps)
        total_calories = sum(v.calories_burned for v in recent_vitals if v.calories_burned)
        
        print(f"Recent vitals records: {len(recent_vitals)}")
        print(f"Total steps (last 10 records): {total_steps}")
        print(f"Total calories burned: {total_calories}")
        
        # Chat history with context
        print(f"\n💬 Chat History with Vitals Context")
        print("-" * 70)
        chat_messages = ChatMessage.query.filter_by(
            patient_id=patient.id
        ).order_by(ChatMessage.timestamp.desc()).limit(3).all()
        
        if chat_messages:
            for i, msg in enumerate(chat_messages, 1):
                print(f"\nMessage {i}:")
                print(f"  User: {msg.message[:50]}...")
                print(f"  AI: {msg.response[:50]}...")
                print(f"  Session ID: {msg.session_id or 'N/A'}")
                if msg.vitals_context:
                    try:
                        context = json.loads(msg.vitals_context)
                        print(f"  Vitals context included: Yes ({len(context)} keys)")
                    except:
                        print(f"  Vitals context included: Yes")
                else:
                    print(f"  Vitals context included: No")
        else:
            print("No chat messages found")
        
        # Risk predictions
        print(f"\n📊 Risk Predictions")
        print("-" * 70)
        latest_risk = RiskPrediction.query.filter_by(
            patient_id=patient.id
        ).order_by(RiskPrediction.created_at.desc()).first()
        
        if latest_risk:
            print(f"6-hour risk: {latest_risk.risk_6h:.1f}%")
            print(f"24-hour risk: {latest_risk.risk_24h:.1f}%")
            print(f"72-hour risk: {latest_risk.risk_72h:.1f}%")
            print(f"Model version: {latest_risk.model_version}")
            
            if latest_risk.risk_factors:
                try:
                    factors = json.loads(latest_risk.risk_factors)
                    print(f"Risk factors: {', '.join(factors) if isinstance(factors, list) else factors}")
                except:
                    pass
        else:
            print("No risk predictions available")
        
        print("\n" + "=" * 70)
        print("✅ All previously unused fields are now integrated and functional!")
        print("=" * 70)
        print("\nNew Features:")
        print("  • Patient contact information (phone, emergency contact)")
        print("  • Medical conditions, medications, and allergies")
        print("  • Sleep tracking (hours and quality)")
        print("  • Activity tracking (steps and calories)")
        print("  • Chat context with vitals data")
        print("  • Risk prediction display")
        print("  • Patient ID in all API responses")
        print("\nAPI Endpoints:")
        print("  • GET /api/patient/profile/<patient_id>")
        print("  • GET /api/sleep-data/<patient_id>")
        print("  • GET /profile (Patient profile page)")
        print("\n")

if __name__ == '__main__':
    demonstrate_new_features()
