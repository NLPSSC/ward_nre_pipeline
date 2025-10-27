# nre_pipeline
FROM nlpssc/medspacy-quickumls-processor:latest AS base

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Get the UMLS API key file path from the host call
ARG umls_key_file=
ENV DEV_UMLS_KEY_PATH=${umls_key_file}

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends make sqlite3 jq && \
    true

# Add /etc/pip.conf, such that any in-container changes during development
# don't raise a warning, since this is use the root python and not a venv
RUN cat <<EOF >> /etc/pip.conf

[global]
root-user-action = ignore

EOF

# /home/westerd/_/project_data/ward_nre_pipeline/UMLS_API_KEY.secret

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
RUN if [ -f /requirements/requirements-dev.txt ]; then \
        python -m pip install -r /requirements/requirements-dev.txt; \
    fi

CMD ["bash"]
