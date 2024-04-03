#!/bin/bash

DATA_SERVER_PORT=28462

chmod +x infrastructure/clients/data-server
chmod +x infrastructure/clients/data-server-arm64

# Start data server
if infrastructure/clients/data-server --port $DATA_SERVER_PORT > /dev/null 2>&1; then
    echo "Data server started successfully on port $DATA_SERVER_PORT"
    DATA_SERVER_PID=$!
else
    echo "Failed to start data server, trying alternative binary..."
    if infrastructure/clients/data-server-arm64 --port $DATA_SERVER_PORT > /dev/null 2>&1; then
        echo "Data server (arm64) started successfully on port $DATA_SERVER_PORT"
        DATA_SERVER_PID=$!
    else
        echo "Unable to start data server"
        exit 1
    fi
fi

# Wait for data server process to finish
wait $DATA_SERVER_PID
