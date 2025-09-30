from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models.patient import Patient
from app.models.vitals import VitalSigns, RiskPrediction
from app.models.insights import PatientInsight
from app.models.user import User
from app.services.chatbot import chatbot
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@bp.route('/')
@login_required
def chat_interface():
    """Main chat interface"""
    if current_user.role != 'patient':
        return redirect(url_for('main.index'))
    
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return redirect(url_for('main.index'))
    
    return render_template('chatbot/interface.html', patient=patient)