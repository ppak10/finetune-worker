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

# Create Virutal Environment for both api and app in home directory
RUN python3.10 -m venv venv

# Install requirements for client
RUN . venv/bin/activate && pip install aiohttp celery redis watchdog

##############
# Entrypoint #
##############

# Runs 'entrypoint.sh' script.
# https://stackoverflow.com/a/50276037/10521456
COPY ./entrypoint.sh ./ubuntu/entrypoint.sh

ENTRYPOINT ["./ubuntu/entrypoint.sh"]
