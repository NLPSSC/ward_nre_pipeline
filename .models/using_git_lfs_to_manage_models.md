# TODO - What will this do for files in .gitignore?

```bash
for f in "$(find ./.models -type f -size +50M -print)"; do
    echo "Tracking ${f} with Git LFS..." && \
        git lfs track "${f}" && \
        git add .gitattributes "${f}" && \
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