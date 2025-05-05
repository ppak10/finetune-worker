#!/bin/bash

# Copies over .devcontainer.json into app folder. 
if [ ! -f /home/app/.devcontainer.json ]; then
  cp /home/ubuntu/.devcontainer.json /home/app/
fi

# Install app dependencies
# echo "Installing app requirements"
# pip install -r requirements.txt
source /home/app/venv/bin/activate && python -m app.client.start_services

# screen -dmS app bash -c "source /home/app/venv/bin/activate && exec python -m app.client.start_services"

# tail -f /dev/null
