#!/bin/bash

# Copies over .devcontainer.json into app folder. 
if [ ! -f /home/app/.devcontainer.json ]; then
  cp /home/ubuntu/.devcontainer.json /home/app/
fi

. app/venv/bin/activate

# Install app dependencies
# echo "Installing app requirements"
# pip install -r requirements.txt

python -m app.client.start_services
