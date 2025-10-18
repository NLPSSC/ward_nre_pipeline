OPTIMIZE_BUILD := 1

include .makefiles/Makefile.common.mk
include .makefiles/Makefile.build_images.mk
include .makefiles/Makefile.genalog_api.mk
include .makefiles/Makefile.nre_pipeline.mk

.DEFAULT_GOAL := help

help: help-base-images help-genalog_api help-nre_pipeline



