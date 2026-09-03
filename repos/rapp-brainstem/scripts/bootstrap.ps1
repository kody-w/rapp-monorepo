[CmdletBinding()]
param(
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$')]
    [string]$Actor = 'github-copilot'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

try {
    [Net.ServicePointManager]::SecurityProtocol = `
        [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
} catch {}

function Fail([string]$Message) {
    throw "RAPP Brainstem bootstrap failed: $Message"
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Assert-RegularFile([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Fail "trusted local file is missing: $Path"
    }
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Fail "trusted local file is a reparse point: $Path"
    }
}

function Assert-Hash([string]$Path, [string]$Expected) {
    Assert-RegularFile $Path
    if ((Get-Sha256 $Path) -ne $Expected) {
        Fail "trusted local file hash mismatch: $Path"
    }
}

function Ensure-RealDirectory([string]$Path) {
    [void](New-Item -ItemType Directory -Path $Path -Force)
    $item = Get-Item -LiteralPath $Path -Force
    if (-not $item.PSIsContainer -or
        (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        Fail "refusing non-directory or reparse-point path: $Path"
    }
}

function Protect-PrivateDirectory([string]$Path) {
    try {
        $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
        $security = New-Object Security.AccessControl.DirectorySecurity
        $security.SetAccessRuleProtection($true, $false)
        $rule = New-Object -TypeName Security.AccessControl.FileSystemAccessRule `
            -ArgumentList @(
                $sid,
                [Security.AccessControl.FileSystemRights]::FullControl,
                [Security.AccessControl.InheritanceFlags]'ContainerInherit, ObjectInherit',
                [Security.AccessControl.PropagationFlags]::None,
                [Security.AccessControl.AccessControlType]::Allow
            )
        [void]$security.AddAccessRule($rule)
        Set-Acl -LiteralPath $Path -AclObject $security
    } catch {
        Fail "could not make bootstrap state private: $Path"
    }
}

function Write-Utf8NoBom([string]$Path, [string]$Value) {
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($Path, $Value, $encoding)
}

function Get-ProcessCreationIdentity([int]$ProcessId) {
    try {
        $process = Get-Process -Id $ProcessId -ErrorAction Stop
    } catch {
        return [pscustomobject]@{ Exists = $false; Identity = $null }
    }
    try {
        $ticks = $process.StartTime.ToUniversalTime().Ticks
        return [pscustomobject]@{
            Exists = $true
            Identity = "windows-start-ticks:$ticks"
        }
    } catch {
        return [pscustomobject]@{ Exists = $true; Identity = $null }
    }
}

function Acquire-BootstrapLock([string]$Path, [string]$StateHome) {
    $owner = Get-ProcessCreationIdentity $PID
    if (-not $owner.Exists -or -not $owner.Identity) {
        Fail 'cannot establish bootstrap process creation identity'
    }
    $record = [ordered]@{
        schema = 'rapp-brainstem-bootstrap-lock/1'
        pid = $PID
        creation_identity = $owner.Identity
        nonce = [Guid]::NewGuid().ToString('N')
    }
    $candidate = Join-Path $StateHome ".bootstrap-lock-owner-$PID-$($record.nonce)"
    Write-Utf8NoBom $candidate (($record | ConvertTo-Json -Compress) + "`n")
    $script:BootstrapLockOwnerHash = Get-Sha256 $candidate
    try {
        [IO.File]::Move($candidate, $Path)
        $script:BootstrapLockHeld = $true
        return
    } catch [IO.IOException] {
    }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Remove-Item -LiteralPath $candidate -Force -ErrorAction SilentlyContinue
        Fail 'bootstrap lock is not a regular file'
    }
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Remove-Item -LiteralPath $candidate -Force -ErrorAction SilentlyContinue
        Fail 'bootstrap lock is a reparse point'
    }
    $currentHash = Get-Sha256 $Path
    try {
        $current = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        Remove-Item -LiteralPath $candidate -Force -ErrorAction SilentlyContinue
        Fail 'bootstrap lock is unreadable; refusing unsafe recovery'
    }
    $propertyNames = @(
        $current.PSObject.Properties.Name | Sort-Object
    )
    if (
        ($propertyNames -join ',') -ne 'creation_identity,nonce,pid,schema' -or
        $current.schema -ne 'rapp-brainstem-bootstrap-lock/1' -or
        -not (
            $current.pid -is [int] -or
            $current.pid -is [long]
        ) -or
        [string]::IsNullOrWhiteSpace([string]$current.creation_identity) -or
        [string]::IsNullOrWhiteSpace([string]$current.nonce)
    ) {
        Remove-Item -LiteralPath $candidate -Force -ErrorAction SilentlyContinue
        Fail 'bootstrap lock record is invalid'
    }
    $snapshot = Get-ProcessCreationIdentity ([int]$current.pid)
    if ($snapshot.Exists -and -not $snapshot.Identity) {
        Remove-Item -LiteralPath $candidate -Force -ErrorAction SilentlyContinue
        Fail 'bootstrap lock owner cannot be inspected safely'
    }
    if (
        $snapshot.Exists -and
        $snapshot.Identity -eq [string]$current.creation_identity
    ) {
        Remove-Item -LiteralPath $candidate -Force -ErrorAction SilentlyContinue
        Fail 'another RAPP Brainstem bootstrap is active'
    }
    Assert-Hash $Path $currentHash
    Remove-Item -LiteralPath $Path -Force
    try {
        [IO.File]::Move($candidate, $Path)
    } catch {
        Remove-Item -LiteralPath $candidate -Force -ErrorAction SilentlyContinue
        Fail 'another RAPP Brainstem bootstrap won the recovered lock'
    }
    $script:BootstrapLockHeld = $true
}

