#!/bin/bash

. venv/bin/activate

# Install app dependencies
# echo "Installing app requirements"
# pip install -r requirements.txt

python -m app.client.start_services
