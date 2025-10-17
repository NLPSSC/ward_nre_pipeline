.SILENT:

# Makefile for Windows (requires GNU Make or nmake)

PRIMARY_ENV_PREFIX=envs\nre_pipeline
GENALOG_ENV_PREFIX=envs\genalog_env
PYTHON=$(PRIMARY_ENV_PREFIX)/Scripts/python.exe
PIP=$(PRIMARY_ENV_PREFIX)/Scripts/pip.exe
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
	@rmdir /s /q __pycache__
	@del /s /q build dist *.egg-info

env-backup:
	-$(MAKE) git-add-commit item_path=environment.yml \
	description="backup before recreation" >nul 2>&1 || cmd /c exit 0

env-export:
	$(MAKE) env-backup >nul 2>&1
	@mamba env export --no-builds --prefix $(PRIMARY_ENV_PREFIX) > temp_env.yml
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
	@if exist $(PRIMARY_ENV_PREFIX) (\
		mamba env update -f environment.yml --prefix $(PRIMARY_ENV_PREFIX) \
	) else (\
		mamba env create -f environment.yml --prefix $(PRIMARY_ENV_PREFIX) \
	)

git-add-commit:
	@git add "$(item_path)"
	@git commit -m "$(description) [$(item_path)]"

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

create-genalog-env:
	@powershell -ExecutionPolicy Bypass -File "scripts\genalog\install-genalog-env.ps1"