function Release-BootstrapLock([string]$Path) {
    if (-not $script:BootstrapLockHeld) { return }
    Assert-Hash $Path $script:BootstrapLockOwnerHash
    Remove-Item -LiteralPath $Path -Force
    $script:BootstrapLockHeld = $false
}

$ScriptDirectory = $PSScriptRoot
$PluginRoot = Split-Path -Parent $ScriptDirectory
$LockPath = Join-Path $PluginRoot 'installer-lock.json'
if ([string]::IsNullOrWhiteSpace($env:USERPROFILE)) {
    Fail 'USERPROFILE is not set'
}
$UserHome = $env:USERPROFILE
$BootstrapStateHome = Join-Path $UserHome '.rapp/brainstem-bootstrap'
$EnvelopeDirectory = Join-Path $BootstrapStateHome 'envelopes'
$DownloadDirectory = Join-Path $BootstrapStateHome 'downloads'
$FailedDirectory = Join-Path $BootstrapStateHome 'failed'
$BrainstemHome = Join-Path $UserHome '.brainstem'

Assert-Hash $LockPath 'e699ad5978cb91b7014011392c3e0619169e239d3418b9e8bdc2098588badf55'
Assert-Hash (Join-Path $PluginRoot 'rapp_operator/__init__.py') '4da21ba688c0d6306dddc09f0db442993139b6906e0732b6ed48da184546aba3'
Assert-Hash (Join-Path $PluginRoot 'rapp_operator/rapp1.py') 'c3a30e448eb7b9ebfa7cca3b5b1e8cfa67486a0f78de8add7efb330b7efa9779'
Assert-Hash (Join-Path $PluginRoot 'rapp_operator/rappctl.py') 'c6cea66c4e695f844b187ef4568a9cd0b5dc65909a4557d398165cbb52b36115'

