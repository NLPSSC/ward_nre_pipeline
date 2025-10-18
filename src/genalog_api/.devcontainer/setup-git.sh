#!/bin/bash

# Get Git configuration from the host (this runs on the host)
GIT_USER_EMAIL="$(git config --global user.email 2>/dev/null || echo '')"
GIT_USER_NAME="$(git config --global user.name 2>/dev/null || echo '')"

# Write to a file that can be read by the container
echo "export GIT_USER_EMAIL=\"$GIT_USER_EMAIL\"" > .devcontainer/git-config.env
echo "export GIT_USER_NAME=\"$GIT_USER_NAME\"" >> .devcontainer/git-config.env

echo "Captured Git config - Email: $GIT_USER_EMAIL, Name: $GIT_USER_NAME"