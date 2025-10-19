OPTIMIZE_BUILD := 1

include .makefiles/Makefile.common.mk
include .makefiles/Makefile.build_images.mk
include .makefiles/Makefile.genalog_api.mk
include .makefiles/Makefile.nre_pipeline.mk

.DEFAULT_GOAL := help

help: help-base-images help-genalog_api help-nre_pipeline

start-docker:
	sudo service docker start

stop-docker:
	sudo service docker stop

build-dev-containers:
	@make python312_base-build && \
		make python38_base-build && \
		make medspacy_quickumls_processor-build && \
		make dev-nre_pipeline-build && make dev-genalog_api-build && \
		make dev-genalog_api-build
