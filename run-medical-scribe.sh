#!/bin/bash

# Medical Scribe Agent - One-Click Setup & Run Script
# This script installs all dependencies and runs both backend and frontend

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project info
PROJECT_NAME="Medical Scribe Agent"
BACKEND_PORT=5001
FRONTEND_PORT=3000

echo -e "${BLUE}🏥 ${PROJECT_NAME} - One-Click Setup & Run${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 1
    else
        return 0
    fi
}

# Function to kill processes on ports
cleanup_ports() {
    echo -e "${YELLOW}🧹 Cleaning up any existing processes...${NC}"
    
    # Kill processes on backend port
    if ! check_port $BACKEND_PORT; then
        print_warning "Killing process on port $BACKEND_PORT"
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
    fi
    
    # Kill processes on frontend port  
    if ! check_port $FRONTEND_PORT; then
        print_warning "Killing process on port $FRONTEND_PORT"
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
    fi
    
    sleep 2
}

# Function to setup backend
setup_backend() {
    echo -e "${BLUE}🐍 Setting up Python Backend...${NC}"
    
    cd backend
    
    # Check Python version
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed. Please install Python 3.8+ and try again."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_status "Using Python $PYTHON_VERSION"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
    else
        print_warning "requirements.txt not found, installing basic dependencies..."
        pip install flask flask-socketio flask-cors deepgram-sdk google-generativeai python-dotenv
    fi
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_warning "Creating .env file template..."
        cat > .env << EOL
# Deepgram API Configuration
DEEPGRAM_API_KEY=api-key

# Google Gemini API Configuration  
GOOGLE_API_KEY=api-key

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# CORS Settings
FRONTEND_URL=http://localhost:3000
EOL
        print_warning "⚠️  Please edit backend/.env with your API keys!"
    fi
    
    cd ..
    print_status "Backend setup complete!"
}

# Function to setup frontend
setup_frontend() {
    echo -e "${BLUE}⚛️  Setting up React Frontend...${NC}"
    
    cd frontend
    
    # Check Node.js
    if ! command_exists node; then
        print_error "Node.js is required but not installed. Please install Node.js 16+ and try again."
        exit 1
    fi
    
    NODE_VERSION=$(node -v)
    print_status "Using Node.js $NODE_VERSION"
    
    # Check npm
    if ! command_exists npm; then
        print_error "npm is required but not installed. Please install npm and try again."
        exit 1
    fi
    
    # Install dependencies
    if [ -f "package.json" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
    else
        print_warning "package.json not found, creating React app..."
        npx create-react-app . --template typescript
        npm install socket.io-client
    fi
    
    cd ..
    print_status "Frontend setup complete!"
}

# Function to start backend
start_backend() {
    echo -e "${BLUE}🚀 Starting Python Backend Server...${NC}"
    
    cd backend
    source venv/bin/activate
    
    # Check if .env has API keys
    if grep -q "your_.*_api_key_here" .env 2>/dev/null; then
        print_warning "API keys not configured in backend/.env"
        print_warning "The backend will start but transcription and AI features won't work until you add your API keys."
    fi
    
    export FLASK_APP=app.py
    export FLASK_ENV=development
    
    print_status "Backend server starting on http://localhost:$BACKEND_PORT"
    python app.py &
    BACKEND_PID=$!
    
    cd ..
    
    # Wait for backend to start
    echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"
    for i in {1..30}; do
        if check_port $BACKEND_PORT; then
            sleep 1
        else
            print_status "Backend server is running!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend failed to start within 30 seconds"
            exit 1
        fi
    done
}

# Function to start frontend
start_frontend() {
    echo -e "${BLUE}🌐 Starting React Frontend Server...${NC}"
    
    cd frontend
    
    print_status "Frontend server starting on http://localhost:$FRONTEND_PORT"
    npm start &
    FRONTEND_PID=$!
    
    cd ..
    
    # Wait for frontend to start
    echo -e "${YELLOW}⏳ Waiting for frontend to start...${NC}"
    for i in {1..60}; do
        if check_port $FRONTEND_PORT; then
            sleep 1
        else
            print_status "Frontend server is running!"
            break
        fi
        if [ $i -eq 60 ]; then
            print_error "Frontend failed to start within 60 seconds"
            exit 1
        fi
    done
}

# Function to show completion message
show_completion() {
    echo -e "\n${GREEN}🎉 ${PROJECT_NAME} is now running!${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}📱 Frontend: ${BLUE}http://localhost:$FRONTEND_PORT${NC}"
    echo -e "${GREEN}🔧 Backend:  ${BLUE}http://localhost:$BACKEND_PORT${NC}"
    echo -e "\n${YELLOW}📝 Next Steps:${NC}"
    echo -e "1. Add your API keys to ${BLUE}backend/.env${NC}"
    echo -e "   - Get Deepgram API key: https://deepgram.com"
    echo -e "   - Get Google API key: https://aistudio.google.com/app/apikey"
    echo -e "2. Open ${BLUE}http://localhost:$FRONTEND_PORT${NC} in your browser"
    echo -e "3. Start recording medical conversations!"
    echo -e "\n${YELLOW}💡 To stop the servers, press Ctrl+C${NC}"
}

# Cleanup function for graceful shutdown
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    cleanup_ports
    
    echo -e "${GREEN}👋 Goodbye!${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    # Check if we're in the right directory
    if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        print_error "This script must be run from the project root directory"
        print_error "Make sure you have both 'backend' and 'frontend' directories"
        exit 1
    fi
    
    # Cleanup any existing processes
    cleanup_ports
    
    # Setup phase
    echo -e "${BLUE}📦 Installing Dependencies...${NC}"
    setup_backend
    setup_frontend
    
    # Start servers
    echo -e "\n${BLUE}🚀 Starting Servers...${NC}"
    start_backend
    start_frontend
    
    # Show completion message
    show_completion
    
    # Keep script running
    echo -e "\n${BLUE}🔄 Servers are running. Press Ctrl+C to stop.${NC}"
    wait
}

# Run main function
main 
