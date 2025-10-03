# Makefile for Windows (requires GNU Make or nmake)

ENV_NAME=envs/nre_pipeline
PYTHON=$(ENV_NAME)/Scripts/python.exe
PIP=$(ENV_NAME)/Scripts/pip.exe
ACTIVATE=for %%A in ("%CONDA_EXE%") do call "%%~dpAactivate.bat"

.PHONY: env install test clean environment-export

env:
	@mamba env create -f environment.yml --prefix $(ENV_NAME) || mamba env update -f environment.yml --prefix $(ENV_NAME)

install:
	@$(ACTIVATE) && $(PYTHON) -m pip install -e .

test:
	@$(ACTIVATE) && $(PYTHON) -m pytest tests

clean:
	@del /s /q *.pyc *.pyo
	@del /s /q __pycache__
	@del /s /q build dist *.egg-info

env-export:
	$(MAKE) git-add-commit item_path=environment.yml description="backup before recreation"
	@mamba env export --no-builds --prefix $(ENV_NAME) > temp_env.yml
	@powershell -Command "$$lines = Get-Content temp_env.yml; $$output = @(); $$i = 0; while ($$i -lt $$lines.Length) { $$line = $$lines[$$i]; if ($$line -match '^name:') { $$output += 'name:'; $$output += '  nre_pipeline'; $$i++; while ($$i -lt $$lines.Length -and $$lines[$$i] -match '^  ') { $$i++ } } elseif ($$line -match '^prefix:') { $$output += 'prefix:'; $$output += '  .\envs\nre_pipeline'; $$i++; while ($$i -lt $$lines.Length -and $$lines[$$i] -match '^  ') { $$i++ } } else { $$output += $$line; $$i++ } }; $$output | Set-Content environment.yml"
	@del temp_env.yml

git-add-commit:
	@set ITEM_NAME=$(notdir $(item_path)) && \
	git add "$(item_path)" && \
	git commit -m "$(description) [$$ITEM_NAME]"
