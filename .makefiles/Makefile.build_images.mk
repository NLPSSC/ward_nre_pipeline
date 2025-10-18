include .makefiles/Makefile.common.mk

ifndef BUILD_IMAGES_INCLUDED
BUILD_IMAGES_INCLUDED := 1

.PHONY: help-build_images python38_base-build python38_base-rebuild python38_base-bash

help-build_images:
	@echo "Base Image Targets:"
	@echo ""
	@echo "  \033[1;32mpython38_base-build\033[0m      Build the Python 3.8 base Docker image"
	@echo "  \033[1;32mpython38_base-rebuild\033[0m    Rebuild the Python 3.8 base Docker image (no cache)"
	@echo "  \033[1;32mpython38_base-bash\033[0m      Start a bash shell in the Python 3.8 base Docker image"
	@echo ""

###############################################################################
# Python 3.8 Base
###############################################################################

PYTHON38_TEXT := "Python 3.8"
PYTHON38_LABEL := python38_base
PYTHON38_BASE_IMAGE_NAME := nlpssc/python38-base:latest
PYTHON38_BASE_DOCKERFILE := .docker_imgs/$(PYTHON38_LABEL)/Dockerfile.python38_base

python38_base-build:
	@[ ! -f $(PYTHON38_BASE_DOCKERFILE) ] && \
		echo "Dockerfile not found" || \
		$(call docker-build, $(PYTHON38_BASE_DOCKERFILE), $(PYTHON38_BASE_IMAGE_NAME), .)

python38_base-rebuild:
	@$(MAKE) python38_base-build FORCE_REBUILD=1

python38_base-bash: python38_base-build
	@docker run --rm -it --entrypoint /bin/bash $(PYTHON38_BASE_IMAGE_NAME)

python38_base-test: python38_base-build
	@docker run --rm -it $(PYTHON38_BASE_IMAGE_NAME) /bin/bash -c "echo 'Testing Python 3.8 base image...'"

python38_base-drop:
	@if docker image inspect $(PYTHON38_BASE_IMAGE_NAME) > /dev/null 2>&1; then \
		docker rmi -f $(PYTHON38_BASE_IMAGE_NAME); \
	else \
		echo "Image $(PYTHON38_BASE_IMAGE_NAME) does not exist."; \
	fi

python38_base-help:
	@echo "$(PYTHON38_TEXT) Base Image Targets:"
	@echo ""
	@echo "  \033[1;32mpython38_base-build\033[0m      Build the $(PYTHON38_TEXT) base Docker image"
	@echo "  \033[1;32mpython38_base-rebuild\033[0m    Rebuild the $(PYTHON38_TEXT) base Docker image (no cache)"
	@echo "  \033[1;32mpython38_base-bash\033[0m      Start a bash shell in the $(PYTHON38_TEXT) base Docker image"
	@echo ""

###############################################################################
# Python 3.11 Base
###############################################################################

PYTHON311_LABEL := "Python 3.11"
PYTHON311_BASE_IMAGE_NAME := nlpssc/python311-base:latest
PYTHON311_BASE_DOCKERFILE := .docker_imgs/python311_base/Dockerfile.python311_base

python311_base-build:
	@[ ! -f $(PYTHON311_BASE_DOCKERFILE) ] && \
		echo "Dockerfile not found" || \
		$(call docker-build, $(PYTHON311_BASE_DOCKERFILE), $(PYTHON311_BASE_IMAGE_NAME), .)

python311_base-rebuild:
	@$(MAKE) python311_base-build FORCE_REBUILD=1

python311_base-bash: python311_base-build
	@docker run --rm -it --entrypoint /bin/bash $(PYTHON311_BASE_IMAGE_NAME)

python311_base-test: python311_base-build
	@docker run --rm -it $(PYTHON311_BASE_IMAGE_NAME) /bin/bash -c "echo 'Testing Python 3.11 base image...'"

