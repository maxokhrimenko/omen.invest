#!/bin/bash

# Portfolio Analysis Tool - Stop Script
# This script stops all running instances of the Portfolio Analysis Tool

set -e  # Exit on any error

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

print_status "Stopping Portfolio Analysis Tool instances..."

# Stop backend processes
print_status "Stopping backend API server..."
if pkill -f "python api.py" 2>/dev/null; then
    print_success "Backend API server stopped"
else
    print_warning "No backend API server process found"
fi

# Stop uvicorn processes (alternative backend runner)
if pkill -f "uvicorn" 2>/dev/null; then
    print_success "Uvicorn processes stopped"
else
    print_warning "No uvicorn processes found"
fi

# Stop frontend development server
print_status "Stopping frontend development server..."
if pkill -f "npm run dev" 2>/dev/null; then
    print_success "Frontend development server stopped"
else
    print_warning "No frontend development server process found"
fi

# Stop vite processes (alternative frontend runner)
if pkill -f "vite" 2>/dev/null; then
    print_success "Vite processes stopped"
else
    print_warning "No vite processes found"
fi

# Stop node processes running vite
if pkill -f "node.*vite" 2>/dev/null; then
    print_success "Node vite processes stopped"
else
    print_warning "No node vite processes found"
fi

# Force kill any remaining processes
print_status "Force stopping any remaining processes..."
if pkill -9 -f "python api.py" 2>/dev/null; then
    print_success "Force stopped python api.py processes"
fi

if pkill -9 -f "uvicorn" 2>/dev/null; then
    print_success "Force stopped uvicorn processes"
fi

if pkill -9 -f "npm run dev" 2>/dev/null; then
    print_success "Force stopped npm run dev processes"
fi

if pkill -9 -f "vite" 2>/dev/null; then
    print_success "Force stopped vite processes"
fi

if pkill -9 -f "node.*vite" 2>/dev/null; then
    print_success "Force stopped node vite processes"
fi

# Stop any processes using common development ports
print_status "Checking for processes on common development ports..."

# Check port 8000 (backend)
if lsof -ti:8000 >/dev/null 2>&1; then
    print_warning "Port 8000 is still in use. Attempting to free it..."
    if lsof -ti:8000 | xargs kill -9 2>/dev/null; then
        print_success "Port 8000 freed"
    else
        print_error "Failed to free port 8000"
    fi
fi

# Check ports 3000, 5173-5180 (frontend)
for port in 3000 5173 5174 5175 5176 5177 5178 5179 5180; do
    if lsof -ti:$port >/dev/null 2>&1; then
        print_warning "Port $port is still in use. Attempting to free it..."
        if lsof -ti:$port | xargs kill -9 2>/dev/null; then
            print_success "Port $port freed"
        else
            print_error "Failed to free port $port"
        fi
    fi
done

# Final verification
print_status "Verifying all instances are stopped..."

# Check for any remaining processes
remaining_processes=$(ps aux | grep -E "(python api.py|npm run dev|vite|uvicorn)" | grep -v grep | wc -l)

if [ "$remaining_processes" -eq 0 ]; then
    print_success "All Portfolio Analysis Tool instances have been stopped"
else
    print_warning "Some processes may still be running:"
    ps aux | grep -E "(python api.py|npm run dev|vite|uvicorn)" | grep -v grep
fi

# Check if ports are free
print_status "Checking port availability..."

# Check backend port
if ! lsof -ti:8000 >/dev/null 2>&1; then
    print_success "Port 8000 (backend) is free"
else
    print_warning "Port 8000 is still in use"
fi

# Check frontend ports
free_ports=0
for port in 3000 5173 5174 5175 5176 5177 5178 5179 5180; do
    if ! lsof -ti:$port >/dev/null 2>&1; then
        free_ports=$((free_ports + 1))
    fi
done

if [ "$free_ports" -gt 0 ]; then
    print_success "Frontend ports are available (checked 3000, 5173-5180)"
else
    print_warning "Some frontend ports may still be in use"
fi

print_success "Stop script completed!"
print_status "You can now run './local/run.sh' to start the application again"
