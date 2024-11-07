#!/bin/bash
# Check if Python is installed
if command -v python3 &>/dev/null; then
    echo "Python is installed" > /home/jamie062/cron/logs/check_python.log
else
    echo "Python is not installed" > /home/jamie062/cron/logs/check_python.log
fi
