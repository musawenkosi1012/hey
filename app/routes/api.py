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

# Helper function for naive UTC datetime (for DB compatibility)
def utc_now():
    return datetime.utcnow()

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/vitals/<int:patient_id>')
@login_required
def get_vitals(patient_id):
    """Get vitals data for a patient"""
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
            'tips': tips,
            'category': category
        })
        
    except Exception as e:
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
        
        report = {
            'success': True,
            'patient': {
                'id': patient.id,
                'name': f"{patient.first_name} {patient.last_name}",
                'age': age,
                'date_of_birth': patient.date_of_birth.isoformat(),
                'gender': patient.gender,
                'conditions': patient.conditions
            },
            'period': {
                'days': days,
                'start_date': start_date.isoformat(),
                'end_date': utc_now().isoformat()
            },
            'statistics': stats,
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