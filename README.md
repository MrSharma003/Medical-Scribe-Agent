# Medical Scribe Agent

AI-powered medical transcription with real-time speaker detection and SOAP note generation.

## Quick Start

**Run the entire application with one command:**

```bash
# Make the script executable (first time only)
chmod +x run-medical-scribe.sh

# Start the application
./run-medical-scribe.sh
```

That's it! The script will automatically:
- Install all dependencies
- Start both backend and frontend servers
- Open the application at http://localhost:3000

## Requirements

- Python 3.8+
- Node.js 16+
- API Keys (Deepgram and Google Gemini)

## Configuration

After first run, add your API keys to `backend/.env`:

```
DEEPGRAM_API_KEY=your_deepgram_api_key
GOOGLE_API_KEY=your_google_gemini_api_key
```

Get API keys:
- Deepgram: https://deepgram.com
- Google Gemini: https://aistudio.google.com/app/apikey

## Troubleshooting

- If script fails: `chmod +x run-medical-scribe.sh`
- Kill existing processes: Script handles this automatically
- Check console output for error details # Medical-Scribe-Agent
