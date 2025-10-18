ifndef BUILD_IMAGES_INCLUDED
BUILD_IMAGES_INCLUDED := 1

.PHONY: help-build_images build-python38_base rebuild-python38_base bash-python38_base

help-build_images:
	@echo "Base Image Targets:"
	@echo ""
	@echo "  \033[1;32mbuild-python38_base\033[0m      Build the Python 3.8 base Docker image"
	@echo "  \033[1;32mrebuild-python38_base\033[0m    Rebuild the Python 3.8 base Docker image (no cache)"
	@echo "  \033[1;32mbash-python38_base\033[0m      Start a bash shell in the Python 3.8 base Docker image"
	@echo ""

PYTHON38_BASE_IMAGE_NAME := nlpssc/python38-base:latest
PYTHON38_BASE_DOCKERFILE := .docker_imgs/Dockerfile.python38_base

build-python38_base:
	@[ ! -f $(PYTHON38_BASE_DOCKERFILE) ] && \
		echo "Dockerfile not found" || \
		$(call docker-build, $(PYTHON38_BASE_DOCKERFILE), $(PYTHON38_BASE_IMAGE_NAME), .)

rebuild-python38_base:
	@$(MAKE) build-python38_base FORCE_REBUILD=1

bash-python38_base: build-python38_base
	@docker run --rm -it --entrypoint /bin/bash $(PYTHON38_BASE_IMAGE_NAME)

test-python38_base: build-python38_base
	@docker run --rm -it $(PYTHON38_BASE_IMAGE_NAME) /bin/bash -c "echo 'Testing Python 3.8 base image...'"

drop-python38_base:
	@if docker image inspect $(PYTHON38_BASE_IMAGE_NAME) > /dev/null 2>&1; then \
		docker rmi -f $(PYTHON38_BASE_IMAGE_NAME); \
	else \
		echo "Image $(PYTHON38_BASE_IMAGE_NAME) does not exist."; \
	fi

endif