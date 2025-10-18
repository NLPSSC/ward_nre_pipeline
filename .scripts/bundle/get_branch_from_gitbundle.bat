@echo off
setlocal

set "script_path=%~dp0"
set "project_root=%script_path%..\..\"
cd %project_root%
echo [DEBUG] Project root: %cd%

REM Get current timestamp using wmic (more reliable than date/time commands)
echo [DEBUG] Retrieving current timestamp...
for /f %%a in ('wmic OS Get localdatetime ^| find "."') do set dt=%%a

if not defined dt (
    echo [ERROR] Failed to retrieve system datetime
    exit /b 1
)

REM Extract date and time components from wmic output (format: YYYYMMDDHHMMSS.milliseconds+timezone)
set "year=%dt:~0,4%"
set "month=%dt:~4,2%"
set "day=%dt:~6,2%"
set "hour=%dt:~8,2%"
set "minute=%dt:~10,2%"
set "second=%dt:~12,2%"

REM Construct timestamp in MM_DD_YYYY__HH_MM_SS format
set "unique_id=%month%_%day%_%year%__%hour%_%minute%_%second%"
echo [INFO] Generated unique_id: %unique_id%

REM Navigate to .data directory
cd /d ".data"
if errorlevel 1 (
    echo [ERROR] Failed to navigate to .data directory
    exit /b 1
)
@REM Z:\_\active\nlpssc\project_ward_non-routine_events\nre_pipeline\.data
echo [DEBUG] Current directory: %cd%


set "remote_folder=~/_/research_projects/ward_nre_pipeline"
set "download_folder=~/_/research_projects/download"
set "new_branch=fetch_%unique_id%"
set "main_branch=master"
set "bundle_path=%cd%\bundles"
echo [DEBUG] Creating bundles directory: %bundle_path%
mkdir "%bundle_path%" 2>nul
set "file_name=%new_branch%.bundle"
set "filepath=%bundle_path%\%file_name%"

ssh lambda-server "cd %remote_folder% && git bundle create %download_folder%/%file_name% %main_branch%"^
 && scp lambda-server:%download_folder%/%file_name% %filepath%^
 && git fetch %filepath% %main_branch%:%new_branch%


endlocal
