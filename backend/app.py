from app_factory import create_app
from config.settings import Config

# Create app and socketio
app, socketio = create_app(Config)

if __name__ == '__main__':
    socketio.run(
        app,
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT,
        allow_unsafe_werkzeug=True  # Allow development server
    ) 