#!/bin/bash

MONGODB_PORT=6379
DATA_SERVER_PORT=28462
FASTAPI_APP_PORT=8000

# Check if MongoDB is installed
if ! command -v mongod &> /dev/null; then
    echo "MongoDB is not installed, attempting to install..."

    # try using brew (for macOS)
    if command -v brew &> /dev/null; then
        brew tap mongodb/brew
        brew install mongodb-community
    # Check if the system has apt package manager
    elif command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y mongodb
    # If apt is not available, check if yum is available
    elif command -v yum &> /dev/null; then
        sudo yum install -y mongodb-org
    # If none of the package managers are available, prompt the user to visit the MongoDB website for installation instructions
    else
        echo "Error: Unable to locate apt, yum, or brew package manager. Please visit the MongoDB website for installation instructions."
        exit 1
    fi
else
    echo "MongoDB is already installed"
fi

# Start MongoDB if not already running
if ! pgrep mongod &> /dev/null; then
    echo "Starting MongoDB server in the background..."
    mkdir -p ~/mongodb-data
    mongod --port $MONGODB_PORT --dbpath ~/mongodb-data --fork --logpath ~/mongodb.log
    sleep 3  # Wait for MongoDB to start

    # Check if MongoDB is running after starting
    if pgrep mongod &> /dev/null; then
        echo "MongoDB started successfully on port $MONGODB_PORT"
    else
        echo "Failed to start MongoDB server"
        exit 1
    fi
else
    echo "MongoDB is already running"
fi

# Create virtual environment
python3 -m venv myenv || {
    echo "Failed to create virtual environment. Please ensure Python 3 and venv are installed."
    exit 1
}

# Activate virtual environment
source myenv/bin/activate || {
    echo "Failed to activate virtual environment."
    exit 1
}

# Install dependencies
pip install -r requirements.txt || {
    echo "Failed to install dependencies."
    exit 1
}

# Define MongoDB variables
export MONGODB_CONNECTION_STRING="mongodb://localhost:${MONGODB_PORT}"
export MONGODB_DATABASE_NAME="open-cosmos"
export MONGODB_DATA_COLLECTION_NAME="data_collection"
export MONGODB_DISCARD_COLLECTION_NAME="data_invalidation_reasons"

# Start FastAPI application
uvicorn main:app --host 0.0.0.0 --port $FASTAPI_APP_PORT &

# Start data server
if ./infrastructure/clients/data-server --port $DATA_SERVER_PORT > /dev/null 2>&1; then
    echo "Data server started successfully on port $DATA_SERVER_PORT"
    DATA_SERVER_PID=$!
else
    echo "Failed to start data server, trying alternative binary..."
    if ./infrastructure/clients/data-server-arm64 --port $DATA_SERVER_PORT > /dev/null 2>&1; then
        echo "Data server (arm64) started successfully on port $DATA_SERVER_PORT"
        DATA_SERVER_PID=$!
    else
        echo "Unable to start data server"
        exit 1
    fi
fi

# Wait for data server process to finish
wait $DATA_SERVER_PID
