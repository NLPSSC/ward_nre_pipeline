# nre_pipeline
FROM nlpssc/medspacy-quickumls-processor:latest AS base

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends make && \
    true

# Add /etc/pip.conf, such that any in-container changes during development
# don't raise a warning, since this is use the root python and not a venv
RUN echo -e "[global]\nroot-user-action = ignore" > /etc/pip.conf

# Add alias to root's .bashrc
RUN echo "alias ll='ls -la'" >> /root/.bashrc || exit 100

# Set up requirements
RUN mkdir -p /requirements && chmod a+rw /requirements
RUN mkdir -p /test_data && chmod a+rw /test_data
RUN mkdir -p /output && chmod a+rw /output
RUN mkdir -p /input_data && chmod a+rw /input_data

COPY .devcontainer/nre_pipeline/*requirements.txt ./requirements
RUN if [ -f /requirements/requirements.txt ]; then \
        python -m pip install -r /requirements/requirements.txt; \
    fi
RUN if [ -f /requirements/dev-requirements.txt ]; then \
        python -m pip install -r /requirements/dev-requirements.txt; \
    fi

CMD ["bash"]
