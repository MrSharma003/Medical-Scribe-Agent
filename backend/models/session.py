from dataclasses import dataclass
from typing import Optional
from enum import Enum

class SessionStatus(Enum):
    READY = "ready"
    RECORDING = "recording"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class RecordingSession:
    session_id: str
    is_recording: bool = False
    transcript: str = ""
    soap_note: str = ""
    status: SessionStatus = SessionStatus.READY
    error_message: Optional[str] = None
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'transcript': self.transcript,
            'soap_note': self.soap_note,
            'is_recording': self.is_recording,
            'status': self.status.value,
            'error_message': self.error_message
        } 