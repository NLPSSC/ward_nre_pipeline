OPTIMIZE_BUILD := 1

include .makefiles/Makefile.common.mk
include .makefiles/Makefile.build_images.mk
include .makefiles/Makefile.genalog_api.mk
include .makefiles/Makefile.nre_pipeline.mk

.DEFAULT_GOAL := help

help:
	@echo "Available Targets:"
	@echo ""
	@$(MAKE) --no-print-directory help-build_images
	@$(MAKE) --no-print-directory help-genalog_api
	@$(MAKE) --no-print-directory help-nre_pipeline


