# Get the current project workspace directory
PROJECT_WORKSPACE := $(shell pwd)

# Determine if we should force rebuild the Docker image
CACHE_FLAG = $(if $(FORCE_REBUILD),--no-cache,)

# Enable BuildKit for Docker builds
DOCKER_BUILDKIT := 1

# Set maximum parallelism for BuildKit
BUILDKIT_MAX_PARALLELISM := $(nproc)

# Environment variables for Docker builds
PROD_DOCKER_ENV := prod
DEV_DOCKER_ENV := dev

# $1 - The path of the Dockerfile
# $2 - The tag for the Docker image
# $3 - The --workspace-folder
docker-build = $(shell docker build \
	--build-arg BUILDKIT_MAX_PARALLELISM=$(nproc) \
	--build-arg BUILDKIT_INLINE_CACHE=1 \
	--compress \
	$(CACHE_FLAG) \
	-f $(1) \
	-t $(2) \
	$(3) \
	)