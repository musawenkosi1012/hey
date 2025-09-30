from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.patient import Patient
from app.models.vitals import VitalSigns
from app.models.insights import ChatMessage
from app.services.chatbot import chatbot
from app.services.vitals_simulator import simulator
from app import db
from datetime import datetime, timedelta
import uuid

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
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
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
            timestamp=datetime.utcnow()
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
            'timestamp': datetime.utcnow().isoformat()
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