from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.patient import Patient
from app.models.vitals import VitalSigns
from app.models.insights import ChatMessage
from app.services.chatbot import chatbot
from app.services.vitals_simulator import simulator
from app import db
from datetime import datetime, timedelta, timezone
import uuid
import logging

logger = logging.getLogger(__name__)

# Helper function for naive UTC datetime (for DB compatibility)
def utc_now():
    return datetime.utcnow()

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/health')
def health_check():
    """Health check endpoint for Render and monitoring"""
    try:
        # Check database connectivity
        from app import db
        db.session.execute(db.text('SELECT 1'))
        
        return jsonify({
            'status': 'healthy',
            'service': 'ChroniSense API',
            'database': 'connected',
            'timestamp': utc_now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'ChroniSense API',
            'error': str(e),
            'timestamp': utc_now().isoformat()
        }), 503

@bp.route('/vitals/<int:patient_id>')
@login_required
def get_vitals(patient_id):
    """Get vitals data for a patient"""
    logger.info(f"get_vitals called for patient_id={patient_id} by user={current_user.username}")
    try:
        # Check authorization
        if current_user.role == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id, id=patient_id).first()
            if not patient:
                return jsonify({'error': 'Unauthorized'}), 403
        
        # Get query parameters
        hours = request.args.get('hours', 24, type=int)
        start_time = utc_now() - timedelta(hours=hours)
        
        vitals = VitalSigns.query.filter(
            VitalSigns.patient_id == patient_id,
            VitalSigns.timestamp >= start_time
        ).order_by(VitalSigns.timestamp.asc()).all()
        
        return jsonify({
            'success': True,
            'data': [v.to_dict() for v in vitals]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/vitals', methods=['POST'])
def ingest_vitals():
    """Ingest vitals data (for external devices)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['patient_id', 'heart_rate', 'systolic_bp', 'diastolic_bp']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create vital signs record
        vitals = VitalSigns(
            patient_id=data['patient_id'],
            heart_rate=data.get('heart_rate'),
            systolic_bp=data.get('systolic_bp'),
            diastolic_bp=data.get('diastolic_bp'),
            spo2=data.get('spo2'),
            temperature=data.get('temperature', 98.6),
            steps=data.get('steps', 0),
            calories_burned=data.get('calories_burned', 0),
            source=data.get('source', 'external'),
            timestamp=utc_now()
        )
        
        db.session.add(vitals)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vitals recorded successfully',
            'id': vitals.id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/chat', methods=['POST'])
@login_required
def chat_with_ai():
    """Chat with AI health coach"""
    try:
        if current_user.role != 'patient':
            return jsonify({'error': 'Only patients can chat with the health coach'}), 403
        
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        session_id = data.get('session_id') or str(uuid.uuid4())
        
        # Generate AI response
        response = chatbot.generate_response(patient.id, message, session_id)
        
        return jsonify({
            'success': response['success'],
            'response': response['response'],
            'session_id': session_id,
            'timestamp': utc_now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/chat/history')
@login_required
def get_chat_history():
    """Get chat history for current patient"""
    try:
        if current_user.role != 'patient':
            return jsonify({'error': 'Unauthorized'}), 403
        
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        limit = request.args.get('limit', 10, type=int)
        history = chatbot.get_chat_history(patient.id, limit)
        
        return jsonify({
            'success': True,
            'patient_id': patient.id,
            'history': history
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/chat/suggestions')
@login_required
def get_chat_suggestions():
    """Get quick response suggestions"""
    try:
        if current_user.role != 'patient':
            return jsonify({'error': 'Unauthorized'}), 403
        
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        suggestions = chatbot.generate_quick_responses(patient.id)
        
        return jsonify({
            'success': True,
            'patient_id': patient.id,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/simulator/start', methods=['POST'])
@login_required
def start_simulator():
    """Start vitals simulation"""
    try:
        if current_user.role not in ['patient', 'doctor']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        patient_id = data.get('patient_id')
        
        if current_user.role == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            patient_id = patient.id if patient else None
        
        if not patient_id:
            return jsonify({'error': 'Patient ID required'}), 400
        
        simulator.start_simulation(patient_id)
        
        return jsonify({
            'success': True,
            'message': 'Vitals simulation started',
            'patient_id': patient_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/simulator/stop', methods=['POST'])
@login_required
def stop_simulator():
    """Stop vitals simulation"""
    try:
        simulator.stop_simulation()
        
        return jsonify({
            'success': True,
            'message': 'Vitals simulation stopped'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/simulator/inject-anomaly', methods=['POST'])
@login_required
def inject_anomaly():
    """Inject an anomaly for testing"""
    try:
        if current_user.role not in ['doctor']:
            return jsonify({'error': 'Only doctors can inject anomalies'}), 403
        
        data = request.get_json()
        anomaly_type = data.get('type', 'hypertension')
        
        simulator.inject_anomaly(anomaly_type)
        
        return jsonify({
            'success': True,
            'message': f'Injected {anomaly_type} anomaly for testing'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/health-tips/<int:patient_id>')
@login_required
def get_health_tips(patient_id):
    """Get personalized health tips for a patient"""
    try:
        # Check authorization
        if current_user.role == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id, id=patient_id).first()
            if not patient:
                return jsonify({'error': 'Unauthorized'}), 403
        
        category = request.args.get('category', 'general')
        tips = chatbot.get_health_tips(patient_id, category)
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'tips': tips,
            'category': category
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/patient/profile/<int:patient_id>')
@login_required
def get_patient_profile(patient_id):
    """Get detailed patient profile information"""
    try:
        # Check authorization
        if current_user.role == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id, id=patient_id).first()
            if not patient:
                return jsonify({'error': 'Unauthorized'}), 403
        elif current_user.role not in ['doctor', 'caregiver']:
            return jsonify({'error': 'Unauthorized'}), 403
        else:
            patient = Patient.query.get(patient_id)
            if not patient:
                return jsonify({'error': 'Patient not found'}), 404
        
        # Build profile response
        import json
        from datetime import date
        
        # Calculate age
        today = date.today()
        age = today.year - patient.date_of_birth.year - ((today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day))
        
        profile = {
            'success': True,
            'patient_id': patient.id,
            'personal_info': {
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'full_name': patient.full_name,
                'date_of_birth': patient.date_of_birth.isoformat(),
                'age': age,
                'gender': patient.gender,
                'phone': patient.phone,
                'emergency_contact': patient.emergency_contact
            },
            'medical_info': {
                'conditions': json.loads(patient.conditions) if patient.conditions else None,
                'medications': json.loads(patient.medications) if patient.medications else None,
                'allergies': json.loads(patient.allergies) if patient.allergies else None
            },
            'thresholds': {
                'bp_systolic_max': patient.bp_systolic_max,
                'bp_diastolic_max': patient.bp_diastolic_max,
                'heart_rate_min': patient.heart_rate_min,
                'heart_rate_max': patient.heart_rate_max,
                'spo2_min': patient.spo2_min
            }
        }
        
        return jsonify(profile)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/sleep-data/<int:patient_id>')
@login_required
def get_sleep_data(patient_id):
    """Get sleep data for a patient"""
    try:
        # Check authorization
        if current_user.role == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id, id=patient_id).first()
            if not patient:
                return jsonify({'error': 'Unauthorized'}), 403
        
        # Get query parameters
        days = request.args.get('days', 7, type=int)
        start_time = utc_now() - timedelta(days=days)
        
        # Get vitals with sleep data
        vitals = VitalSigns.query.filter(
            VitalSigns.patient_id == patient_id,
            VitalSigns.timestamp >= start_time,
            VitalSigns.sleep_hours.isnot(None)
        ).order_by(VitalSigns.timestamp.desc()).all()
        
        sleep_data = []
        for v in vitals:
            sleep_data.append({
                'date': v.timestamp.date().isoformat(),
                'sleep_hours': v.sleep_hours,
                'sleep_quality': v.sleep_quality,
                'timestamp': v.timestamp.isoformat()
            })
        
        # Calculate sleep statistics
        avg_sleep = sum(v.sleep_hours for v in vitals if v.sleep_hours) / len(vitals) if vitals else 0
        
        quality_counts = {}
        for v in vitals:
            if v.sleep_quality:
                quality_counts[v.sleep_quality] = quality_counts.get(v.sleep_quality, 0) + 1
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'sleep_records': sleep_data,
            'statistics': {
                'average_hours': round(avg_sleep, 1),
                'total_nights': len(vitals),
                'quality_distribution': quality_counts
            },
            'period_days': days
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/web-knowledge')
@login_required
def get_web_knowledge():
    """Get web-scraped health knowledge about a topic"""
    try:
        from app.services.web_scraper import scraper
        
        topic = request.args.get('topic', 'general health')
        max_length = request.args.get('max_length', 500, type=int)
        
        knowledge = scraper.scrape_health_topic(topic, max_length)
        
        if knowledge:
            return jsonify({
                'success': True,
                'topic': topic,
                'knowledge': knowledge
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No knowledge found for this topic'
            }), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reports/health-summary/<int:patient_id>')
@login_required
def get_health_summary_report(patient_id):
    """Generate comprehensive health summary report for a patient"""
    try:
        # Check authorization
        if current_user.role == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id, id=patient_id).first()
            if not patient:
                return jsonify({'error': 'Unauthorized'}), 403
        elif current_user.role != 'doctor':
            return jsonify({'error': 'Unauthorized'}), 403
        
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get report period (default last 7 days)
        days = request.args.get('days', 7, type=int)
        start_date = utc_now() - timedelta(days=days)
        
        # Get vitals for the period
        vitals = VitalSigns.query.filter(
            VitalSigns.patient_id == patient_id,
            VitalSigns.timestamp >= start_date
        ).order_by(VitalSigns.timestamp.asc()).all()
        
        # Calculate statistics
        if vitals:
            bp_readings = [v for v in vitals if v.systolic_bp and v.diastolic_bp]
            hr_readings = [v for v in vitals if v.heart_rate]
            spo2_readings = [v for v in vitals if v.spo2]
            
            stats = {
                'blood_pressure': {
                    'avg_systolic': sum(v.systolic_bp for v in bp_readings) / len(bp_readings) if bp_readings else 0,
                    'avg_diastolic': sum(v.diastolic_bp for v in bp_readings) / len(bp_readings) if bp_readings else 0,
                    'max_systolic': max(v.systolic_bp for v in bp_readings) if bp_readings else 0,
                    'min_systolic': min(v.systolic_bp for v in bp_readings) if bp_readings else 0,
                    'readings_count': len(bp_readings)
                },
                'heart_rate': {
                    'avg': sum(v.heart_rate for v in hr_readings) / len(hr_readings) if hr_readings else 0,
                    'max': max(v.heart_rate for v in hr_readings) if hr_readings else 0,
                    'min': min(v.heart_rate for v in hr_readings) if hr_readings else 0,
                    'readings_count': len(hr_readings)
                },
                'oxygen_saturation': {
                    'avg': sum(v.spo2 for v in spo2_readings) / len(spo2_readings) if spo2_readings else 0,
                    'min': min(v.spo2 for v in spo2_readings) if spo2_readings else 0,
                    'readings_count': len(spo2_readings)
                },
                'activity': {
                    'total_steps': sum(v.steps for v in vitals if v.steps),
                    'avg_daily_steps': sum(v.steps for v in vitals if v.steps) / days if vitals else 0
                }
            }
        else:
            stats = None
        
        # Get chat history for the period
        from app.models.insights import ChatMessage
        chat_history = ChatMessage.query.filter(
            ChatMessage.patient_id == patient_id,
            ChatMessage.timestamp >= start_date
        ).order_by(ChatMessage.timestamp.desc()).limit(10).all()
        
        # Get insights for the period
        from app.models.insights import PatientInsight
        insights = PatientInsight.query.filter(
            PatientInsight.patient_id == patient_id,
            PatientInsight.created_at >= start_date
        ).order_by(PatientInsight.created_at.desc()).all()
        
        # Generate health recommendations
        recommendations = []
        if stats and stats['blood_pressure']['avg_systolic'] > 130:
            recommendations.append({
                'type': 'blood_pressure',
                'severity': 'warning',
                'message': 'Blood pressure is elevated. Consider reducing sodium intake and increasing physical activity.'
            })
        
        if stats and stats['activity']['avg_daily_steps'] < 5000:
            recommendations.append({
                'type': 'activity',
                'severity': 'info',
                'message': 'Daily step count is below recommended levels. Try to increase to at least 6,000 steps per day.'
            })
        
        # Build comprehensive report
        # Calculate age from date_of_birth
        from datetime import date
        today = date.today()
        age = today.year - patient.date_of_birth.year - ((today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day))
        
        # Parse medical information
        import json
        conditions = None
        medications = None
        allergies = None
        
        try:
            if patient.conditions:
                conditions = json.loads(patient.conditions)
        except:
            conditions = patient.conditions
        
        try:
            if patient.medications:
                medications = json.loads(patient.medications)
        except:
            medications = patient.medications
        
        try:
            if patient.allergies:
                allergies = json.loads(patient.allergies)
        except:
            allergies = patient.allergies
        
        # Get sleep data
        sleep_vitals = [v for v in vitals if v.sleep_hours is not None]
        sleep_stats = None
        if sleep_vitals:
            avg_sleep = sum(v.sleep_hours for v in sleep_vitals) / len(sleep_vitals)
            quality_counts = {}
            for v in sleep_vitals:
                if v.sleep_quality:
                    quality_counts[v.sleep_quality] = quality_counts.get(v.sleep_quality, 0) + 1
            
            sleep_stats = {
                'average_hours': round(avg_sleep, 1),
                'total_nights': len(sleep_vitals),
                'quality_distribution': quality_counts
            }
        
        report = {
            'success': True,
            'patient': {
                'id': patient.id,
                'name': f"{patient.first_name} {patient.last_name}",
                'age': age,
                'date_of_birth': patient.date_of_birth.isoformat(),
                'gender': patient.gender,
                'phone': patient.phone,
                'emergency_contact': patient.emergency_contact,
                'conditions': conditions,
                'medications': medications,
                'allergies': allergies
            },
            'period': {
                'days': days,
                'start_date': start_date.isoformat(),
                'end_date': utc_now().isoformat()
            },
            'statistics': stats,
            'sleep_statistics': sleep_stats,
            'vitals_count': len(vitals),
            'recommendations': recommendations,
            'insights_count': len(insights),
            'chat_interactions': len(chat_history),
            'generated_at': utc_now().isoformat()
        }
        
        return jsonify(report)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/reports/generate/<int:patient_id>', methods=['POST'])
@login_required
def generate_report(patient_id):
    """Generate and save a daily, weekly, or monthly report"""
    try:
        # Check authorization
        if current_user.role == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id, id=patient_id).first()
            if not patient:
                return jsonify({'error': 'Unauthorized'}), 403
        elif current_user.role not in ['doctor']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        data = request.get_json()
        report_type = data.get('type', 'daily')  # daily, weekly, monthly
        
        # Calculate period based on report type
        if report_type == 'daily':
            days = 1
            period_start = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = utc_now()
        elif report_type == 'weekly':
            days = 7
            period_start = utc_now() - timedelta(days=7)
            period_end = utc_now()
        elif report_type == 'monthly':
            days = 30
            period_start = utc_now() - timedelta(days=30)
            period_end = utc_now()
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
        # Get vitals for the period
        vitals = VitalSigns.query.filter(
            VitalSigns.patient_id == patient_id,
            VitalSigns.timestamp >= period_start,
            VitalSigns.timestamp <= period_end
        ).order_by(VitalSigns.timestamp.asc()).all()
        
        if not vitals:
            return jsonify({'error': 'No vitals data available for this period'}), 404
        
        # Calculate statistics
        bp_readings = [v for v in vitals if v.systolic_bp and v.diastolic_bp]
        hr_readings = [v for v in vitals if v.heart_rate]
        spo2_readings = [v for v in vitals if v.spo2]
        
        # Generate AI insights using chatbot service
        avg_bp_sys = sum(v.systolic_bp for v in bp_readings) / len(bp_readings) if bp_readings else 0
        avg_bp_dia = sum(v.diastolic_bp for v in bp_readings) / len(bp_readings) if bp_readings else 0
        avg_hr = sum(v.heart_rate for v in hr_readings) / len(hr_readings) if hr_readings else 0
        avg_spo2 = sum(v.spo2 for v in spo2_readings) / len(spo2_readings) if spo2_readings else 0
        
        # Generate AI analysis
        analysis_prompt = f"Generate a {report_type} health report for a patient with these vitals: BP {avg_bp_sys:.0f}/{avg_bp_dia:.0f}, HR {avg_hr:.0f} bpm, SpO2 {avg_spo2:.1f}%. Provide analysis and recommendations."
        ai_response = chatbot.generate_response(patient_id, analysis_prompt, f"report_{report_type}_{utc_now().timestamp()}")
        
        # Determine severity
        severity = 'info'
        if avg_bp_sys > 140 or avg_hr > 100 or avg_spo2 < 92:
            severity = 'critical'
        elif avg_bp_sys > 130 or avg_hr > 90 or avg_spo2 < 95:
            severity = 'warning'
        
        # Create insight record
        from app.models.insights import PatientInsight
        insight = PatientInsight(
            patient_id=patient_id,
            title=f"{report_type.capitalize()} Health Report - {period_end.strftime('%B %d, %Y')}",
            content=ai_response.get('response', 'Report generated successfully'),
            insight_type=report_type,
            severity=severity,
            period_start=period_start,
            period_end=period_end,
            generated_by_ai=True
        )
        
        db.session.add(insight)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{report_type.capitalize()} report generated successfully',
            'report': {
                'id': insight.id,
                'title': insight.title,
                'content': insight.content,
                'type': report_type,
                'severity': severity,
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat(),
                'generated_at': insight.created_at.isoformat()
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/reports/scheduled/<int:patient_id>')
@login_required
def get_scheduled_reports(patient_id):
    """Get all scheduled reports (daily, weekly, monthly) for a patient"""
    try:
        # Check authorization
        if current_user.role == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id, id=patient_id).first()
            if not patient:
                return jsonify({'error': 'Unauthorized'}), 403
        
        report_type = request.args.get('type')  # daily, weekly, monthly, or None for all
        
        from app.models.insights import PatientInsight
        query = PatientInsight.query.filter_by(patient_id=patient_id)
        
        if report_type:
            query = query.filter_by(insight_type=report_type)
        else:
            query = query.filter(PatientInsight.insight_type.in_(['daily', 'weekly', 'monthly']))
        
        reports = query.order_by(PatientInsight.created_at.desc()).limit(30).all()
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'reports': [{
                'id': r.id,
                'title': r.title,
                'content': r.content,
                'type': r.insight_type,
                'severity': r.severity,
                'period_start': r.period_start.isoformat() if r.period_start else None,
                'period_end': r.period_end.isoformat() if r.period_end else None,
                'created_at': r.created_at.isoformat(),
                'generated_by_ai': r.generated_by_ai
            } for r in reports]
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/doctor/patient/<int:patient_id>/electrobook')
@login_required
def get_patient_electrobook(patient_id):
    """Get electrobook insights for a patient (doctor only)"""
    try:
        if current_user.role != 'doctor':
            return jsonify({'error': 'Unauthorized - doctors only'}), 403
        
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get all insights for this patient
        from app.models.insights import PatientInsight
        insights = PatientInsight.query.filter_by(
            patient_id=patient_id
        ).order_by(PatientInsight.created_at.desc()).all()
        
        # Categorize insights
        daily_insights = [i for i in insights if i.insight_type == 'daily']
        weekly_insights = [i for i in insights if i.insight_type == 'weekly']
        monthly_insights = [i for i in insights if i.insight_type == 'monthly']
        
        return jsonify({
            'success': True,
            'patient': {
                'id': patient.id,
                'name': f"{patient.first_name} {patient.last_name}",
                'gender': patient.gender,
                'date_of_birth': patient.date_of_birth.isoformat()
            },
            'insights': {
                'daily': [{
                    'id': i.id,
                    'title': i.title,
                    'content': i.content,
                    'severity': i.severity,
                    'created_at': i.created_at.isoformat(),
                    'generated_by_ai': i.generated_by_ai
                } for i in daily_insights[:7]],
                'weekly': [{
                    'id': i.id,
                    'title': i.title,
                    'content': i.content,
                    'severity': i.severity,
                    'created_at': i.created_at.isoformat(),
                    'generated_by_ai': i.generated_by_ai
                } for i in weekly_insights[:4]],
                'monthly': [{
                    'id': i.id,
                    'title': i.title,
                    'content': i.content,
                    'severity': i.severity,
                    'created_at': i.created_at.isoformat(),
                    'generated_by_ai': i.generated_by_ai
                } for i in monthly_insights[:3]]
            },
            'total_insights': len(insights)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/doctor/patient/<int:patient_id>/vitals/history')
@login_required
def get_patient_vitals_history(patient_id):
    """Get complete vitals history for a patient (doctor only)"""
    try:
        if current_user.role != 'doctor':
            return jsonify({'error': 'Unauthorized - doctors only'}), 403
        
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get query parameters
        days = request.args.get('days', type=int)
        limit = request.args.get('limit', 1000, type=int)
        page = request.args.get('page', 1, type=int)
        
        # Build query
        query = VitalSigns.query.filter_by(patient_id=patient_id)
        
        if days:
            start_date = utc_now() - timedelta(days=days)
            query = query.filter(VitalSigns.timestamp >= start_date)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        vitals = query.order_by(VitalSigns.timestamp.desc()).limit(limit).offset(offset).all()
        
        # Calculate statistics
        if vitals:
            bp_readings = [v for v in vitals if v.systolic_bp and v.diastolic_bp]
            hr_readings = [v for v in vitals if v.heart_rate]
            spo2_readings = [v for v in vitals if v.spo2]
            
            stats = {
                'total_readings': len(vitals),
                'anomaly_count': len([v for v in vitals if v.is_anomaly]),
                'blood_pressure': {
                    'avg_systolic': sum(v.systolic_bp for v in bp_readings) / len(bp_readings) if bp_readings else 0,
                    'avg_diastolic': sum(v.diastolic_bp for v in bp_readings) / len(bp_readings) if bp_readings else 0,
                    'max_systolic': max(v.systolic_bp for v in bp_readings) if bp_readings else 0,
                    'min_systolic': min(v.systolic_bp for v in bp_readings) if bp_readings else 0
                },
                'heart_rate': {
                    'avg': sum(v.heart_rate for v in hr_readings) / len(hr_readings) if hr_readings else 0,
                    'max': max(v.heart_rate for v in hr_readings) if hr_readings else 0,
                    'min': min(v.heart_rate for v in hr_readings) if hr_readings else 0
                },
                'spo2': {
                    'avg': sum(v.spo2 for v in spo2_readings) / len(spo2_readings) if spo2_readings else 0,
                    'min': min(v.spo2 for v in spo2_readings) if spo2_readings else 0
                }
            }
        else:
            stats = None
        
        return jsonify({
            'success': True,
            'patient': {
                'id': patient.id,
                'name': f"{patient.first_name} {patient.last_name}"
            },
            'vitals': [v.to_dict() for v in vitals],
            'statistics': stats,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'total_pages': (total_count + limit - 1) // limit
            },
            'period_days': days
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/doctor/patient/<int:patient_id>/full-details')
@login_required
def get_patient_full_details(patient_id):
    """Get comprehensive patient details including profile, vitals, insights, and chat history (doctor only)"""
    try:
        if current_user.role != 'doctor':
            return jsonify({'error': 'Unauthorized - doctors only'}), 403
        
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get patient profile
        from datetime import date
        import json
        
        today = date.today()
        age = today.year - patient.date_of_birth.year - ((today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day))
        
        # Parse medical information
        conditions = None
        medications = None
        allergies = None
        
        try:
            if patient.conditions:
                conditions = json.loads(patient.conditions)
        except:
            conditions = patient.conditions
        
        try:
            if patient.medications:
                medications = json.loads(patient.medications)
        except:
            medications = patient.medications
        
        try:
            if patient.allergies:
                allergies = json.loads(patient.allergies)
        except:
            allergies = patient.allergies
        
        # Get recent vitals (last 30 days)
        thirty_days_ago = utc_now() - timedelta(days=30)
        recent_vitals = VitalSigns.query.filter(
            VitalSigns.patient_id == patient_id,
            VitalSigns.timestamp >= thirty_days_ago
        ).order_by(VitalSigns.timestamp.desc()).limit(100).all()
        
        # Get latest risk prediction
        from app.models.vitals import RiskPrediction
        latest_risk = RiskPrediction.query.filter_by(
            patient_id=patient_id
        ).order_by(RiskPrediction.created_at.desc()).first()
        
        # Get recent insights
        from app.models.insights import PatientInsight
        insights = PatientInsight.query.filter_by(
            patient_id=patient_id
        ).order_by(PatientInsight.created_at.desc()).limit(20).all()
        
        # Get chat history
        chat_history = ChatMessage.query.filter_by(
            patient_id=patient_id
        ).order_by(ChatMessage.timestamp.desc()).limit(10).all()
        
        # Calculate vitals statistics
        if recent_vitals:
            bp_readings = [v for v in recent_vitals if v.systolic_bp and v.diastolic_bp]
            hr_readings = [v for v in recent_vitals if v.heart_rate]
            spo2_readings = [v for v in recent_vitals if v.spo2]
            
            vitals_stats = {
                'blood_pressure': {
                    'avg_systolic': sum(v.systolic_bp for v in bp_readings) / len(bp_readings) if bp_readings else 0,
                    'avg_diastolic': sum(v.diastolic_bp for v in bp_readings) / len(bp_readings) if bp_readings else 0,
                    'max_systolic': max(v.systolic_bp for v in bp_readings) if bp_readings else 0,
                    'min_systolic': min(v.systolic_bp for v in bp_readings) if bp_readings else 0
                },
                'heart_rate': {
                    'avg': sum(v.heart_rate for v in hr_readings) / len(hr_readings) if hr_readings else 0,
                    'max': max(v.heart_rate for v in hr_readings) if hr_readings else 0,
                    'min': min(v.heart_rate for v in hr_readings) if hr_readings else 0
                },
                'spo2': {
                    'avg': sum(v.spo2 for v in spo2_readings) / len(spo2_readings) if spo2_readings else 0,
                    'min': min(v.spo2 for v in spo2_readings) if spo2_readings else 0
                },
                'anomaly_count': len([v for v in recent_vitals if v.is_anomaly])
            }
        else:
            vitals_stats = None
        
        # Build comprehensive response
        response = {
            'success': True,
            'patient': {
                'id': patient.id,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'full_name': patient.full_name,
                'age': age,
                'date_of_birth': patient.date_of_birth.isoformat(),
                'gender': patient.gender,
                'phone': patient.phone,
                'emergency_contact': patient.emergency_contact,
                'medical_info': {
                    'conditions': conditions,
                    'medications': medications,
                    'allergies': allergies
                },
                'thresholds': {
                    'bp_systolic_max': patient.bp_systolic_max,
                    'bp_diastolic_max': patient.bp_diastolic_max,
                    'heart_rate_min': patient.heart_rate_min,
                    'heart_rate_max': patient.heart_rate_max,
                    'spo2_min': patient.spo2_min
                }
            },
            'vitals': {
                'recent': [v.to_dict() for v in recent_vitals[:20]],
                'statistics': vitals_stats,
                'total_count': len(recent_vitals)
            },
            'risk_assessment': {
                'risk_6h': latest_risk.risk_6h if latest_risk else 0,
                'risk_24h': latest_risk.risk_24h if latest_risk else 0,
                'risk_72h': latest_risk.risk_72h if latest_risk else 0,
                'updated_at': latest_risk.created_at.isoformat() if latest_risk else None
            } if latest_risk else None,
            'insights': [{
                'id': i.id,
                'title': i.title,
                'content': i.content,
                'type': i.insight_type,
                'severity': i.severity,
                'created_at': i.created_at.isoformat(),
                'generated_by_ai': i.generated_by_ai
            } for i in insights],
            'chat_history': [{
                'message': c.message,
                'response': c.response,
                'timestamp': c.timestamp.isoformat()
            } for c in chat_history],
            'generated_at': utc_now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500