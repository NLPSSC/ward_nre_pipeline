#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(realpath "${SCRIPT_DIR}/../..")"
cd "${PROJECT_ROOT}" || exit 1
cd .models || exit 1

GIT_LFS_THRESHOLD=50
echo "Using Git LFS threshold of ${GIT_LFS_THRESHOLD}MB"

DRYRUN=0
# Check for --dry-run argument
for arg in "$@"; do
    if [ "$arg" = "--dry-run" ]; then
        DRYRUN=1
        break
    fi
done


EXT_TO_MONITOR=("*.cdb")

# Find files over the threshold and assign to array
mapfile -t FILES_FOR_GIT_LFS < <(find . -type f -size +${GIT_LFS_THRESHOLD}M -print)
for ext in "${EXT_TO_MONITOR[@]}"; do
    echo "Searching for files with extension ${ext} to track with Git LFS..."
    while IFS= read -r -d '' file; do
        FILES_FOR_GIT_LFS+=("$file")
    done < <(find . -type f -name "${ext}" -print0)
done

# Remove files already tracked by git from FILES_FOR_GIT_LFS
echo "Filtering out files already tracked by git..."
filtered_files=()
file_count_removed_from_tracking=0
for f in "${FILES_FOR_GIT_LFS[@]}"; do
    # Check if file is already tracked by git
    if ! git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
        filtered_files+=("$f")
    else
        echo "Skipping already tracked file: $f"
        file_count_removed_from_tracking=$((file_count_removed_from_tracking + 1))
    fi
done

echo "Removed ${file_count_removed_from_tracking} files already tracked by git from the list."

FILES_FOR_GIT_LFS=("${filtered_files[@]}")

FILE_COUNT="${#FILES_FOR_GIT_LFS[@]}"
echo "Found ${FILE_COUNT} files larger than ${GIT_LFS_THRESHOLD}MB or with monitored extensions - ${EXT_TO_MONITOR[*]} - to track with Git LFS."


current_index=0

for f in "${FILES_FOR_GIT_LFS[@]}"; do
    # ASCII progress bar
    bar_width=40
    percent=$(( (100 * (current_index + 1)) / FILE_COUNT ))
    num_hashes=$(( (bar_width * percent) / 100 ))
    num_spaces=$(( bar_width - num_hashes ))
    bar=$(printf "%0.s#" $(seq 1 $num_hashes))
    spaces=$(printf "%0.s " $(seq 1 $num_spaces))
    echo -ne "\rProcessing file $((current_index + 1)) of ${FILE_COUNT} [${bar}${spaces}]"
    current_index=$((current_index + 1))

    if [ "${DRYRUN}" == "1" ]; then
        continue
    fi

    git lfs track "${f}" >/dev/null 2>&1 && \
    git add .gitattributes >/dev/null 2>&1 && \
    git commit -m "Tracking ${f}" >/dev/null 2>&1 && \
    git add -f "${f}" >/dev/null 2>&1 && \
    git commit -m "Tracking ${f}" >/dev/null 2>&1 && \
    git push >/dev/null 2>&1
    # check the error code of the last command
    if [ $? -ne 0 ]; then
        echo "Error tracking ${f} with Git LFS"
        exit 1
    fi

done
echo # print newline after progress bar