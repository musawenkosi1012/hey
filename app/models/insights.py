from app import db
from datetime import datetime

class PatientInsight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    
    # Insight content
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    insight_type = db.Column(db.String(20), nullable=False)  # daily, weekly, alert
    
    # AI generation metadata
    generated_by_ai = db.Column(db.Boolean, default=True)
    ai_model = db.Column(db.String(50), default='gpt-3.5-turbo')
    
    # Data period this insight covers
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    severity = db.Column(db.String(20), default='info')  # info, warning, critical
    
    def __repr__(self):
        return f'<PatientInsight {self.insight_type}: {self.title}>'

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    
    # Message content
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    
    # Context used for response
    vitals_context = db.Column(db.Text, nullable=True)  # JSON of relevant vitals
    
    # Metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<ChatMessage Patient:{self.patient_id} Time:{self.timestamp}>'