#!/bin/bash

MONGODB_PORT=6379
DATA_SERVER_PORT=28462
FASTAPI_APP_PORT=8000

# Check if MongoDB is installed
if ! command -v mongod &> /dev/null; then
    echo "MongoDB is not installed, installing..."
    sudo apt update
    sudo apt install -y mongodb
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
        echo "MongoDB started successfully on port 6379"
    else
        echo "Failed to start MongoDB server"
        exit 1
    fi
else
    echo "MongoDB is already running"
fi

# Create virtual environment
python3 -m venv myenv

# Activate virtual environment
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Define MongoDB variables
export MONGODB_CONNECTION_STRING="mongodb://localhost:${MONGODB_PORT}"
export MONGODB_DATABASE_NAME="open-cosmos"
export MONGODB_DATA_COLLECTION_NAME="data_collection"
export MONGODB_DISCARD_COLLECTION_NAME="data_invalidation_reasons"

# Start FastAPI application
uvicorn main:app --host 0.0.0.0 --port $FASTAPI_APP_PORT &

# Start data server
if ./infrastructure/clients/data-server --port $DATA_SERVER_PORT > /dev/null 2>&1; then
    echo "Data server started successfully on port 28462"
    DATA_SERVER_PID=$!
else
    echo "Failed to start data server, trying alternative binary..."
    if ./infrastructure/clients/data-server-arm64 --port $DATA_SERVER_PORT > /dev/null 2>&1; then
        echo "Data server (arm64) started successfully on port 28462"
        DATA_SERVER_PID=$!
    else
        echo "Unable to start data server"
        exit 1
    fi
fi

# Wait for data server process to finish
wait $DATA_SERVER_PID
