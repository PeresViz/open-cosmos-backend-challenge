#!/bin/bash

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "Redis is not installed, installing..."
    sudo apt update
    sudo apt install redis-server
else
    echo "Redis is already installed"
fi

# Start Redis server if not already running
if ! pgrep redis-server &> /dev/null; then
    echo "Starting Redis server in the background..."
    redis-server --port 6379 --daemonize yes &>/dev/null &
    sleep 3  # Wait for Redis to start

    # Check if Redis is running after starting
    if pgrep redis-server &> /dev/null; then
        echo "Redis started successfully on port 6379"
    else
        echo "Failed to start Redis server"
        exit 1
    fi
else
    echo "Redis is already running"
fi

# Create virtual environment
python3 -m venv myenv

# Activate virtual environment
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start data server
if ./infrastructure/clients/data-server --port 28462 > /dev/null 2>&1; then
    echo "Data server started successfully on port 28462"
    DATA_SERVER_PID=$!
else
    echo "Failed to start data server, trying alternative binary..."
    if ./infrastructure/clients/data-server-arm64 --port 28462 > /dev/null 2>&1; then
        echo "Data server (arm64) started successfully on port 28462"
        DATA_SERVER_PID=$!
    else
        echo "Unable to start data server"
        exit 1
    fi
fi

# Wait for data server process to finish
wait $DATA_SERVER_PID
