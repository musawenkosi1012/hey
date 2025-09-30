from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models.patient import Patient
from app.models.vitals import VitalSigns, RiskPrediction
from app.models.insights import PatientInsight
from app.models.user import User
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Doctor dashboard"""
    if current_user.role != 'doctor':
        return redirect(url_for('main.index'))
    
    # Get all patients
    patients = Patient.query.join(User).all()
    
    # Get patients with recent alerts
    recent_alerts = VitalSigns.query.filter(
        VitalSigns.is_anomaly == True,
        VitalSigns.timestamp >= datetime.utcnow() - timedelta(hours=24)
    ).join(Patient).all()
    
    # Get recent insights that need review
    pending_insights = PatientInsight.query.filter(
        PatientInsight.severity.in_(['warning', 'critical']),
        PatientInsight.created_at >= datetime.utcnow() - timedelta(days=7)
    ).join(Patient).all()
    
    return render_template('doctor/dashboard.html',
                         patients=patients,
                         recent_alerts=recent_alerts,
                         pending_insights=pending_insights)

@bp.route('/patient/<int:patient_id>')
@login_required
def patient_detail(patient_id):
    """Detailed view of a specific patient"""
    if current_user.role != 'doctor':
        return redirect(url_for('main.index'))
    
    patient = Patient.query.get_or_404(patient_id)
    
    # Get recent vitals (last 7 days)
    recent_vitals = VitalSigns.query.filter(
        VitalSigns.patient_id == patient_id,
        VitalSigns.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).order_by(VitalSigns.timestamp.desc()).all()
    
    # Get latest risk prediction
    latest_risk = RiskPrediction.query.filter_by(
        patient_id=patient_id
    ).order_by(RiskPrediction.created_at.desc()).first()
    
    # Get insights
    insights = PatientInsight.query.filter_by(
        patient_id=patient_id
    ).order_by(PatientInsight.created_at.desc()).limit(10).all()
    
    # Calculate weekly averages
    week_start = datetime.utcnow() - timedelta(days=7)
    week_vitals = [v for v in recent_vitals if v.timestamp >= week_start]
    
    weekly_stats = {}
    if week_vitals:
        weekly_stats = {
            'avg_bp_sys': sum(v.systolic_bp for v in week_vitals if v.systolic_bp) / len([v for v in week_vitals if v.systolic_bp]) if any(v.systolic_bp for v in week_vitals) else 0,
            'avg_bp_dia': sum(v.diastolic_bp for v in week_vitals if v.diastolic_bp) / len([v for v in week_vitals if v.diastolic_bp]) if any(v.diastolic_bp for v in week_vitals) else 0,
            'avg_hr': sum(v.heart_rate for v in week_vitals if v.heart_rate) / len([v for v in week_vitals if v.heart_rate]) if any(v.heart_rate for v in week_vitals) else 0,
            'avg_spo2': sum(v.spo2 for v in week_vitals if v.spo2) / len([v for v in week_vitals if v.spo2]) if any(v.spo2 for v in week_vitals) else 0,
            'total_steps': sum(v.steps for v in week_vitals if v.steps),
            'anomaly_count': len([v for v in week_vitals if v.is_anomaly])
        }
    
    return render_template('doctor/patient_detail.html',
                         patient=patient,
                         recent_vitals=recent_vitals,
                         latest_risk=latest_risk,
                         insights=insights,
                         weekly_stats=weekly_stats)

@bp.route('/patients')
@login_required
def patients_list():
    """List all patients"""
    if current_user.role != 'doctor':
        return redirect(url_for('main.index'))
    
    patients = Patient.query.join(User).all()
    
    # Add latest vitals for each patient
    patients_with_vitals = []
    for patient in patients:
        latest_vitals = VitalSigns.query.filter_by(
            patient_id=patient.id
        ).order_by(VitalSigns.timestamp.desc()).first()
        
        latest_risk = RiskPrediction.query.filter_by(
            patient_id=patient.id
        ).order_by(RiskPrediction.created_at.desc()).first()
        
        patients_with_vitals.append({
            'patient': patient,
            'latest_vitals': latest_vitals,
            'latest_risk': latest_risk
        })
    
    return render_template('doctor/patients_list.html',
                         patients_with_vitals=patients_with_vitals)