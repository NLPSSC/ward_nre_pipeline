## Installing Devcontainer

```bash
if [[ -z $CONDA_PREFIX ]]; then
    conda activate
fi

if ! command -v node >/dev/null 2>&1; then
    conda install nodejs -c conda-forge
fi

if ! command -v devcontainer >/dev/null 2>&1; then
    npm i -g @devcontainers/cli
fi
```