from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.models.patient import Patient
from app import db
from datetime import date
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    logger.info("Login endpoint accessed")
    if current_user.is_authenticated:
        logger.info(f"User {current_user.username} already authenticated, redirecting to index")
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        logger.debug(f"Login attempt for username: {username}")
        
        if not username or not password:
            logger.warning("Login attempt with missing credentials")
            flash('Please provide both username and password.', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            logger.info(f"User {username} logged in successfully, role={user.role}")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'patient')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        # If patient, create patient profile
        if role == 'patient':
            first_name = request.form.get('first_name', username)
            last_name = request.form.get('last_name', '')
            dob = request.form.get('date_of_birth')
            gender = request.form.get('gender', 'other')
            
            # Parse date of birth
            try:
                if dob:
                    dob = date.fromisoformat(dob)
                else:
                    dob = date(1990, 1, 1)  # Default DOB
            except ValueError:
                dob = date(1990, 1, 1)
            
            patient = Patient(
                user_id=user.id,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                gender=gender
            )
            
            db.session.add(patient)
            db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    username = current_user.username
    logger.info(f"User {username} logging out")
    logout_user()
    flash('You have been logged out.', 'info')
    logger.info(f"User {username} logged out successfully")
    return redirect(url_for('main.index'))

# User loader for Flask-Login
from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    logger.debug(f"Loading user with id={user_id}")
    return User.query.get(int(user_id))