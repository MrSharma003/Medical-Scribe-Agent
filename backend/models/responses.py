from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class APIResponse:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self):
        result = {'success': self.success}
        if self.data:
            result['data'] = self.data
        if self.error:
            result['error'] = self.error
        return result

@dataclass
class SOAPNoteResult:
    success: bool
    soap_note: str = ""
    error: Optional[str] = None 