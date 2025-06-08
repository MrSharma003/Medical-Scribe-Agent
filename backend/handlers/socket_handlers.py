import asyncio
from flask_socketio import emit
from services.medical_scribe_service import MedicalScribeService

class SocketHandlers:
    def __init__(self, socketio):
        self.socketio = socketio
        self.scribe_service = MedicalScribeService(socketio)  # Pass socketio for real-time updates
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all socket event handlers"""
        self.socketio.on_event('connect', self.handle_connect)
        self.socketio.on_event('disconnect', self.handle_disconnect)
        self.socketio.on_event('start_recording', self.handle_start_recording)
        self.socketio.on_event('audio_chunk', self.handle_audio_chunk)
        self.socketio.on_event('stop_recording', self.handle_stop_recording)
    
    def handle_connect(self):
        """Handle client connection"""
        print('Client connected')
        emit('connected', {'data': 'Connected to Medical Scribe Server'})
    
    def handle_disconnect(self):
        """Handle client disconnection"""
        print('Client disconnected')
    
    def handle_start_recording(self, data):
        """Handle start recording event"""
        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': 'Session ID is required'})
            return
        
        # Create new session
        session = self.scribe_service.create_session(session_id)
        result = self.scribe_service.start_recording(session_id)
        
        if result['success']:
            emit('recording_started', {
                'session_id': session_id,
                'status': 'Recording started - Real-time streaming transcription active'
            })
        else:
            emit('error', {'message': result.get('error', 'Failed to start recording')})
    
    def handle_audio_chunk(self, data):
        """Handle real-time audio chunk processing with streaming"""
        session_id = data.get('session_id')
        audio_data = data.get('audio_data')
        
        if not session_id or not audio_data:
            emit('error', {'message': 'Session ID and audio data are required'})
            return
        
        # Send chunk to streaming transcription - transcripts will be emitted automatically
        result = self.scribe_service.add_audio_chunk(session_id, audio_data)
        
        if not result['success']:
            emit('transcription_error', {
                'session_id': session_id, 
                'error': result.get('error', 'Unknown error')
            })
    
    def handle_stop_recording(self, data):
        """Handle stop recording and generate SOAP note"""
        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': 'Session ID is required'})
            return
        
        result = self.scribe_service.stop_recording(session_id)
        if result['success']:
            emit('recording_stopped', {
                'session_id': session_id,
                'transcript': result['transcript'],
                'status': 'Recording stopped, generating SOAP note...'
            })
            
            # Generate SOAP note in background
            self.socketio.start_background_task(self._generate_soap_note, session_id)
        else:
            emit('error', {'message': 'Failed to stop recording'})
    
    def _generate_soap_note(self, session_id):
        """Background task to generate SOAP note"""
        try:
            result = self.scribe_service.generate_soap_note(session_id)
            
            if result.success:
                self.socketio.emit('soap_note_complete', {
                    'session_id': session_id,
                    'soap_note': result.soap_note,
                    'status': 'SOAP note generated successfully'
                })
            else:
                self.socketio.emit('soap_generation_error', {
                    'session_id': session_id,
                    'error': result.error
                })
                
        except Exception as e:
            self.socketio.emit('soap_generation_error', {
                'session_id': session_id,
                'error': f"SOAP generation failed: {str(e)}"
            }) 