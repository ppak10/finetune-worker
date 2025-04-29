FROM ubuntu:22.04

ARG ENVIRONMENT

WORKDIR /home

#######################
# Python Dependencies #
#######################

# Prerequisites
RUN apt update
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

# Python 3.10
RUN apt update
RUN apt install -y python3.10 python3.10-venv python3-pip

###########################
# Entrypoint Dependencies #
###########################

RUN apt install -y screen

###############
# Worker User #
###############

# Create and use a non-root user
RUN useradd -ms /bin/bash finetune-worker 

# Set permissions on home directory 
RUN chown -R finetune-worker:finetune-worker /home

# Switch to the non-root user
USER finetune-worker

#########################
# Python Initialization #
#########################

# Create Virutal Environment for running client in home directory
RUN python3.10 -m venv app/venv

# Install requirements for client
RUN . app/venv/bin/activate && pip install aiohttp celery redis watchdog websockets

###########################
# Development Environment #
###########################
COPY ./.devcontainer.json ./app/.devcontainer.json

##############
# Entrypoint #
##############

# Runs 'entrypoint.sh' script.
# https://stackoverflow.com/a/50276037/10521456
COPY ./entrypoint.sh ./ubuntu/entrypoint.sh

ENTRYPOINT ["./ubuntu/entrypoint.sh"]
