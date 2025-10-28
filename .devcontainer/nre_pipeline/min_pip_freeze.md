# Minimal Pip Freeze for NRE Pipeline Development Container

## Files

| File Name             | Purpose                                      |
| --------------------- | -------------------------------------------- |
| requirements.grep.yml | List of packages to grep from requirements   |
| requirements-dev.txt  | Development dependencies for NRE Pipeline    |
| requirements.txt      | Production dependencies for NRE Pipeline     |
| parse_pip_yml.py      | Script to parse the YAML and generate freeze |

## Generating the Files for dev and prod

To generate the `requirements-dev.txt` and `requirements.txt` files, use the following commands:

```bash
python -m pip freeze | grep -E "^("$(./parse_pip_yml.py dev)")==" > requirements-dev.txt
python -m pip freeze | grep -E "^("$(./parse_pip_yml.py prod)")==" > requirements.txt
```