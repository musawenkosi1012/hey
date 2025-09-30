from app import create_app, socketio
import logging

# Initialize logging before creating app
from app.logging_config import setup_logging
setup_logging()

logger = logging.getLogger(__name__)

logger.info("Creating Flask application")
app = create_app()

if __name__ == '__main__':
    logger.info("Starting SocketIO server on 0.0.0.0:5000")
    logger.info("Debug mode: True")
    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        raise