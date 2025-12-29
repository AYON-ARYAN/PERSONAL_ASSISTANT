#!/bin/bash

# Move to project directory
cd /Volumes/BLACK_SHARK/offline_ai_asssistant || exit

# Activate virtual environment
source venv/bin/activate

# Run the assistant
python app.py
