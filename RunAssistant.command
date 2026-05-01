#!/bin/bash

# Move to project directory (the folder this script lives in)
cd "$(dirname "$0")" || exit 1

# Activate virtual environment (created via: python3 -m venv venv)
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Run the assistant
python app.py
