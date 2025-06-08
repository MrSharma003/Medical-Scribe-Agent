import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5001))
    
    # CORS settings
    CORS_ORIGINS = ["http://localhost:3000"]
    
    # API Keys
    DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    @classmethod
    def validate_config(cls):
        """Validate that required environment variables are set"""
        missing_vars = []
        
        if not cls.DEEPGRAM_API_KEY:
            missing_vars.append('DEEPGRAM_API_KEY')
        if not cls.GOOGLE_API_KEY:
            missing_vars.append('GOOGLE_API_KEY')
            
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}") 