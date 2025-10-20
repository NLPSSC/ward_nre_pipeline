include .makefiles/Makefile.common.mk

ifndef BUILD_IMAGES_INCLUDED
BUILD_IMAGES_INCLUDED := 1

.PHONY: help-base-images

get_label_text = $(shell .makefiles/get_config_value.sh $(1) 'text')
get_label_image_name = $(shell .makefiles/get_config_value.sh $(1) 'image_name')
get_label_dockerfile = $(shell .makefiles/get_config_value.sh $(1) 'dockerfile')

defined_base_images := python38_base python311_base python312_base medspacy_quickumls_processor

define show_error
    printf "\033[1;31m%s\033[0m" $(1)
endef

validate-%:
	@if [ "$(filter $*,$(defined_base_images))" = "" ]; then \
		$(call show_error,"$* is not a valid base image target") \
		exit 1; \
	else \
		echo "" && \
			echo "Label: 		$*" && \
			echo "Text: 		$(call get_label_text,$*)" && \
			echo "Image Name: 	$(call get_label_image_name,$*)" && \
			echo "Dockerfile: 	$(call get_label_dockerfile,$*)" && \
			echo ""; \
	fi

# Pattern rule for building only allowed base images
%-build: 
	@$(MAKE) --no-print-directory validate-$* && \
		[ ! -f $(call get_label_dockerfile,$*) ] && \
			echo "Dockerfile not found" || \
			$(call docker-build, $(call get_label_dockerfile,$*), $(call get_label_image_name,$*), .)

%-rebuild:
	@$(MAKE) --no-print-directory validate-$* && \
		$(MAKE) --no-print-directory $*-build FORCE_REBUILD=1

%-bash: %-build
	@docker run --rm -it --entrypoint /bin/bash $(call get_label_image_name,$*)

%-test: %-build
	@docker run --rm -it $(call get_label_image_name,$*) /bin/bash -c "echo 'Testing $(call get_label_text,$*) base image...'"

%-drop:
	@if docker image inspect $(call get_label_image_name,$*) > /dev/null 2>&1; then \
		docker rmi -f $(call get_label_image_name,$*); \
	else \
		echo "Image $(call get_label_image_name,$*) does not exist."; \
	fi

%-help:
	@echo "\033[1;34m$(call get_label_text,$*)\033[0m Base Image Targets"
	@echo ""
	@echo "  \033[1;32m$*-build\033[0m      Build the $(call get_label_text,$*) base Docker image"
	@echo "  \033[1;32m$*-rebuild\033[0m    Rebuild the $(call get_label_text,$*) base Docker image (no cache)"
	@echo "  \033[1;32m$*-bash\033[0m      Start a bash shell in the $(call get_label_text,$*) base Docker image"
	@echo ""


help-base-images:
	@$(foreach img,$(defined_base_images),$(MAKE) --no-print-directory $(img)-help;)

# $(PYTHON38_LABEL)-build:
# 	@[ ! -f $(PYTHON38_BASE_DOCKERFILE) ] && \
# 		echo "Dockerfile not found" || \
# 		$(call docker-build, $(PYTHON38_BASE_DOCKERFILE), $(PYTHON38_BASE_IMAGE_NAME), .)

# $(PYTHON38_LABEL)-rebuild:
# 	@$(MAKE) $(PYTHON38_LABEL)-build FORCE_REBUILD=1

# $(PYTHON38_LABEL)-bash: $(PYTHON38_LABEL)-build
# 	@docker run --rm -it --entrypoint /bin/bash $(PYTHON38_BASE_IMAGE_NAME)

# $(PYTHON38_LABEL)-test: $(PYTHON38_LABEL)-build
# 	@docker run --rm -it $(PYTHON38_BASE_IMAGE_NAME) /bin/bash -c "echo 'Testing $(PYTHON38_TEXT) base image...'"

# $(PYTHON38_LABEL)-drop:
# 	@if docker image inspect $(PYTHON38_BASE_IMAGE_NAME) > /dev/null 2>&1; then \
# 		docker rmi -f $(PYTHON38_BASE_IMAGE_NAME); \
# 	else \
# 		echo "Image $(PYTHON38_BASE_IMAGE_NAME) does not exist."; \
# 	fi

# $(PYTHON38_LABEL)-help:
# 	@echo "$(PYTHON38_TEXT) Base Image Targets:"
# 	@echo ""
# 	@echo "  \033[1;32m$(PYTHON38_LABEL)-build\033[0m      Build the $(PYTHON38_TEXT) base Docker image"
# 	@echo "  \033[1;32m$(PYTHON38_LABEL)-rebuild\033[0m    Rebuild the $(PYTHON38_TEXT) base Docker image (no cache)"
# 	@echo "  \033[1;32m$(PYTHON38_LABEL)-bash\033[0m      Start a bash shell in the $(PYTHON38_TEXT) base Docker image"
# 	@echo ""

# ###############################################################################
# # Python 3.11 Base
# ###############################################################################

