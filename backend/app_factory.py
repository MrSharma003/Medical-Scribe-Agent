from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from config.settings import Config
from routes.api_routes import api_bp
from handlers.socket_handlers import SocketHandlers

def create_app(config_class=Config):
    """Application factory pattern"""
    # Validate configuration
    config_class.validate_config()
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config_class.SECRET_KEY
    
    # Setup CORS
    CORS(app, origins=config_class.CORS_ORIGINS)
    
    # Setup SocketIO
    socketio = SocketIO(app, cors_allowed_origins=config_class.CORS_ORIGINS)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Initialize socket handlers
    SocketHandlers(socketio)
    
    return app, socketio 