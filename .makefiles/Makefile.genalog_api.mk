ifndef GENALOG_API_INCLUDED
GENALOG_API_INCLUDED := 1

.PHONY: help-genalog_api dev-build-genalog_api dev-up-genalog_api dev-shell-genalog_api dev-exec-genalog_api

help-genalog_api:
	@echo "genalog_api Targets"
	@echo ""
	@echo "  \033[1;32mdev-build-genalog_api\033[0m   Build the genalog_api DevContainer image"
	@echo "  \033[1;32mdev-up-genalog_api\033[0m      Start (and attach to) the genalog_api DevContainer"
	@echo "  \033[1;32mdev-shell-genalog_api\033[0m   Open a bash shell in the genalog_api DevContainer"
	@echo "  \033[1;32mdev-exec-genalog_api\033[0m    Run a command in the genalog_api DevContainer"
	@echo "  \033[1;32mdev-down-genalog_api\033[0m    Remove the genalog_api DevContainer"
	@echo "  \033[1;32mdev-test-genalog_api\033[0m    Run tests in the genalog_api DevContainer"
	@echo ""
	@echo "Usage: make <target>[-genalog_api]"
	@echo ""


# Build the genalog_api service image
dev-build-genalog_api:
	docker compose -f .devcontainer/genalog_api/docker-compose.yml build genalog_api

# Start (and attach to) the genalog_api service
dev-up-genalog_api:
	docker compose -f .devcontainer/genalog_api/docker-compose.yml up -d genalog_api

# Remove (stop and delete) the genalog_api container
dev-down-genalog_api:
	docker compose -f .devcontainer/genalog_api/docker-compose.yml down

# Open a bash shell in the genalog_api container
dev-shell-genalog_api:
	docker compose -f .devcontainer/genalog_api/docker-compose.yml exec genalog_api /bin/bash

# Run a command in the genalog_api container
dev-exec-genalog_api:
	docker compose -f .devcontainer/genalog_api/docker-compose.yml exec genalog_api bash -c "$(cmd)"

# Run tests in the genalog_api container
dev-test-genalog_api:
	docker compose -f .devcontainer/genalog_api/docker-compose.yml exec genalog_api pytest

endif