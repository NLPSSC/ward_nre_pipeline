#!/bin/bash

# Git configuration setup for devcontainer
# This script sets up Git user configuration from host values

if [ -f "/workspace/genalog_api/.devcontainer/git-config.env" ]; then
    source /workspace/genalog_api/.devcontainer/git-config.env
    
    if [ -n "$GIT_USER_EMAIL" ] && [ -z "$(git config --global user.email 2>/dev/null)" ]; then
        git config --global user.email "$GIT_USER_EMAIL"
        echo "✓ Set Git user email: $GIT_USER_EMAIL"
    fi
    
    if [ -n "$GIT_USER_NAME" ] && [ -z "$(git config --global user.name 2>/dev/null)" ]; then
        git config --global user.name "$GIT_USER_NAME"
        echo "✓ Set Git user name: $GIT_USER_NAME"
    fi
fi