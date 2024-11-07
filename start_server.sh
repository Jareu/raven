#!/bin/bash
# Check if the Flask app is running
if ! pgrep -f "python.*app.py" > /dev/null; then
    nohup python3 /home/jamie062/python/raven_server.py &
fi
