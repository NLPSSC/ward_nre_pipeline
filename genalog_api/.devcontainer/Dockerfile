# Use Python 3.8 slim image
FROM python:3.8-slim

# Set work directory
WORKDIR /workspace

# Copy requirements file
COPY ../requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Default command
CMD ["bash"]
