@echo off

setlocal enabledelayedexpansion

:: Set colors for logging
set "COLOR_ORIGINAL="
for /f "tokens=1,2 delims==" %%a in ('color') do if "%%a"=="Color" set "COLOR_ORIGINAL=%%b"
set "COLOR_RED=0C"
set "COLOR_GREEN=0A"
set "COLOR_YELLOW=0E"
set "COLOR_BLUE=09"
set "COLOR_WHITE=0F"

color %COLOR_WHITE%


set "CLEAN_AND_RECLONE=0"

REM Set script and project directories
set "SCRIPT_DIR=%~dp0"
cd "%SCRIPT_DIR%\..\.."
set "PROJECT_ROOT=%CD%"

REM Change to project root
cd "%PROJECT_ROOT%"

REM Main install block
set "INSTALL_PATH=%PROJECT_ROOT%\\build\\genalog"

IF "%CLEAN_AND_RECLONE%"=="1" (
    IF EXIST "%INSTALL_PATH%" (
        rmdir /s /q "%INSTALL_PATH%"
    )
) else (
    call :log_info "Skipping removal of existing install directory."
)

IF NOT EXIST "%INSTALL_PATH%" mkdir "%INSTALL_PATH%"
cd "%INSTALL_PATH%"

REM Clone the repository
IF "%CLEAN_AND_RECLONE%"=="1" (
    git clone git@github.com:NLPSSC/genalog.git "%CD%"
    IF ERRORLEVEL 1 (
        echo Git clone failed!
        exit /b 1
    )
) else (
    call :log_info "Skipping git clone."
)

REM Run environment setup

echo "%INSTALL_PATH%\\scripts\\create-genalog-env.bat %PROJECT_ROOT%"
IF ERRORLEVEL 1 (
	call :log_error "Environment setup failed!"
	exit /b 1
)

REM Clean up
cd "%PROJECT_ROOT%"
IF "%CLEAN_AND_RECLONE%"=="1" (
    rmdir /s /q "%INSTALL_PATH%"
) else (
    call :log_info "Skipping removal of existing install directory."
)

exit /b

:log_cmd 
    color %COLOR_BLUE%
    ECHO [CMD] %*
    color %COLOR_ORIGINAL%
GOTO :EOF

:log_error
    color %COLOR_RED%
    ECHO [ERROR] %*
    color %COLOR_ORIGINAL%
GOTO :EOF

:log_info
    color %COLOR_BLUE%
    ECHO [INFO] %*
    color %COLOR_ORIGINAL%
GOTO :EOF