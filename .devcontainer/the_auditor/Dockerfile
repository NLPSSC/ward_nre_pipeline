FROM python:3.9-slim

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends make sqlite3 jq && \
#     true


# Add /etc/pip.conf, such that any in-container changes during development
# don't raise a warning, since this is use the root python and not a venv
RUN cat <<EOF >> /etc/pip.conf

[global]
root-user-action = ignore

EOF

# Add alias to root's .bashrc
RUN echo "alias ll='ls -la'" >> /root/.bashrc || exit 100

RUN mkdir -p /requirements && chmod a+rw /requirements
RUN mkdir -p /output && chmod a+rw /output

COPY .devcontainer/the_auditor/*requirements.txt ./requirements

RUN if [ -f /requirements/requirements.txt ]; then \
        python -m pip install -r /requirements/requirements.txt; \
    fi
RUN if [ -f /requirements/requirements-dev.txt ]; then \
        python -m pip install -r /requirements/requirements-dev.txt; \
    fi

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["bash"]