# PYTHON311_LABEL := "Python 3.11"
# PYTHON311_BASE_IMAGE_NAME := nlpssc/python311-base:latest
# PYTHON311_BASE_DOCKERFILE := .docker_imgs/python311_base/Dockerfile.python311_base

# python311_base-build:
# 	@[ ! -f $(PYTHON311_BASE_DOCKERFILE) ] && \
# 		echo "Dockerfile not found" || \
# 		$(call docker-build, $(PYTHON311_BASE_DOCKERFILE), $(PYTHON311_BASE_IMAGE_NAME), .)

# python311_base-rebuild:
# 	@$(MAKE) python311_base-build FORCE_REBUILD=1

# python311_base-bash: python311_base-build
# 	@docker run --rm -it --entrypoint /bin/bash $(PYTHON311_BASE_IMAGE_NAME)

# python311_base-test: python311_base-build
# 	@docker run --rm -it $(PYTHON311_BASE_IMAGE_NAME) /bin/bash -c "echo 'Testing Python 3.11 base image...'"

# python311_base-drop:
# 	@if docker image inspect $(PYTHON311_BASE_IMAGE_NAME) > /dev/null 2>&1; then \
# 		docker rmi -f $(PYTHON311_BASE_IMAGE_NAME); \
# 	else \
# 		echo "Image $(PYTHON311_BASE_IMAGE_NAME) does not exist."; \
# 	fi



# ###############################################################################
# # Python 3.12 Base
# ###############################################################################

# PYTHON312_LABEL := "Python 3.12"
# PYTHON312_BASE_IMAGE_NAME := nlpssc/python312-base:latest
# PYTHON312_BASE_DOCKERFILE := .docker_imgs/python312_base/Dockerfile.python312_base

# python312_base-build:
# 	@[ ! -f $(PYTHON312_BASE_DOCKERFILE) ] && \
# 		echo "Dockerfile not found" || \
# 		$(call docker-build, $(PYTHON312_BASE_DOCKERFILE), $(PYTHON312_BASE_IMAGE_NAME), .)

# python312_base-rebuild:
# 	@$(MAKE) python312_base-build FORCE_REBUILD=1

# python312_base-bash: python312_base-build
# 	@docker run --rm -it --entrypoint /bin/bash $(PYTHON312_BASE_IMAGE_NAME)

# python312_base-test: python312_base-build
# 	@docker run --rm -it $(PYTHON312_BASE_IMAGE_NAME) /bin/bash -c "echo 'Testing Python 3.12 base image...'"

# python312_base-drop:
# 	@if docker image inspect $(PYTHON312_BASE_IMAGE_NAME) > /dev/null 2>&1; then \
# 		docker rmi -f $(PYTHON312_BASE_IMAGE_NAME); \
# 	else \
# 		echo "Image $(PYTHON312_BASE_IMAGE_NAME) does not exist."; \
# 	fi

# ###############################################################################
# # MedSpacy QuickUMLS Processor Base
# ###############################################################################

# MEDSPACY_QUICKUMLS_PROCESSOR_LABEL := "Medspacy-QuickUMLS Processor"
# MEDSPACY_QUICKUMLS_PROCESSOR_IMAGE_NAME := nlpssc/medspacy-quickumls-processor:latest
# MEDSPACY_QUICKUMLS_PROCESSOR_DOCKERFILE := .docker_imgs/medspacy_quickumls_processor/Dockerfile.medspacy_quickumls_processor

# medspacy_quickumls_processor-build:
# 	@[ ! -f $(MEDSPACY_QUICKUMLS_PROCESSOR_DOCKERFILE) ] && \
# 		echo "Dockerfile not found" || \
# 		$(call docker-build, $(MEDSPACY_QUICKUMLS_PROCESSOR_DOCKERFILE), $(MEDSPACY_QUICKUMLS_PROCESSOR_IMAGE_NAME), .)

# medspacy_quickumls_processor-rebuild:
# 	@$(MAKE) medspacy_quickumls_processor-build FORCE_REBUILD=1

# medspacy_quickumls_processor-bash: medspacy_quickumls_processor-build
# 	@docker run --rm -it --entrypoint /bin/bash $(MEDSPACY_QUICKUMLS_PROCESSOR_IMAGE_NAME)

# medspacy_quickumls_processor-test: medspacy_quickumls_processor-build
# 	@docker run --rm -it $(MEDSPACY_QUICKUMLS_PROCESSOR_IMAGE_NAME) /bin/bash -c "echo 'Testing Python 3.8 base image...'"

# medspacy_quickumls_processor-drop:
# 	@if docker image inspect $(MEDSPACY_QUICKUMLS_PROCESSOR_IMAGE_NAME) > /dev/null 2>&1; then \
# 		docker rmi -f $(MEDSPACY_QUICKUMLS_PROCESSOR_IMAGE_NAME); \
# 	else \
# 		echo "Image $(MEDSPACY_QUICKUMLS_PROCESSOR_IMAGE_NAME) does not exist."; \
# 	fi
	

# base-drop-images: python38_base-drop python311_base-drop python312_base-drop medspacy_quickumls_processor-drop 

endif
