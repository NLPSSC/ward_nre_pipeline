OPTIMIZE_BUILD := 1

include .makefiles/Makefile.common.mk
include .makefiles/Makefile.build_images.mk
include .makefiles/Makefile.genalog_api.mk
include .makefiles/Makefile.nre_pipeline.mk

.DEFAULT_GOAL := help

help:
	@$(MAKE) help-build_images
	@$(MAKE) help-genalog_api
	@$(MAKE) help-nre_pipeline



