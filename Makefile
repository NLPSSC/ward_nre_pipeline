include .makefiles/Makefile.common.mk
include .makefiles/Makefile.genalog_api.mk
include .makefiles/Makefile.nre_pipeline.mk

.DEFAULT_GOAL := help

help:
	@echo "Available targets:"
	@echo "  build-python38-base - Build the Python 3.8 base Docker image"
	@echo "  rebuild-python38-base - Rebuild the Python 3.8 base Docker image"

build-python38-base:
	@docker build -t python38-base .docker_imgs/Dockerfile.python38

rebuild-python38-base:
	@docker build -t python38-base .docker_imgs/Dockerfile.python38 --no-cache

