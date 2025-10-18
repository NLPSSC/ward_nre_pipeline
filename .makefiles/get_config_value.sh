#!/bin/bash
# Usage: ./get_config_value.sh <key> <subkey>
#
# Example: ./get_config_value.sh python38_base 'text'
#   Returns the value "Python 3.8"
CONFIG_FILE=".makefiles/build_images.config.json"

key="$1"
subkey="$2"

jq -r --arg k "$key" --arg s "$subkey" '.[$k][$s]' "$CONFIG_FILE"