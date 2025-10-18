# nre_pipeline
FROM nlpssc/medspacy-quickumls-processor:latest AS base

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \

# Add alias to root's .bashrc
RUN echo "alias ll='ls -la'" >> /root/.bashrc || exit 100

CMD ["bash"]
