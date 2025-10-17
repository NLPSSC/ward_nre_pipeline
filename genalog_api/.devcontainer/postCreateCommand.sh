#!/usr/bin/bash

pip install --upgrade pip --root-user-action=ignore && \
    python -m pip install -r ./requirements.txt --root-user-action=ignore

# pip install --upgrade pip --root-user-action=ignore && \
#     python -m pip install -r ./requirements.txt --root-user-action=ignore

# # Configure Git to use parent directory if .git exists there
# if [ -d "../.git" ]; then
#     git config --global --add safe.directory /workspace/..
#     cd /workspace && git --git-dir=../.git --work-tree=.. status
# fi