if (Test-Path -LiteralPath $BrainstemHome) {
    Fail "$BrainstemHome already exists; fresh bootstrap refuses existing state"
}
try {
    $health = Invoke-WebRequest -Uri 'http://127.0.0.1:7071/health/public' `
        -UseBasicParsing -TimeoutSec 2
    if ($health.StatusCode -eq 200) {
        Fail 'a RAPP Brainstem is already reachable'
    }
} catch {
    if ($_.Exception.Message -like 'RAPP Brainstem bootstrap failed:*') {
        throw
    }
}

Ensure-RealDirectory (Join-Path $UserHome '.rapp')
Ensure-RealDirectory $BootstrapStateHome
Ensure-RealDirectory $EnvelopeDirectory
Ensure-RealDirectory $DownloadDirectory
Ensure-RealDirectory $FailedDirectory
Protect-PrivateDirectory $BootstrapStateHome
Protect-PrivateDirectory $EnvelopeDirectory
Protect-PrivateDirectory $DownloadDirectory
Protect-PrivateDirectory $FailedDirectory

$CreatedUtc = [DateTime]::UtcNow.ToString(
    'yyyy-MM-ddTHH:mm:ss.fffZ',
    [Globalization.CultureInfo]::InvariantCulture
)

$EnvelopeTemporary = Join-Path $EnvelopeDirectory ".bootstrap-envelope.$PID"
$EnvelopeSha256 = $null
$InstallerPath = $null
$WorkDirectory = $null
$BootstrapLock = Join-Path $BootstrapStateHome '.bootstrap.lock'
$script:BootstrapLockHeld = $false
$script:BootstrapLockOwnerHash = $null
$MutationStarted = $false
$BootstrapSucceeded = $false
$FailureId = [DateTime]::UtcNow.ToString(
    'yyyyMMddTHHmmssZ',
    [Globalization.CultureInfo]::InvariantCulture
) + "-$PID"
Acquire-BootstrapLock $BootstrapLock $BootstrapStateHome
try {
    if (Test-Path -LiteralPath $BrainstemHome) {
        Fail 'RAPP Brainstem state appeared before planning'
    }
    $EnvelopeJson = @"
{
  "action": "bootstrap",
  "actor": "$Actor",
  "bootstrap_state_home": "~/.rapp/brainstem-bootstrap",
  "created_utc": "$CreatedUtc",
  "installer": {
    "arguments": [
      "--no-launch",
      "--version",
      "installers"
    ],
    "platform": "windows",
    "repository_ref": {
      "kind": "rolling-tag",
      "value": "installers"
    },
    "sha256": "0821162f6c1961d4037a9d0b591db5aca468864d2bb50b5c4ca409c506d7d3ca",
    "url": "https://raw.githubusercontent.com/microsoft/aibast-agents-library/c60521e2cacbcbfa585a118c1275093d7bb15b74/install.ps1"
  },
  "installer_lock": {
    "schema": "rapp-brainstem-installer-lock/3",
    "sha256": "e699ad5978cb91b7014011392c3e0619169e239d3418b9e8bdc2098588badf55"
  },
  "operator_bundle": {
    "files": [
      {
        "name": "__init__.py",
        "sha256": "4da21ba688c0d6306dddc09f0db442993139b6906e0732b6ed48da184546aba3"
      },
      {
        "name": "rapp1.py",
        "sha256": "c3a30e448eb7b9ebfa7cca3b5b1e8cfa67486a0f78de8add7efb330b7efa9779"
      },
      {
        "name": "rappctl.py",
        "sha256": "c6cea66c4e695f844b187ef4568a9cd0b5dc65909a4557d398165cbb52b36115"
      }
    ],
    "schema": "rapp-brainstem-operator-bundle/1",
    "sha256": "d007f602e1429f04aa60bd40bb63ba6756a1f1fc684fd8b8f469bd393dcb8e77"
  },
  "postconditions": {
    "brainstem_release": "exact-target",
    "live_verification": "required-separately",
    "managed_runtime": "stopped"
  },
  "preconditions": {
    "brainstem_release": "absent",
    "managed_runtime": "stopped",
    "protected_user_state": "absent"
  },
  "schema": "rapp-brainstem-bootstrap-envelope/2",
  "target_release": {
    "commit": "c60521e2cacbcbfa585a118c1275093d7bb15b74",
    "repository": "https://github.com/microsoft/aibast-agents-library.git",
    "tag": "installers",
    "tree": "3c5bb0d55ca4a5aff8872d30b8108e2438ef808d",
    "version": "0.6.16",
    "version_url": "https://raw.githubusercontent.com/microsoft/aibast-agents-library/c60521e2cacbcbfa585a118c1275093d7bb15b74/rapp_brainstem/VERSION"
  },
  "trust_anchor": {
    "authority": "executing-plugin-bundle",
    "kind": "local-marketplace-plugin",
    "plugin": "rapp-brainstem"
  }
}
"@
    Write-Utf8NoBom $EnvelopeTemporary $EnvelopeJson
    $EnvelopeSha256 = Get-Sha256 $EnvelopeTemporary
    $EnvelopePath = Join-Path $EnvelopeDirectory "$EnvelopeSha256.json"
    if (Test-Path -LiteralPath $EnvelopePath) {
        Assert-Hash $EnvelopePath $EnvelopeSha256
        Remove-Item -LiteralPath $EnvelopeTemporary -Force
    } else {
        Move-Item -LiteralPath $EnvelopeTemporary -Destination $EnvelopePath
    }
    $EnvelopeTemporary = $null

    if (Test-Path -LiteralPath $BrainstemHome) {
        Fail 'RAPP Brainstem state appeared after planning'
    }

    $InstallerPath = Join-Path $DownloadDirectory "installer-$EnvelopeSha256-$PID.ps1"
    Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/microsoft/aibast-agents-library/c60521e2cacbcbfa585a118c1275093d7bb15b74/install.ps1' -OutFile $InstallerPath `
        -UseBasicParsing -TimeoutSec 120
    Assert-Hash $InstallerPath '0821162f6c1961d4037a9d0b591db5aca468864d2bb50b5c4ca409c506d7d3ca'

    Ensure-RealDirectory (Join-Path $BootstrapStateHome 'work')
    $WorkDirectory = Join-Path $BootstrapStateHome "work/$EnvelopeSha256-$PID"
    Ensure-RealDirectory $WorkDirectory
    $env:TEMP = $WorkDirectory
    $env:TMP = $WorkDirectory
    $env:TMPDIR = $WorkDirectory
    $env:BRAINSTEM_REPO_URL = 'https://github.com/microsoft/aibast-agents-library.git'
    $env:BRAINSTEM_REPO_REF = 'installers'
    $env:BRAINSTEM_VERSION_URL = 'https://raw.githubusercontent.com/microsoft/aibast-agents-library/c60521e2cacbcbfa585a118c1275093d7bb15b74/rapp_brainstem/VERSION'
    $env:BRAINSTEM_HOME = $BrainstemHome

    $PowerShellExe = [Diagnostics.Process]::GetCurrentProcess().MainModule.FileName
    $MutationStarted = $true
    & $PowerShellExe -NoProfile -ExecutionPolicy Bypass -File $InstallerPath `
        '--no-launch' '--version' 'installers'
    if ($LASTEXITCODE -ne 0) {
        Fail "upstream installer exited with code $LASTEXITCODE"
    }

    $BrainstemPython = Join-Path $BrainstemHome 'venv/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $BrainstemPython -PathType Leaf)) {
        Fail 'the installed RAPP Brainstem Python is missing'
    }

    & $BrainstemPython (Join-Path $PluginRoot 'rapp_operator/rappctl.py') `
        'reconcile' '--actor' $Actor '--envelope' $EnvelopePath `
        '--envelope-sha256' $EnvelopeSha256
    if ($LASTEXITCODE -ne 0) {
        Fail "bootstrap reconciliation exited with code $LASTEXITCODE"
    }
    $BootstrapSucceeded = $true
    Write-Host 'RAPP Brainstem installed and reconciled. Live /chat verification is still required.'
} finally {
    $lockFailure = $null
    try {
        Release-BootstrapLock $BootstrapLock
    } catch {
        $BootstrapSucceeded = $false
        $lockFailure = $_
    }
    if ($EnvelopeTemporary -and (Test-Path -LiteralPath $EnvelopeTemporary)) {
        Remove-Item -LiteralPath $EnvelopeTemporary -Force -ErrorAction SilentlyContinue
    }
    if ($InstallerPath -and (Test-Path -LiteralPath $InstallerPath)) {
        Remove-Item -LiteralPath $InstallerPath -Force -ErrorAction SilentlyContinue
    }
    if ($WorkDirectory -and (Test-Path -LiteralPath $WorkDirectory)) {
        Remove-Item -LiteralPath $WorkDirectory -Recurse -Force -ErrorAction SilentlyContinue
    }
    if (
        -not $BootstrapSucceeded -and
        $MutationStarted -and
        (Test-Path -LiteralPath $BrainstemHome)
    ) {
        $suffix = if ($EnvelopeSha256) { $EnvelopeSha256 } else { 'no-envelope' }
        $quarantine = Join-Path $FailedDirectory "$FailureId-$suffix"
        try {
            Move-Item -LiteralPath $BrainstemHome -Destination $quarantine -ErrorAction Stop
            Write-Warning "RAPP Brainstem partial bootstrap quarantined at $quarantine"
        } catch {
            Remove-Item -LiteralPath $BrainstemHome -Recurse -Force -ErrorAction SilentlyContinue
            if (Test-Path -LiteralPath $BrainstemHome) {
                Write-Error 'RAPP Brainstem bootstrap recovery could not restore the absent state'
            }
        }
    }
    if ($lockFailure) {
        throw $lockFailure
    }
}
