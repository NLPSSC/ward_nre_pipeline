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
	@make python311_base-build && \
		make python38_base-build && \
		make medspacy_quickumls_processor-build && \
		make dev-nre_pipeline-build && make dev-genalog_api-build && \
		make dev-genalog_api-build


clean-all-docker:
	@if [ -z "$$(docker ps -aq)" ]; then \
		echo "No containers to remove."; \
	else \
		docker rm -f $$(docker ps -aq); \
	fi
	@if [ -z "$$(docker images -q)" ]; then \
		echo "No images to remove."; \
	else \
		docker rmi -f $$(docker images -q); \
	fi
	@if [ -n "$$(docker volume ls -q)" ]; then \
		docker volume rm -f $$(docker volume ls -q); \
	else \
		echo "No volumes to remove."; \
	fi
	docker container prune -f
	docker image prune -f
	docker builder prune -f
	docker system prune -f

	
test-collect-only:
	pytest --collect-only -c /workspace/pytest.ini

test-to-first-error:
	pytest -x -c /workspace/pytest.ini

help: help-base-images help-genalog_api help-nre_pipeline
	@echo "test-collect-only    Run pytest in collect-only mode"
	@echo "test-to-first-error  Run pytest and stop at first error"
