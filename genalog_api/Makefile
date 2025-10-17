.PHONY: help dev-build dev-up dev-shell dev-down dev-post-create dev-test

help:
	@echo ""
	@echo "\033[1;36mAvailable targets:\033[0m"
	@echo "  \033[1;32mdev-build\033[0m        Build the DevContainer image"
	@echo "  \033[1;32mdev-up\033[0m           Start (and attach to) the DevContainer"
	@echo "  \033[1;32mdev-shell\033[0m        Open a bash shell in the DevContainer (starts container if needed)"
	@echo "  \033[1;32mdev-down\033[0m         Remove (stop and delete) the DevContainer"
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

dev-exec: dev-up
	@devcontainer exec --workspace-folder . bash -c '"$@"'

# Remove (stop and delete) the DevContainer using Docker
dev-down:
	@CONTAINERS=$$(docker ps -a --format '{{.ID}} {{.Image}}' | grep ' vsc-genalog_api' | awk '{print $$1}'); \
	if [ -n "$$CONTAINERS" ]; then docker rm -f $$CONTAINERS; fi

# Run tests in the DevContainer
dev-test:
	@devcontainer exec --workspace-folder . pytest
