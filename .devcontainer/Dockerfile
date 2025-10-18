FROM python:3.8-slim

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	curl \
	libglib2.0-0 \
	git \
	vim \
	openssh-client \
	&& rm -rf /var/lib/apt/lists/*

