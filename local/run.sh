#!/bin/bash

# Portfolio Analysis Tool - Local Development Runner
# This script starts both the backend API and frontend development server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to kill processes on specific ports
kill_port() {
    if port_in_use $1; then
        print_warning "Port $1 is in use. Attempting to free it..."
        lsof -ti :$1 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}
``
# Function to start backend
start_backend() {
    print_status "Starting backend API server..."
    
    # Check if Python virtual environment exists
    if [ ! -d "venv" ]; then
        print_error "Python virtual environment not found. Please run setup first."
        exit 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if required packages are installed
    if ! python -c "import fastapi" 2>/dev/null; then
        print_warning "FastAPI not found. Installing required packages..."
        pip install fastapi uvicorn python-multipart
    fi
    
    # Kill any existing process on port 8000
    kill_port 8000
    
    # Start backend server
    print_status "Starting backend on http://localhost:8000"
    cd backend
    python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    
    # Check if backend started successfully
    if port_in_use 8000; then
        print_success "Backend started successfully (PID: $BACKEND_PID)"
    else
        print_error "Failed to start backend server"
        exit 1
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend development server..."
    
    # Check if frontend directory exists
    if [ ! -d "frontend" ]; then
        print_error "Frontend directory not found. Please run setup first."
        exit 1
    fi
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "Node modules not found. Installing dependencies..."
        npm install
    fi
    
    # Kill any existing process on port 3000
    kill_port 3000
    
    # Start frontend server
    print_status "Starting frontend on http://localhost:3000"
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # Wait a moment for frontend to start
    sleep 3
    
    # Check if frontend started successfully
    if port_in_use 3000; then
        print_success "Frontend started successfully (PID: $FRONTEND_PID)"
    else
        print_error "Failed to start frontend server"
        exit 1
    fi
}

# Function to setup the project
setup_project() {
    print_status "Setting up Portfolio Analysis Tool for local development..."
    
    # Check if Python is installed
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi
    
    # Check if Node.js is installed
    if ! command_exists node; then
        print_error "Node.js is required but not installed."
        exit 1
    fi
    
    # Check if npm is installed
    if ! command_exists npm; then
        print_error "npm is required but not installed."
        exit 1
    fi
    
    # Setup backend
    print_status "Setting up backend..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r backend/requirements.txt
    pip install fastapi uvicorn python-multipart
    
    # Setup frontend (if it exists)
    if [ -d "frontend" ]; then
        print_status "Setting up frontend..."
        cd frontend
        npm install
        cd ..
    else
        print_warning "Frontend directory not found. Skipping frontend setup."
    fi
    
    print_success "Project setup completed!"
}

# Function to stop all services
stop_services() {
    print_status "Stopping all services..."
    
    # Kill backend
    if port_in_use 8000; then
        lsof -ti :8000 | xargs kill -9 2>/dev/null || true
        print_success "Backend stopped"
    fi
    
    # Kill frontend
    if port_in_use 3000; then
        lsof -ti :3000 | xargs kill -9 2>/dev/null || true
        print_success "Frontend stopped"
    fi
}

# Function to show status
show_status() {
    print_status "Service Status:"
    
    if port_in_use 8000; then
        print_success "Backend: Running on http://localhost:8000"
    else
        print_warning "Backend: Not running"
    fi
    
    if port_in_use 3000; then
        print_success "Frontend: Running on http://localhost:3000"
    else
        print_warning "Frontend: Not running"
    fi
}

# Function to show help
show_help() {
    echo "Portfolio Analysis Tool - Local Development Runner"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start both backend and frontend servers"
    echo "  backend   Start only the backend server"
    echo "  frontend  Start only the frontend server"
    echo "  stop      Stop all running services"
    echo "  status    Show status of running services"
    echo "  setup     Setup the project for development"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start     # Start both servers"
    echo "  $0 backend   # Start only backend"
    echo "  $0 stop      # Stop all services"
}

# Main script logic
case "${1:-start}" in
    "start")
        print_status "Starting Portfolio Analysis Tool..."
        start_backend
        start_frontend
        print_success "All services started!"
        print_status "Backend API: http://localhost:8000"
        print_status "Frontend App: http://localhost:3000"
        print_status "Press Ctrl+C to stop all services"
        
        # Wait for user interrupt
        trap 'stop_services; exit 0' INT
        wait
        ;;
    "backend")
        start_backend
        print_status "Backend running on http://localhost:8000"
        print_status "Press Ctrl+C to stop"
        wait $BACKEND_PID
        ;;
    "frontend")
        start_frontend
        print_status "Frontend running on http://localhost:3000"
        print_status "Press Ctrl+C to stop"
        wait $FRONTEND_PID
        ;;
    "stop")
        stop_services
        ;;
    "status")
        show_status
        ;;
    "setup")
        setup_project
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
