.SILENT:

# Makefile for Windows (requires GNU Make or nmake)

ENV_NAME=envs/nre_pipeline
PYTHON=$(ENV_NAME)/Scripts/python.exe
PIP=$(ENV_NAME)/Scripts/pip.exe
ACTIVATE=for %%A in ("%CONDA_EXE%") do call "%%~dpAactivate.bat"

.PHONY: install test clean env-backup env-export env-build git-add-commit quickumls-install

install:
	$(MAKE) env-build
	@$(ACTIVATE) && $(PYTHON) -m pip install -e .
	$(MAKE) quickumls-install

test:
	@$(ACTIVATE) && $(PYTHON) -m pytest tests

clean:
	@del /s /q *.pyc *.pyo
	@del /s /q __pycache__
	@del /s /q build dist *.egg-info

env-backup:
	-$(MAKE) git-add-commit item_path=environment.yml \
	description="backup before recreation" >nul 2>&1 || cmd /c exit 0

env-export:
	$(MAKE) env-backup >nul 2>&1
	@mamba env export --no-builds --prefix $(ENV_NAME) > temp_env.yml
	@powershell -Command \
	"$$lines = Get-Content temp_env.yml; $$output = @(); $$i = 0; \
	while ($$i -lt $$lines.Length) { $$line = $$lines[$$i]; \
	if ($$line -match '^name:') { $$output += 'name:'; \
	$$output += '  nre_pipeline'; $$i++; \
	while ($$i -lt $$lines.Length -and $$lines[$$i] -match '^  ') { $$i++ } \
	} elseif ($$line -match '^prefix:') { $$output += 'prefix:'; \
	$$output += '  .\envs\nre_pipeline'; $$i++; \
	while ($$i -lt $$lines.Length -and $$lines[$$i] -match '^  ') { $$i++ } \
	} else { $$output += $$line; $$i++ } }; \
	$$output | Set-Content environment.yml"
	@del temp_env.yml

env-build:
	@if exist $(ENV_NAME) (\
		mamba env update -f environment.yml --prefix $(ENV_NAME) \
	) else (\
		mamba env create -f environment.yml --prefix $(ENV_NAME) \
	)

git-add-commit:
	@set ITEM_NAME=$(notdir $(item_path)) && \
	git add "$(item_path)" && \
	git commit -m "$(description) [$$ITEM_NAME]"

quickumls-install:
	@echo @echo off > temp_install.bat
	@echo setlocal enabledelayedexpansion >> temp_install.bat
	@echo for /f "usebackq tokens=1,2 delims==" %%%%A in (".env") do ( >> temp_install.bat
	@echo   set "var=%%%%A" >> temp_install.bat
	@echo   set "val=%%%%B" >> temp_install.bat
	@echo   for /f "tokens=* delims= " %%%%x in ("!val!") do set "!var!=%%%%x" >> temp_install.bat
	@echo ^) >> temp_install.bat
	@echo call scripts\quickumls_subset_install.bat "%%UMLS_SUBSET_SOURCE%%" "%%QUICKUMLS_DATA%%" >> temp_install.bat
	@call temp_install.bat
	@del temp_install.bat
