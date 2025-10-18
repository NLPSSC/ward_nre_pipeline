@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM Script: push_gitbundle.bat
REM Purpose: Create a timestamped git bundle and upload it to lambda-server
REM Author: Generated script for NRE Pipeline
REM ============================================================================

echo [INFO] Starting git bundle creation and upload process...

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
set "formatted_datetime=%month%_%day%_%year%__%hour%_%minute%_%second%"
echo [INFO] Generated timestamp: %formatted_datetime%

REM Setup paths and directories
set "script_path=%~dp0"
set "project_root=%script_path%..\..\"
echo [DEBUG] Project root: %project_root%

REM Navigate to .data directory
cd /d "%project_root%.data"
if !errorlevel! neq 0 (
    echo [ERROR] Failed to navigate to .data directory: %project_root%.data
    exit /b 1
)
echo [DEBUG] Current directory: %cd%

REM Create bundle filename and ensure bundles directory exists
set "project_name=ward_nre_pipeline"
set "file_name=%formatted_datetime%_%project_name%.bundle"
set "bundle_path=%cd%\bundles"
echo [DEBUG] Creating bundles directory: %bundle_path%
mkdir "%bundle_path%" 2>nul
set "filepath=%bundle_path%\%file_name%"
echo [INFO] Bundle will be created at: %filepath%

REM Remote server configuration
set "remote_configuration=lambda-server"
set "remote_update_path=/home/westerd/_/research_projects/upload"
set "remote_upload_dest=%remote_configuration%:%remote_update_path%"
set "remote_repo=/home/westerd/_/research_projects/%project_name%"
echo [INFO] Remote server: %remote_configuration%
echo [INFO] Upload path: %remote_upload_dest%
echo [INFO] Remote repo: %remote_repo%

REM Navigate back to project root for git operations
cd /d "%project_root%"
if !errorlevel! neq 0 (
    echo [ERROR] Failed to navigate back to project root
    exit /b 1
)

REM Step 1: Create git bundle
echo [INFO] Creating git bundle with all branches and tags...
git push && git bundle create "%filepath%" --all
if !errorlevel! neq 0 (
    echo [ERROR] Failed to create git bundle
    exit /b 1
)
echo [SUCCESS] Git bundle created successfully: %file_name%

REM Step 2: Upload bundle to remote server
echo [INFO] Uploading bundle to remote server...
scp "%filepath%" %remote_upload_dest%
if !errorlevel! neq 0 (
    echo [ERROR] Failed to upload bundle via SCP
    exit /b 1
)
echo [SUCCESS] Bundle uploaded successfully

REM Step 3: Update remote repository
echo [INFO] Updating remote repository...
set "n_to_keep=5"
set "remote_cmd=cd %remote_repo%"
set "remote_cmd=%remote_cmd% && git fetch ../upload/%file_name%"
set "remote_cmd=%remote_cmd% && git rebase FETCH_HEAD"
set "bash_clean_cmd=cd %remote_update_path% && ls -1t | tail -n +$((%n_to_keep%+1)) | xargs -d '\n' rm --"
set "remote_cmd=%remote_cmd% && %bash_clean_cmd%"

ssh %remote_configuration% "%remote_cmd%"
if !errorlevel! neq 0 (
    echo [WARNING] Remote repository update may have failed - check manually
    exit /b 1
)
echo [SUCCESS] Remote repository updated successfully

REM Cleanup and completion

echo [INFO] Cleaning up local bundle files...

pushd "%bundle_path%"
setlocal enabledelayedexpansion
set count=0
for /f "delims=" %%F in ('dir /b /a:-d /o-d') do (
    set /a count+=1
    if !count! gtr 5 (
        del "%%F"
    )
)
endlocal
popd

echo.
echo [INFO] ============================================================================
echo [INFO] Git bundle process completed successfully
echo [INFO] Bundle file: %file_name%
echo [INFO] Local path: %filepath%
echo [INFO] Remote path: %remote_upload_path%/%file_name%
echo [INFO] ============================================================================
echo.

endlocal
exit /b 0


