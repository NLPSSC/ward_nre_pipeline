#!/usr/bin/bash

pip install --upgrade pip --root-user-action=ignore && \
    python -m pip install -r ./requirements.txt --root-user-action=ignore

# Configure Git to use the mounted .git directory
if [ -d "/workspace/.git" ]; then
    git config --global --add safe.directory /workspace
    # Set up Git to work from the workspace root
    cd /workspace && git config --global --add safe.directory $(pwd)
fi

# Git configuration will be set up automatically when shell starts
# via /setup-git-on-shell.sh sourced in .bashrc

