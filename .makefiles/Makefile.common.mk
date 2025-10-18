ifndef COMMON_MK_INCLUDED
COMMON_MK_INCLUDED := 1

# Get the current project workspace directory
PROJECT_WORKSPACE := $(shell pwd)

# Determine if we should force rebuild the Docker image
CACHE_FLAG = $(if $(filter 1,$(FORCE_REBUILD)),--no-cache,)

# Enable BuildKit for Docker builds
DOCKER_BUILDKIT := 1

# Set maximum parallelism for BuildKit
ifdef OPTIMIZE_BUILD
BUILDKIT_MAX_PARALLELISM_SETTING := --build-arg BUILDKIT_MAX_PARALLELISM=$(nproc)
BUILDKIT_INLINE_CACHE_SETTING := --build-arg BUILDKIT_INLINE_CACHE=1
COMPRESS_SETTING := --compress
endif

# Environment variables for Docker builds
PROD_DOCKER_ENV := prod
DEV_DOCKER_ENV := dev

define green
    printf "\033[1;32m%s\033[0m" $(1)
endef


# $1 - The path of the Dockerfile
# $2 - The tag (image name) for the Docker image
# $3 - The --workspace-folder
define docker-build
    docker build -t $(2) -f $(1) $(3)
	docker build \
	$(BUILDKIT_MAX_PARALLELISM_SETTING) \
	$(BUILDKIT_INLINE_CACHE_SETTING) \
	$(COMPRESS_SETTING) \
	$(CACHE_FLAG) \
	-f $(1) -t $(2) $(3) && \
	docker image inspect $(2) | \
		jq -r '"Size: " + ((.[0].Size / 1024 / 1024 * 100 | round / 100) | tostring) + " MB"'
	
endef

endif	

