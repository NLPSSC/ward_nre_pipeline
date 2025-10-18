@echo off
REM Script to install QuickUMLS with a UMLS subset
REM Usage: quickumls_subset_install.bat <umls_subset_path> <destination_path>

setlocal enabledelayedexpansion

REM Get the directory of the current script
set "script_dir=%~dp0"
for %%i in ("%script_dir%..") do set "PROJECT_ROOT=%%~fi"

REM Check if running inside a conda environment
if "%CONDA_DEFAULT_ENV%"=="" (
    echo Error: No conda environment is active. Please activate the appropriate environment before running this script.
    exit /b 10
)

set "umls_subset_path=%~1"
set "destination_path=%~2"

REM Trim any trailing spaces
for /f "tokens=* delims= " %%a in ("%umls_subset_path%") do set "umls_subset_path=%%a"
for /f "tokens=* delims= " %%a in ("%destination_path%") do set "destination_path=%%a"

REM Ensure destination_path ends with \META
if not "%umls_subset_path:~-5%"=="\META" (
    set "umls_subset_path=%umls_subset_path%\META"
)

if "%umls_subset_path%"=="" (
    echo Usage: %~nx0 ^<umls_subset_path^> ^<destination_path^>
    exit /b 1
)

if "%destination_path%"=="" (
    echo Usage: %~nx0 ^<umls_subset_path^> ^<destination_path^>
    exit /b 1
)

if not exist "%umls_subset_path%" (
    echo Error: UMLS subset path '%umls_subset_path%' does not exist.
    exit /b 2
)

if not exist "%destination_path%" (
    echo Warning: Destination path '%destination_path%' does not exist. Creating.
    mkdir "%destination_path%"
)

echo %destination_path% >> "%PROJECT_ROOT%\\.gitignore"

python -m quickumls.install -L -U "%umls_subset_path%" "%destination_path%"
