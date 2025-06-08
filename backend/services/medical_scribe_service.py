import base64
from typing import Dict
from models.session import RecordingSession, SessionStatus
from models.responses import  SOAPNoteResult
from services.deepgram_service import DeepgramService
from services.gemini_service import GeminiService

class MedicalScribeService:
    def __init__(self, socketio=None):
        self.sessions: Dict[str, RecordingSession] = {}
        self.deepgram_service = DeepgramService()
        self.gemini_service = GeminiService()
        self.socketio = socketio
    
    def create_session(self, session_id: str) -> RecordingSession:
        """Create a new recording session"""
        session = RecordingSession(
            session_id=session_id,
            is_recording=False,
            transcript="",
            soap_note="",
            status=SessionStatus.READY
        )
        self.sessions[session_id] = session
        return session
    
    def start_recording(self, session_id: str) -> Dict[str, any]:
        """Start recording for a session using streaming transcription"""
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}
        
        # Define callback for streaming transcripts
        def on_transcript_received(transcript_data):
            """Callback when new transcript is received from streaming"""
            # Handle both old format (string) and new format (dict) for backward compatibility
            if isinstance(transcript_data, dict):
                transcript_chunk = transcript_data.get('formatted_text', '')
                full_transcript = transcript_data.get('full_transcript', '')
                speaker = transcript_data.get('speaker')
                raw_text = transcript_data.get('text', '')
            else:
                # Legacy format support
                transcript_chunk = transcript_data
                full_transcript = session.transcript + " " + transcript_chunk
                speaker = None
                raw_text = transcript_data
            
            session.transcript = full_transcript.strip()
            print(f"Updated session transcript: {len(session.transcript)} characters")
            
            # Emit real-time transcript update to frontend with speaker info
            if self.socketio and transcript_chunk.strip():
                self.socketio.emit('live_transcription', {
                    'session_id': session_id,
                    'transcript_chunk': transcript_chunk.strip(),
                    'raw_text': raw_text.strip(),
                    'speaker': speaker,
                    'full_transcript': session.transcript
                })
        
        # Start Deepgram streaming session
        streaming_started = self.deepgram_service.start_streaming_session(
            session_id, 
            on_transcript_received
        )
        
        if streaming_started:
            session.is_recording = True
            session.status = SessionStatus.RECORDING
            print(f"Started streaming recording for session: {session_id}")
            return {"success": True}
        else:
            return {"success": False, "error": "Failed to start streaming session"}
    
    def add_audio_chunk(self, session_id: str, audio_data: str) -> Dict[str, any]:
        """Send PCM audio chunk to streaming transcription"""
        session = self.get_session(session_id)
        if not session or not session.is_recording:
            return {"success": False, "error": "Session not recording"}
        
        try:
            # Decode the base64 PCM audio data
            audio_bytes = base64.b64decode(audio_data.split(',')[1] if ',' in audio_data else audio_data)
            
            print(f"Sending PCM chunk to streaming: {len(audio_bytes)} bytes")
            
            # Send raw PCM bytes to streaming connection
            success = self.deepgram_service.send_audio_chunk_to_stream(session_id, audio_bytes)
            
            if success:
                return {
                    "success": True,
                    "total_transcript": session.transcript
                }
            else:
                return {"success": False, "error": "Failed to send audio to streaming"}
            
        except Exception as e:
            print(f"Error processing PCM audio chunk: {e}")
            return {"success": False, "error": str(e)}
    
    def stop_recording(self, session_id: str) -> Dict[str, any]:
        """Stop recording and streaming session"""
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}
        
        session.is_recording = False
        session.status = SessionStatus.PROCESSING
        
        # Stop streaming session and get final transcript
        final_transcript = self.deepgram_service.stop_streaming_session(session_id)
        if final_transcript:
            session.transcript = final_transcript.strip()
        
        print(f"Recording stopped for session: {session_id}")
        print(f"Final transcript length: {len(session.transcript)} characters")
        
        return {
            "success": True, 
            "transcript": session.transcript,
            "message": "Recording stopped, ready for SOAP note generation"
        }
    
    def generate_soap_note(self, session_id: str) -> SOAPNoteResult:
        """Generate SOAP note from accumulated transcript"""
        session = self.get_session(session_id)
        if not session:
            return SOAPNoteResult(success=False, error="Session not found")
        
        if not session.transcript.strip():
            return SOAPNoteResult(success=False, error="No transcript available for SOAP note generation")
        
        session.status = SessionStatus.PROCESSING
        
        try:
            print(f"Generating SOAP note for {len(session.transcript)} characters of transcript")
            result = self.gemini_service.generate_soap_note(session.transcript)
            
            if result.success:
                session.soap_note = result.soap_note
                session.status = SessionStatus.COMPLETED
                print("SOAP note generated successfully")
            else:
                session.status = SessionStatus.ERROR
                print(f"SOAP note generation failed: {result.error}")
            
            return result
            
        except Exception as e:
            session.status = SessionStatus.ERROR
            error_msg = f"Error generating SOAP note: {str(e)}"
            print(error_msg)
            return SOAPNoteResult(success=False, error=error_msg)
    
    def get_session(self, session_id: str) -> RecordingSession:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def cleanup_session(self, session_id: str) -> bool:
        """Clean up session resources"""
        try:
            # Stop streaming session if still active
            self.deepgram_service.stop_streaming_session(session_id)
            
            if session_id in self.sessions:
                del self.sessions[session_id]
            print(f"Session {session_id} cleaned up")
            return True
        except Exception as e:
            print(f"Error cleaning up session: {e}")
            return False 