# PowerShell script to install Genalog environment

param(
    [switch]$CleanAndReclone = $false
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

# Main install block
$InstallPath = Join-Path $ProjectRoot "build\genalog"

if ($CleanAndReclone) {
    if (Test-Path $InstallPath) {
        Remove-Item $InstallPath -Recurse -Force
    }
}
else {
    Write-LogInfo "Skipping removal of existing install directory."
}

if (-not (Test-Path $InstallPath)) {
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

# Run environment setup
$EnvSetupScript = Join-Path $InstallPath "scripts\create-genalog-env.bat"
Write-LogCmd "`"$EnvSetupScript`" `"$ProjectRoot`""

try {
    & $EnvSetupScript $ProjectRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Environment setup failed!"
    }
}
catch {
    Write-LogError "Environment setup failed!"
    exit 1
}

# Clean up
Set-Location $ProjectRoot
if ($CleanAndReclone) {
    Remove-Item $InstallPath -Recurse -Force
}
else {
    Write-LogInfo "Skipping removal of existing install directory."
}

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