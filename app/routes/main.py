from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.patient import Patient
from app.models.vitals import VitalSigns
from app.models.insights import PatientInsight
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        if current_user.role == 'patient':
            return redirect(url_for('main.patient_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor.dashboard'))
        else:
            return redirect(url_for('main.caregiver_dashboard'))
    
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def patient_dashboard():
    """Patient dashboard with real-time vitals"""
    if current_user.role != 'patient':
        return redirect(url_for('main.index'))
    
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found. Please contact support.', 'error')
        return redirect(url_for('main.index'))
    
    # Get recent vitals (last 24 hours)
    recent_vitals = VitalSigns.query.filter(
        VitalSigns.patient_id == patient.id,
        VitalSigns.timestamp >= datetime.utcnow() - timedelta(hours=24)
    ).order_by(VitalSigns.timestamp.desc()).limit(50).all()
    
    # Get latest vital signs
    latest_vitals = recent_vitals[0] if recent_vitals else None
    
    # Get recent insights
    recent_insights = PatientInsight.query.filter_by(
        patient_id=patient.id
    ).order_by(PatientInsight.created_at.desc()).limit(5).all()
    
    # Calculate daily stats
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_vitals = [v for v in recent_vitals if v.timestamp >= today_start]
    
    daily_stats = {}
    if today_vitals:
        daily_stats = {
            'avg_bp_sys': sum(v.systolic_bp for v in today_vitals if v.systolic_bp) / len([v for v in today_vitals if v.systolic_bp]) if any(v.systolic_bp for v in today_vitals) else 0,
            'avg_bp_dia': sum(v.diastolic_bp for v in today_vitals if v.diastolic_bp) / len([v for v in today_vitals if v.diastolic_bp]) if any(v.diastolic_bp for v in today_vitals) else 0,
            'avg_hr': sum(v.heart_rate for v in today_vitals if v.heart_rate) / len([v for v in today_vitals if v.heart_rate]) if any(v.heart_rate for v in today_vitals) else 0,
            'total_steps': sum(v.steps for v in today_vitals if v.steps),
            'avg_spo2': sum(v.spo2 for v in today_vitals if v.spo2) / len([v for v in today_vitals if v.spo2]) if any(v.spo2 for v in today_vitals) else 0
        }
    
    return render_template('dashboard/patient.html', 
                         patient=patient,
                         latest_vitals=latest_vitals,
                         recent_vitals=recent_vitals,
                         recent_insights=recent_insights,
                         daily_stats=daily_stats)

@bp.route('/chatbot')
@login_required
def chatbot_page():
    """AI Health Coach chatbot page"""
    if current_user.role != 'patient':
        return redirect(url_for('main.index'))
    
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('chatbot/chat.html', patient=patient)

@bp.route('/electrobook')
@login_required
def electrobook():
    """Electro-book insights page"""
    if current_user.role != 'patient':
        return redirect(url_for('main.index'))
    
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Get insights by type
    daily_insights = PatientInsight.query.filter_by(
        patient_id=patient.id,
        insight_type='daily'
    ).order_by(PatientInsight.created_at.desc()).limit(7).all()
    
    weekly_insights = PatientInsight.query.filter_by(
        patient_id=patient.id,
        insight_type='weekly'
    ).order_by(PatientInsight.created_at.desc()).limit(4).all()
    
    return render_template('electrobook/insights.html',
                         patient=patient,
                         daily_insights=daily_insights,
                         weekly_insights=weekly_insights)

@bp.route('/vitals')
@login_required
def vitals_history():
    """Detailed vitals history page"""
    if current_user.role != 'patient':
        return redirect(url_for('main.index'))
    
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Get date range from query params
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    vitals = VitalSigns.query.filter(
        VitalSigns.patient_id == patient.id,
        VitalSigns.timestamp >= start_date
    ).order_by(VitalSigns.timestamp.desc()).all()
    
    return render_template('vitals/history.html',
                         patient=patient,
                         vitals=vitals,
                         days=days)

@bp.route('/caregiver')
@login_required
def caregiver_dashboard():
    """Caregiver dashboard"""
    if current_user.role != 'caregiver':
        return redirect(url_for('main.index'))
    
    # For now, show basic info - in a real app, this would be linked to specific patients
    return render_template('dashboard/caregiver.html')