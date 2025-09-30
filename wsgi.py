"""
WSGI entry point for production deployment
Used by gunicorn to serve the application
"""
import os
import logging
from app import create_app, socketio

# Setup logging before creating app
from app.logging_config import setup_logging
setup_logging()

logger = logging.getLogger(__name__)

# Create the Flask application
logger.info("Creating Flask application for production")
app = create_app()

# For gunicorn with eventlet (SocketIO support)
# gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT wsgi:app

if __name__ == "__main__":
    # This block is used for local testing with socketio.run
    # In production, gunicorn will use the 'app' object directly
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting SocketIO server on 0.0.0.0:{port}")
    socketio.run(app, host='0.0.0.0', port=port)
