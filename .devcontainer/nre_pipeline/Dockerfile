# nre_pipeline
FROM nlpssc/medspacy-quickumls-processor:latest AS base

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \

# Add alias to root's .bashrc
RUN echo "alias ll='ls -la'" >> /root/.bashrc || exit 100

# Set up requirements
RUN mkdir -p /requirements && chmod a+rw /requirements
COPY .devcontainer/nre_pipeline/*requirements.txt ./requirements
RUN if [ -f /requirements/requirements.txt ]; then python -m pip install -r /requirements/requirements.txt; fi
RUN if [ -f /requirements/dev-requirements.txt ]; then python -m pip install -r /requirements/dev-requirements.txt; fi

CMD ["bash"]
