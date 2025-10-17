.PHONY: help dev-build dev-shell dev-post-create dev-test

help:
	@echo ""
	@echo "\033[1;36mAvailable targets:\033[0m"
	@echo "  \033[1;32mdev-build\033[0m        Build the DevContainer image"
	@echo "  \033[1;32mdev-shell\033[0m        Open a bash shell in the DevContainer"
	@echo "  \033[1;32mdev-post-create\033[0m  Run postCreateCommand in the DevContainer"
	@echo "  \033[1;32mdev-test\033[0m         Run tests in the DevContainer"
	@echo ""

# Build the DevContainer image
dev-build:
	@devcontainer build --workspace-folder .

# Start (and attach to) the DevContainer
dev-up: dev-build
	@devcontainer up --workspace-folder .

# Open a bash shell in the DevContainer
dev-shell: dev-up
	@devcontainer exec --workspace-folder . /bin/bash

# Run postCreateCommand in the DevContainer
dev-post-create:
	@devcontainer exec --workspace-folder . bash .devcontainer/postCreateCommand.sh

# Run tests in the DevContainer
dev-test:
	@devcontainer exec --workspace-folder . pytest
