# Example Output - ChroniSense Vitals Monitoring

This file shows sample output from the vitals monitoring demonstration scripts.

## Production Mode Output (simulate_vitals.py)

```
============================================================
🏥 ChroniSense Vitals Monitoring System
============================================================
System is running. Collecting and analyzing vitals every 5 minutes.
Press Ctrl+C to stop.
============================================================

============================================================
📊 VITALS COLLECTION - 2025-09-30 08:00:00
============================================================
💓 Heart Rate:        72 bpm
🩺 Blood Pressure:    118/78 mmHg
🌡️  Temperature:       37.0°C
💨 Oxygen Saturation: 98%
------------------------------------------------------------
✅ All vitals normal - No alerts
============================================================

============================================================
📊 VITALS COLLECTION - 2025-09-30 08:05:00
============================================================
💓 Heart Rate:        95 bpm
🩺 Blood Pressure:    135/88 mmHg
🌡️  Temperature:       37.6°C
💨 Oxygen Saturation: 95%
------------------------------------------------------------
🚨 ALERTS:
   ⚠️  High heart rate detected
   🩺 Elevated blood pressure
   🌡️  Fever suspected
   💨 Low oxygen saturation
============================================================

============================================================
📊 VITALS COLLECTION - 2025-09-30 08:10:00
============================================================
💓 Heart Rate:        68 bpm
🩺 Blood Pressure:    120/80 mmHg
🌡️  Temperature:       36.8°C
💨 Oxygen Saturation: 99%
------------------------------------------------------------
✅ All vitals normal - No alerts
============================================================
```

## Demo Mode Output (simulate_vitals_demo.py)

```
============================================================
🏥 ChroniSense Vitals Monitoring System - DEMO MODE
============================================================
System is running. Collecting and analyzing vitals every 5 seconds.
Press Ctrl+C to stop.
============================================================

============================================================
📊 VITALS COLLECTION - 2025-09-30 14:30:05
============================================================
💓 Heart Rate:        74 bpm
🩺 Blood Pressure:    118/90 mmHg
🌡️  Temperature:       37.5°C
💨 Oxygen Saturation: 97%
------------------------------------------------------------
🚨 ALERTS:
   🩺 Elevated blood pressure
============================================================

============================================================
📊 VITALS COLLECTION - 2025-09-30 14:30:10
============================================================
💓 Heart Rate:        63 bpm
🩺 Blood Pressure:    115/79 mmHg
🌡️  Temperature:       37.4°C
💨 Oxygen Saturation: 96%
------------------------------------------------------------
✅ All vitals normal - No alerts
============================================================

============================================================
📊 VITALS COLLECTION - 2025-09-30 14:30:15
============================================================
💓 Heart Rate:        91 bpm
🩺 Blood Pressure:    128/82 mmHg
🌡️  Temperature:       37.7°C
💨 Oxygen Saturation: 95%
------------------------------------------------------------
🚨 ALERTS:
   ⚠️  High heart rate detected
   🌡️  Fever suspected
   💨 Low oxygen saturation
============================================================

============================================================
📊 VITALS COLLECTION - 2025-09-30 14:30:20
============================================================
💓 Heart Rate:        76 bpm
🩺 Blood Pressure:    122/75 mmHg
🌡️  Temperature:       36.9°C
💨 Oxygen Saturation: 98%
------------------------------------------------------------
✅ All vitals normal - No alerts
============================================================
```

## Alert Types Demonstrated

### Heart Rate Alerts
- ⚠️  High heart rate detected (> 90 bpm)
- ⚠️  Low heart rate detected (< 60 bpm)

### Temperature Alerts
- 🌡️  Fever suspected (> 37.5°C)
- 🌡️  Low body temperature (< 36.0°C)

### Oxygen Saturation Alerts
- 💨 Low oxygen saturation (< 96%)

### Blood Pressure Alerts
- 🩺 Elevated blood pressure (systolic > 130 or diastolic > 85)
- 🩺 Low blood pressure (systolic < 90 or diastolic < 60)

## System Stop Output

When the user presses Ctrl+C:

```
============================================================
🛑 System stopped by user
============================================================
```

## Key Features Demonstrated

1. ✅ **Continuous Monitoring**: System runs indefinitely until stopped
2. ✅ **Real-time Analysis**: Instant evaluation of each vital reading
3. ✅ **Multi-parameter Tracking**: Heart rate, BP, temperature, SpO₂
4. ✅ **Intelligent Alerts**: Automatic detection of abnormal values
5. ✅ **Clear Timestamps**: Precise timing for each measurement
6. ✅ **User-friendly Display**: Emoji indicators and formatted output
7. ✅ **Status Reporting**: Clear indication of normal vs alert conditions
