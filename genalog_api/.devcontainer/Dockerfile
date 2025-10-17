# Use the official Python 3.8 slim image
FROM python:3.8-slim

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive
ENV GIT_DISCOVERY_ACROSS_FILESYSTEM=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	curl \
	libglib2.0-0 \
	git \
	vim \
	&& rm -rf /var/lib/apt/lists/*

RUN echo "alias ll='ls -la'" >> /root/.bashrc

# Set up a working directory
WORKDIR /workspace/genalog_api

# Copy requirements file
COPY requirements.txt .
COPY ./.devcontainer/postCreateCommand.sh /postCreateCommand.sh
RUN chmod +x /postCreateCommand.sh

# Install Python dependencies
# RUN pip install --upgrade pip && pip install -r requirements.txt
RUN /postCreateCommand.sh

# Default command
CMD ["bash"]
