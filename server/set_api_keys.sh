#!/bin/bash

# Define the keys and values
OPENAI_API_KEY="your-openai-api-key"
ELEVENLABS_API_KEY="your-elevenlabs-api-key"

# Export the keys to the environment
export OPENAI_API_KEY="$OPENAI_API_KEY"
export ELEVENLABS_API_KEY="$ELEVENLABS_API_KEY"

# Check if the variables are set correctly
if [[ -z "$OPENAI_API_KEY" || -z "$ELEVENLABS_API_KEY" ]]; then
    echo "$(date): Error - API keys were not set." >> /path/to/log/set_api_keys.log
    exit 1
else
    echo "$(date): API keys successfully set. OPENAI_API_KEY=$OPENAI_API_KEY, ELEVENLABS_API_KEY=$ELEVENLABS_API_KEY" >> /path/to/log/set_api_keys.log
fi
