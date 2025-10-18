ifndef BUILD_IMAGES_INCLUDED
BUILD_IMAGES_INCLUDED := 1

.PHONY: help-build_images build-python38_base rebuild-python38_base

help-build_images:
	@echo "Base Image Targets:"
	@echo ""
	@echo "  \033[1;32mbuild-python38_base\033[0m      Build the Python 3.8 base Docker image"
	@echo "  \033[1;32mrebuild-python38_base\033[0m    Rebuild the Python 3.8 base Docker image (no cache)"
	@echo ""

PYTHON38_BASE_IMAGE := nlpssc/python38-base:latest

# docker build -t $(PYTHON38_BASE_IMAGE) -f .docker_imgs/Dockerfile.python38 $(CACHE_FLAG) .
build-python38_base:
	@[ ! -f .docker_imgs/Dockerfile.python38 ] && \
		echo "Dockerfile not found" || \
		$(call docker-build, .docker_imgs/Dockerfile.python38, $(PYTHON38_BASE_IMAGE), .)

rebuild-python38_base:
	@$(MAKE) build-python38_base FORCE_REBUILD=1

drop-python38_base:
	@if docker image inspect $(PYTHON38_BASE_IMAGE) > /dev/null 2>&1; then \
		docker rmi -f $(PYTHON38_BASE_IMAGE); \
	else \
		echo "Image $(PYTHON38_BASE_IMAGE) does not exist."; \
	fi

endif