#!/bin/bash

. venv/bin/activate

# Install api dependencies
echo "Installing api requirements"
pip install -r api/requirements.txt

# Install app dependencies
echo "Installing app requirements"
pip install -r app/requirements.txt

python api/polling.py
