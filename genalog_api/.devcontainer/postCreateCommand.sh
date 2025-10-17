#!/usr/bin/bash

pip install --upgrade pip --root-user-action=ignore && \
    python -m pip install -r ./requirements.txt --root-user-action=ignore

# Configure Git to use the mounted .git directory
if [ -d "/workspace/.git" ]; then
    git config --global --add safe.directory /workspace
    # Set up Git to work from the workspace root
    cd /workspace && git config --global --add safe.directory $(pwd)
fi

# Copy Git user configuration from host (read from generated file)
if [ -f ".devcontainer/git-config.env" ]; then
    source .devcontainer/git-config.env
    
    if [ -n "$GIT_USER_EMAIL" ]; then
        git config --global user.email "$GIT_USER_EMAIL"
        echo "Set Git user email: $GIT_USER_EMAIL"
    fi
    
    if [ -n "$GIT_USER_NAME" ]; then
        git config --global user.name "$GIT_USER_NAME"
        echo "Set Git user name: $GIT_USER_NAME"
    fi
else
    echo "Warning: Git config file not found. Git user identity may not be set."
fi

