#!/usr/bin/env python3
"""
ChroniSense Vitals Simulator - Standalone Demo Script

This script demonstrates the system's real-time monitoring capabilities by
simulating the collection and analysis of vital signs every 5 minutes.

Features:
- Simulates realistic vital signs (heart rate, blood pressure, temperature, oxygen saturation)
- Intelligent analysis with alert detection
- Continuous monitoring display
- Timestamps for each data collection cycle

Usage:
    python simulate_vitals.py

For demo purposes (faster updates):
    Change COLLECTION_INTERVAL to 5 seconds instead of 5 minutes
"""

import random
import time
from datetime import datetime

# Configuration
COLLECTION_INTERVAL = 5 * 60  # 5 minutes in seconds (change to 5 for demo)

def collect_vitals():
    """
    Simulate random vitals collection.
    
    Returns:
        dict: Dictionary containing simulated vital signs and timestamp
    """
    return {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'heart_rate': random.randint(60, 100),   # bpm
        'blood_pressure': f"{random.randint(110, 130)}/{random.randint(70, 90)}",  # mmHg
        'temperature': round(random.uniform(36.5, 37.8), 1),  # Celsius
        'oxygen_saturation': random.randint(95, 100)  # %
    }

def analyze_vitals(vitals):
    """
    Analyze collected vitals and generate alerts for abnormal values.
    
    Args:
        vitals (dict): Dictionary containing vital signs
        
    Returns:
        list: List of alert messages for abnormal vitals
    """
    alerts = []
    
    # Check heart rate
    if vitals['heart_rate'] > 90:
        alerts.append('⚠️  High heart rate detected')
    elif vitals['heart_rate'] < 60:
        alerts.append('⚠️  Low heart rate detected')
    
    # Check temperature
    if float(vitals['temperature']) > 37.5:
        alerts.append('🌡️  Fever suspected')
    elif float(vitals['temperature']) < 36.0:
        alerts.append('🌡️  Low body temperature')
    
    # Check oxygen saturation
    if int(vitals['oxygen_saturation']) < 96:
        alerts.append('💨 Low oxygen saturation')
    
    # Check blood pressure
    try:
        systolic, diastolic = map(int, vitals['blood_pressure'].split('/'))
        if systolic > 130 or diastolic > 85:
            alerts.append('🩺 Elevated blood pressure')
        elif systolic < 90 or diastolic < 60:
            alerts.append('🩺 Low blood pressure')
    except:
        pass
    
    return alerts

def format_vitals_display(vitals, alerts):
    """
    Format vitals and alerts for display.
    
    Args:
        vitals (dict): Dictionary containing vital signs
        alerts (list): List of alert messages
        
    Returns:
        str: Formatted string for display
    """
    output = []
    output.append("=" * 60)
    output.append(f"📊 VITALS COLLECTION - {vitals['timestamp']}")
    output.append("=" * 60)
    output.append(f"💓 Heart Rate:        {vitals['heart_rate']} bpm")
    output.append(f"🩺 Blood Pressure:    {vitals['blood_pressure']} mmHg")
    output.append(f"🌡️  Temperature:       {vitals['temperature']}°C")
    output.append(f"💨 Oxygen Saturation: {vitals['oxygen_saturation']}%")
    output.append("-" * 60)
    
    if alerts:
        output.append("🚨 ALERTS:")
        for alert in alerts:
            output.append(f"   {alert}")
    else:
        output.append("✅ All vitals normal - No alerts")
    
    output.append("=" * 60)
    return "\n".join(output)

def main():
    """
    Main function to run the continuous vitals monitoring simulation.
    """
    print("\n" + "=" * 60)
    print("🏥 ChroniSense Vitals Monitoring System")
    print("=" * 60)
    print("System is running. Collecting and analyzing vitals every", end=" ")
    if COLLECTION_INTERVAL >= 60:
        print(f"{COLLECTION_INTERVAL // 60} minutes.")
    else:
        print(f"{COLLECTION_INTERVAL} seconds.")
    print("Press Ctrl+C to stop.")
    print("=" * 60)
    print()
    
    try:
        while True:
            # Collect vitals
            vitals = collect_vitals()
            
            # Analyze vitals for alerts
            alerts = analyze_vitals(vitals)
            
            # Display results
            print(format_vitals_display(vitals, alerts))
            print()
            
            # Wait for next collection interval
            time.sleep(COLLECTION_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("🛑 System stopped by user")
        print("=" * 60)
        print()

if __name__ == "__main__":
    main()
