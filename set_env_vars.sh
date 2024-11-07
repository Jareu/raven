#!/bin/bash

# Define the environment variables
OPENAI_KEY="OPENAI_API_KEY=abcd"
ELEVENLABS_KEY="ELEVENLABS_API_KEY=efgh"

# Target file where environment variables are set (update if different)
PROFILE_FILE="$HOME/.bashrc"

# Check and add OPENAI_API_KEY if not present
if ! grep -q "$OPENAI_KEY" "$PROFILE_FILE"; then
    echo "$OPENAI_KEY" >> "$PROFILE_FILE"
    echo "OPENAI_API_KEY set in $PROFILE_FILE"
else
    echo "OPENAI_API_KEY already set in $PROFILE_FILE"
fi

# Check and add ELEVENLABS_API_KEY if not present
if ! grep -q "$ELEVENLABS_KEY" "$PROFILE_FILE"; then
    echo "$ELEVENLABS_KEY" >> "$PROFILE_FILE"
    echo "ELEVENLABS_API_KEY set in $PROFILE_FILE"
else
    echo "ELEVENLABS_API_KEY already set in $PROFILE_FILE"
fi
