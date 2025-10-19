#!/usr/bin/env bash

set -e

PROJECT_PATH="$(dirname $(dirname $(dirname $(realpath "${BASH_SOURCE[0]}"))))"

function create_project_env {

    local env_prefix="_NRE_ENV"
    local context="$1"
    local project_name="$2"
    local environment_path=""
    local env_var_name=""

if [[ "${context}"=="host" || "${context}"=="devcontainer" ]]; then
    echo "[INFO] building for ${context}"
else
    echo "[ERROR] context must be \"host\" or \"devcontainer\""
fi

    local conda_env_name="${context}_${project_name}_env"
    local env_path="${PROJECT_PATH}/envs/${conda_env_name}"

    # Parse arguments
    shift
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --environment_path)
                shift
                environment_path="$1"
                ;;
            *)
                ;;
        esac
        shift
    done

    if [[ -z "${conda_env_name}" ]]; then
        echo "[ERROR] Must provide environment name" && return -1
    fi

    if [[ ! -z "${environment_path}" ]]; then
        echo "[INFO] Environment Path: ${environment_path}"
    fi

    echo "[INFO] Environment Name: ${conda_env_name}"
    echo "[INFO] Environment Path: ${env_path}"

    # ENV_PATH_EXISTS=0
    # if [ -d "${env_path}" ]; then
    #     ENV_PATH_EXISTS=1
    #     echo "[INFO] "${env_path}" already exists."
    # else
    #     echo "[INFO] "${env_path}" will be created."
    # fi
    
    # if [ -d "${env_path}" ]; then
    #     echo "[INFO] Creating empty ${env_path}..."
    #     echo mamba create -p "${env_path}" -f 
    # else
    #     echo "[INFO] Creating ${env_path} with ${environment_path}..."
    #     env_var_name="${env_prefix}_${conda_env_name}"

    #     if [ -f "${environment_path}" ]; then
    #         mamba env create -p "${env_path}" -f "${environment_path}"
    #     else
    #         mamba env create -p "${env_path}"
    #     fi

    #     # Create the directory if it doesn't exist
    #     mkdir -p "${env_path}/etc/conda/activate.d"
    #     # Create a script to set your variable
    #     echo "export ${env_var_name}="active"" > "${env_path}/etc/conda/activate.d/env_vars.sh"

    #     # Create the directory if it doesn't exist
    #     mkdir -p "${env_path}/etc/conda/deactivate.d"

    #     # Create a script to unset your variable
    #     echo "unset ${env_var_name}" > "${env_path}/etc/conda/deactivate.d/env_vars.sh"
    # fi
}

# $1 - Environment name
# $2 - Path to the specific environment.yml
#
# Examples:
#   --Create an empty environment--
#   create_project_env "host_nre_pipeline_env"
#   --Create an environment with the environment file
#   create_project_env "host_nre_pipeline_env" "host_nre_pipeline_env.environment.yml"
#
create_project_env "$*"