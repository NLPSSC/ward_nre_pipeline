ifndef GENALOG_API_INCLUDED
GENALOG_API_INCLUDED := 1

.PHONY: help-genalog_api dev-genalog_api-build dev-genalog_api-up dev-genalog_api-shell dev-genalog_api-exec

help-genalog_api:
	@echo "genalog_api Targets"
	@echo ""
	@echo "  \033[1;32mdev-genalog_api-build\033[0m   Build the genalog_api DevContainer image"
	@echo "  \033[1;32mdev-genalog_api-up\033[0m      Start (and attach to) the genalog_api DevContainer"
	@echo "  \033[1;32mdev-genalog_api-shell\033[0m   Open a bash shell in the genalog_api DevContainer"
	@echo "  \033[1;32mdev-genalog_api-exec\033[0m    Run a command in the genalog_api DevContainer"
	@echo "  \033[1;32mdev-genalog_api-down\033[0m    Remove the genalog_api DevContainer"
	@echo "  \033[1;32mdev-genalog_api-test\033[0m    Run tests in the genalog_api DevContainer"
	@echo ""
	@echo "Usage: make <target>[-genalog_api]"
	@echo ""


# Build the genalog_api service image
dev-genalog_api-build:
	@docker compose -f .devcontainer/genalog_api/docker-compose.yml build genalog_api

# Start (and attach to) the genalog_api service
dev-genalog_api-up:
	@docker compose -f .devcontainer/genalog_api/docker-compose.yml up -d genalog_api

# Remove (stop and delete) the genalog_api container
dev-genalog_api-down:
	@docker compose -f .devcontainer/genalog_api/docker-compose.yml down

# Open a bash shell in the genalog_api container
dev-genalog_api-shell: dev-genalog_api-up
	@docker compose -f .devcontainer/genalog_api/docker-compose.yml exec genalog_api /bin/bash

# Run a command in the genalog_api container
dev-genalog_api-exec:
	@docker compose -f .devcontainer/genalog_api/docker-compose.yml exec genalog_api bash -c "$(cmd)"

# Run tests in the genalog_api container
dev-genalog_api-test:
	@docker compose -f .devcontainer/genalog_api/docker-compose.yml exec genalog_api pytest

endif