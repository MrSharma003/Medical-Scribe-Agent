import google.generativeai as genai
from models.responses import SOAPNoteResult
from config.settings import Config

class GeminiService:
    def __init__(self):
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Configure generation parameters for medical content
        self.generation_config = genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=2000,
            temperature=0.3,
        )
        
        # Safety settings for medical content
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
    
    def generate_soap_note(self, transcript: str) -> SOAPNoteResult:
        """Generate SOAP note from transcript using Google Gemini"""
        try:
            prompt = self._create_soap_prompt(transcript)
            print("----------------CHecking gemini API", transcript)
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            if response.text:
                return SOAPNoteResult(
                    success=True,
                    soap_note=response.text
                )
            else:
                return SOAPNoteResult(
                    success=False,
                    error="No response generated from Gemini API"
                )
                
        except Exception as e:
            error_message = self._handle_gemini_error(str(e))
            return SOAPNoteResult(
                success=False,
                error=error_message
            )
    
    def test_api_connection(self) -> dict:
        """Test Gemini API connection"""
        try:
            test_model = genai.GenerativeModel('gemini-1.5-flash')
            response = test_model.generate_content(
                "Respond with 'API Working' if you can see this message.",
                generation_config=genai.types.GenerationConfig(max_output_tokens=10)
            )
            
            if response.text and "API Working" in response.text:
                return {
                    "status": "working",
                    "model": "gemini-1.5-flash",
                    "message": "Gemini API is configured and working"
                }
            else:
                return {
                    "status": "error", 
                    "message": "Gemini API responded but with unexpected content"
                }
                
        except Exception as e:
            error_message = self._handle_gemini_error(str(e))
            return {
                "status": "error",
                "message": error_message
            }
    
    def _create_soap_prompt(self, transcript: str) -> str:
        """Create the prompt for SOAP note generation"""
        return f"""
You are a medical documentation assistant specializing in creating accurate SOAP notes from doctor-patient conversations.

Based on the following medical conversation transcript between a doctor and patient, create a professional SOAP note.

SOAP Format:
- SUBJECTIVE: Patient's symptoms, complaints, and history in their own words
- OBJECTIVE: Observable, measurable findings (vital signs, physical exam, test results)
- ASSESSMENT: Medical diagnosis or clinical impression
- PLAN: Treatment plan, medications, follow-up instructions

Transcript:
{transcript}

Please format the SOAP note professionally with clear sections. If any section lacks information from the transcript, note "Not documented in visit" for that section.

Create a well-structured SOAP note now:
"""
    
    def _handle_gemini_error(self, error_message: str) -> str:
        """Handle and format Gemini API errors"""
        if "API_KEY" in error_message.upper():
            return "Invalid or missing Google API key. Please check your GOOGLE_API_KEY in .env file."
        elif "QUOTA" in error_message.upper():
            return "API quota exceeded. Please check your Gemini API usage limits."
        elif "SAFETY" in error_message.upper():
            return "Content was blocked by safety filters. This may happen with medical content."
        elif "PERMISSION_DENIED" in error_message.upper():
            return "API key doesn't have permission to use Gemini"
        else:
            return f"Gemini API error: {error_message}" 