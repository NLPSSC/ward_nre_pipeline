# PowerShell script to install Genalog environment

param(
    [switch]$CleanAndReclone = $true
)

# Set colors for logging
$ColorOriginal = $Host.UI.RawUI.ForegroundColor
$ColorRed = "Red"
$ColorGreen = "Green" 
$ColorYellow = "Yellow"
$ColorBlue = "Blue"
$ColorWhite = "White"

$Host.UI.RawUI.ForegroundColor = $ColorWhite

# Logging functions
function Write-LogCmd {
    param([string]$Message)
    $Host.UI.RawUI.ForegroundColor = $ColorBlue
    Write-Host "[CMD] $Message"
    $Host.UI.RawUI.ForegroundColor = $ColorOriginal
}

function Write-LogError {
    param([string]$Message)
    $Host.UI.RawUI.ForegroundColor = $ColorRed
    Write-Host "[ERROR] $Message"
    $Host.UI.RawUI.ForegroundColor = $ColorOriginal
}

function Write-LogInfo {
    param([string]$Message)
    $Host.UI.RawUI.ForegroundColor = $ColorBlue
    Write-Host "[INFO] $Message"
    $Host.UI.RawUI.ForegroundColor = $ColorOriginal
}

# Set script and project directories
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $ScriptDir "..\..") 
$ProjectRoot = Get-Location

# Change to project root
Set-Location $ProjectRoot

$GenalogPrefixPath = "$ProjectRoot\envs\genalog_env"

if (Test-Path $GenalogPrefixPath) {
    Write-LogCmd "Removing existing conda environment at $GenalogPrefixPath"
    mamba env remove -p $GenalogPrefixPath
}

# Main install block
$InstallPath = Join-Path $ProjectRoot "src\genalog_api"

if ($CleanAndReclone) {
    if (Test-Path $InstallPath) {
        Remove-Item $InstallPath -Recurse -Force
    }
}
else {
    Write-LogInfo "Skipping removal of existing install directory."
}


if (-not (Test-Path $InstallPath)) {
    Write-LogInfo "Creating new install directory at $InstallPath"
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
}
Set-Location $InstallPath

# Clone the repository
if ($CleanAndReclone) {
    try {
        git clone git@github.com:NLPSSC/genalog.git $PWD
        if ($LASTEXITCODE -ne 0) {
            throw "Git clone failed!"
        }
    }
    catch {
        Write-Host "Git clone failed!" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-LogInfo "Skipping git clone."
}

Push-Location $InstallPath
# Deactivate conda environment if not in base
$condaInfo = mamba info --json | ConvertFrom-Json
$currentEnv = $condaInfo.active_prefix_name
if ($currentEnv -ne "base") {
    Write-LogCmd "Deactivating current conda environment: $currentEnv"
    mamba deactivate
}

Push-Location $InstallPath

Write-LogInfo "Current directory: $PWD"


$EnvFilePath = Join-Path $ProjectRoot ".env"
if (-not (Test-Path $EnvFilePath)) {
    Write-LogInfo "Creating .env file at $EnvFilePath"
    "PYTHONPATH=src" | Out-File -FilePath $EnvFilePath -Encoding utf8
}


try {
    mamba env create -f .\environment.yml -p "$ProjectRoot\envs\genalog_env"
    if ($LASTEXITCODE -ne 0) {
        throw "Conda environment creation failed!"
    }
}
catch {
    Write-LogError "Conda environment creation failed!"
    exit 1
}


# Run environment setup
# $EnvSetupScript = Join-Path $InstallPath "scripts\create-genalog-env.ps1"
# Write-LogCmd "Executing environment setup script: $EnvSetupScript"

# try {
#     & $EnvSetupScript
#     if ($LASTEXITCODE -ne 0) {
#         throw "Environment setup failed!"
#     }
# }
# catch {
#     Write-LogError "Environment setup failed!"
#     exit 1
# }

# # Clean up
# Set-Location $ProjectRoot
# if ($CleanAndReclone) {
#     Remove-Item $InstallPath -Recurse -Force
# }
# else {
#     Write-LogInfo "Skipping removal of existing install directory."
# }