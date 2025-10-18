.PHONY: help dev-build dev-up dev-shell dev-down dev-post-create dev-test

help:
	@echo ""
	@echo "  \033[1;32mdev-build-genalog_api\033[0m   Build the genalog_api DevContainer image"
	@echo "  \033[1;32mdev-up-genalog_api\033[0m      Start (and attach to) the genalog_api DevContainer"
	@echo "  \033[1;32mdev-shell-genalog_api\033[0m   Open a bash shell in the genalog_api DevContainer"
	@echo "  \033[1;32mdev-exec-genalog_api\033[0m    Run a command in the genalog_api DevContainer"
	@echo "  \033[1;32mdev-down-genalog_api\033[0m    Remove the genalog_api DevContainer"
	@echo "  \033[1;32mdev-test-genalog_api\033[0m    Run tests in the genalog_api DevContainer"
	@echo ""
	@echo "Usage: make <target>[-genalog_api]"

# Build the DevContainer image
dev-build-genalog_api:
	@devcontainer build --workspace-folder . --config .devcontainer/genalog_api/devcontainer.json

# Start (and attach to) the DevContainer
dev-up-genalog_api: dev-build-genalog_api
	@devcontainer up --workspace-folder . --config .devcontainer/genalog_api/devcontainer.json

# Open a bash shell in the DevContainer
dev-shell-genalog_api: dev-up-genalog_api
	@devcontainer exec --workspace-folder . --config .devcontainer/genalog_api/devcontainer.json /bin/bash

dev-exec-genalog_api: dev-up-genalog_api
	@devcontainer exec --workspace-folder . --config .devcontainer/genalog_api/devcontainer.json bash -c '"$@"'

# Remove (stop and delete) the DevContainer using Docker
dev-down-genalog_api:
	@CONTAINERS=$$(docker ps -a --format '{{.ID}} {{.Image}}' | grep ' vsc-genalog_api' | awk '{print $$1}'); \
	if [ -n "$$CONTAINERS" ]; then docker rm -f $$CONTAINERS; fi

# Run tests in the DevContainer
dev-test-genalog_api:
	@devcontainer exec --workspace-folder . pytest
