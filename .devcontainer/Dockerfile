FROM python:3.8

# Set work directory
WORKDIR /workspace/src/genalog_api

# Copy requirements file
COPY ../src/genalog_api/requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Default command
CMD ["bash"]
