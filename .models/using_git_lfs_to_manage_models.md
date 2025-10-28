# TODO - What will this do for files in .gitignore?

```bash
DRYRUN=1
for f in $(find ./.models -type f -size +50M -print); do
    if [ "${DRYRUN}" == "1" ]; then
        echo "[DRYRUN] Tracking ${f} with Git LFS..." && \
        echo git lfs track "${f}" && \
        echo git add .gitattributes && \
        echo git commit -m "Tracking ${f}" && \
        echo git add -f "${f}" && \
        echo git commit -m "Tracking ${f}" && \
        echo git push
        continue
    fi

    echo "Tracking ${f} with Git LFS..." && \
        git lfs track "${f}" && \
        git add .gitattributes && \
        git commit -m "Tracking ${f}" && \
        git add -f "${f}" && \
        git commit -m "Tracking ${f}" && \
        git push
    # check the error code of the last command
    if [ $? -ne 0 ]; then
        echo "Error tracking ${f} with Git LFS"
        exit 1
    fi
done
```