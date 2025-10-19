#!/usr/bin/env bash

function create_project_env {

    local env_prefix="_NRE_ENV"
    local conda_env_name="$1"
    local environment_path=""
    local env_path="./envs/${conda_env_name}"
    local env_var_name

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

    # if [ ! -d ./envs ]; then
    #     echo "Cannot locate ./envs" && echo 1
    # fi

    # if [ -z "${environment_path}" ]; then
    #     if [ ! -f "${environment_path}" ]; then
    #         echo "Cannot local environment path ${environment_path}."
    #     fi
    # fi

    # if [ -d "${env_path}" ]; then
    #     mamba create -p "${env_path}" -f 
    # else
    #     env_var_name="${env_prefix}_${conda_env_name}"

    #     mamba env create -p "${env_path}"

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
create_project_env "$1" "$2"