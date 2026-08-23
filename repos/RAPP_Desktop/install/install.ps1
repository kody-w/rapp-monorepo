$ErrorActionPreference = "Stop"

$RappHome = "$env:USERPROFILE\.rapp"
$InstallDirectory = Join-Path $RappHome "app"

function Write-RappLog {
    param([string]$Message)
    Write-Host "[RAPP] $Message" -ForegroundColor Cyan
}

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name is required. Install it and run the installer again."
    }
}

Require-Command "git"
Require-Command "node"
Require-Command "npm"
Require-Command "python"

$NodeVersionParts = (node --version).TrimStart("v").Split(".")
$NodeMajor = [int]$NodeVersionParts[0]
$NodeMinor = [int]$NodeVersionParts[1]
if (($NodeMajor -lt 22) -or (($NodeMajor -eq 22) -and ($NodeMinor -lt 12))) {
    throw "Node.js 22.12.0 or newer is required."
}

New-Item -ItemType Directory -Force -Path $RappHome | Out-Null
if (Test-Path (Join-Path $InstallDirectory ".git")) {
    Write-RappLog "Updating RAPP Desktop..."
    git -C $InstallDirectory pull --ff-only origin main
} else {
    Write-RappLog "Cloning RAPP Desktop..."
    git clone https://github.com/kody-w/RAPP_Desktop.git $InstallDirectory
}

Set-Location $InstallDirectory
Write-RappLog "Building the Electron companion..."
npm ci
npm run dist

Write-RappLog "Preparing the bundled Brainstem fallback..."
$VenvDirectory = Join-Path $RappHome "venv"
python -m venv $VenvDirectory
$VenvPython = Join-Path $VenvDirectory "Scripts\python.exe"
& $VenvPython -m pip install --quiet --upgrade pip
& $VenvPython -m pip install --quiet -r "rapp_os\requirements.txt"

@("agents", "skills", "projects", "contexts", "memory") | ForEach-Object {
    New-Item -ItemType Directory -Force -Path (Join-Path $RappHome $_) | Out-Null
}

$Launcher = @"
@echo off
"$VenvPython" "$InstallDirectory\rapp_os\rapp_os.py" %*
"@
Set-Content -Path (Join-Path $RappHome "rapp.bat") -Value $Launcher

$Setup = Get-ChildItem -Path (Join-Path $InstallDirectory "release") `
    -Filter "RAPP Desktop-*-win-*.exe" -Recurse |
    Select-Object -First 1
if (-not $Setup) {
    throw "The Windows installer was not produced."
}

Write-RappLog "Installing RAPP Desktop..."
Start-Process -FilePath $Setup.FullName -ArgumentList "/S" -Wait
Write-RappLog "RAPP Desktop is ready."
