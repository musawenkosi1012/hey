from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

logger = logging.getLogger(__name__)

def create_app():
    logger.info("Starting Flask application creation")
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///chronisense.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    logger.info(f"Database URI configured: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Setup logging
    from app.logging_config import setup_logging
    setup_logging(app)
    
    # Initialize extensions
    logger.info("Initializing Flask extensions")
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    CORS(app)
    logger.info("Flask extensions initialized successfully")
    
    # Login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Import models
    logger.info("Importing database models")
    from app.models import user, patient, vitals, insights
    logger.info("Database models imported successfully")
    
    # Register blueprints
    logger.info("Registering application blueprints")
    from app.routes import main, auth, api, chatbot, doctor
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(chatbot.bp)
    app.register_blueprint(doctor.bp)
    logger.info("All blueprints registered successfully")
    
    logger.info("Flask application created successfully")
    return app