python311_base-drop:
	@if docker image inspect $(PYTHON311_BASE_IMAGE_NAME) > /dev/null 2>&1; then \
		docker rmi -f $(PYTHON311_BASE_IMAGE_NAME); \
	else \
		echo "Image $(PYTHON311_BASE_IMAGE_NAME) does not exist."; \
	fi



###############################################################################
# Python 3.12 Base
###############################################################################

PYTHON312_LABEL := "Python 3.12"
PYTHON312_BASE_IMAGE_NAME := nlpssc/python312-base:latest
PYTHON312_BASE_DOCKERFILE := .docker_imgs/python312_base/Dockerfile.python312_base

python312_base-build:
	@[ ! -f $(PYTHON312_BASE_DOCKERFILE) ] && \
		echo "Dockerfile not found" || \
		$(call docker-build, $(PYTHON312_BASE_DOCKERFILE), $(PYTHON312_BASE_IMAGE_NAME), .)

python312_base-rebuild:
	@$(MAKE) python312_base-build FORCE_REBUILD=1

python312_base-bash: python312_base-build
	@docker run --rm -it --entrypoint /bin/bash $(PYTHON312_BASE_IMAGE_NAME)

python312_base-test: python312_base-build
	@docker run --rm -it $(PYTHON312_BASE_IMAGE_NAME) /bin/bash -c "echo 'Testing Python 3.12 base image...'"

python312_base-drop:
	@if docker image inspect $(PYTHON312_BASE_IMAGE_NAME) > /dev/null 2>&1; then \
		docker rmi -f $(PYTHON312_BASE_IMAGE_NAME); \
	else \
		echo "Image $(PYTHON312_BASE_IMAGE_NAME) does not exist."; \
	fi

###############################################################################
# MedSpacy QuickUMLS Processor Base
###############################################################################

MEDSPACY_QUICKUMLS_PROCESSOR_LABEL := "Medspacy-QuickUMLS Processor"
MEDSPACY_QUICKUMLS_PROCESSOR_IMAGE_NAME := nlpssc/medspacy-quickumls-processor:latest
MEDSPACY_QUICKUMLS_PROCESSOR_DOCKERFILE := .docker_imgs/medspacy_quickumls_processor/Dockerfile.medspacy_quickumls_processor

medspacy_quickumls_processor-build:
	@[ ! -f $(MEDSPACY_QUICKUMLS_PROCESSOR_DOCKERFILE) ] && \
		echo "Dockerfile not found" || \
		$(call docker-build, $(MEDSPACY_QUICKUMLS_PROCESSOR_DOCKERFILE), $(MEDSPACY_QUICKUMLS_PROCESSOR_IMAGE_NAME), .)

medspacy_quickumls_processor-rebuild:
	@$(MAKE) medspacy_quickumls_processor-build FORCE_REBUILD=1

medspacy_quickumls_processor-bash: medspacy_quickumls_processor-build
	@docker run --rm -it --entrypoint /bin/bash $(MEDSPACY_QUICKUMLS_PROCESSOR_IMAGE_NAME)

medspacy_quickumls_processor-test: medspacy_quickumls_processor-build
	@docker run --rm -it $(MEDSPACY_QUICKUMLS_PROCESSOR_IMAGE_NAME) /bin/bash -c "echo 'Testing Python 3.8 base image...'"

medspacy_quickumls_processor-drop:
	@if docker image inspect $(MEDSPACY_QUICKUMLS_PROCESSOR_IMAGE_NAME) > /dev/null 2>&1; then \
		docker rmi -f $(MEDSPACY_QUICKUMLS_PROCESSOR_IMAGE_NAME); \
	else \
		echo "Image $(MEDSPACY_QUICKUMLS_PROCESSOR_IMAGE_NAME) does not exist."; \
	fi
	
endif

base-drop-images: python38_base-drop python311_base-drop python312_base-drop medspacy_quickumls_processor-drop 

