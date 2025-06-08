from flask import Blueprint, jsonify
from services.gemini_service import GeminiService
from services.medical_scribe_service import MedicalScribeService

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize services
gemini_service = GeminiService()
scribe_service = MedicalScribeService()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@api_bp.route('/gemini-status', methods=['GET'])
def gemini_status():
    """Check if Gemini API is configured and working"""
    status = gemini_service.test_api_connection()
    return jsonify(status)

@api_bp.route('/get_session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session data"""
    session = scribe_service.get_session(session_id)
    if session:
        return jsonify(session.to_dict())
    else:
        return jsonify({'error': 'Session not found'}), 404

@api_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """List all active sessions"""
    sessions = [session.to_dict() for session in scribe_service.sessions.values()]
    return jsonify({"sessions": sessions}) 