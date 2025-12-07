#!/bin/bash

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null
then
    echo "ngrok could not be found. Please install it first (brew install ngrok/ngrok/ngrok)."
    exit
fi

# Load env vars
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
fi

if [ -z "$NGROK_AUTH_TOKEN" ]; then
    echo "NGROK_AUTH_TOKEN is missing in .env"
    exit 1
fi

# Configure auth token
ngrok config add-authtoken $NGROK_AUTH_TOKEN

echo "----------------------------------------------------------------"
echo "Starting public tunnel to http://localhost:8000"
echo "Send the HTTPS link below to your friend."
echo "----------------------------------------------------------------"

# Start tunnel
ngrok http 8000
