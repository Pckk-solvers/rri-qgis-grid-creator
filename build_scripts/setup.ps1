[CmdletBinding()]
param(
  [switch]$Recreate,              # remove and recreate venv
  [string]$Requirements,          # optional custom path to requirements.txt
  [string]$Constraints            # optional constraints file
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# repo root = parent of this script folder
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $repoRoot

# resolve requirements.txt (arg > repo root > script dir)
function Resolve-FirstExisting([string[]]$paths) {
  foreach ($p in $paths) { if (Test-Path $p) { return (Resolve-Path $p).Path } }
  return $null
}

$req = $null
if ($Requirements) {
  if (!(Test-Path $Requirements)) { throw "requirements not found: $Requirements" }
  $req = (Resolve-Path $Requirements).Path
} else {
  $req = Resolve-FirstExisting @(
    (Join-Path $repoRoot 'requirements.txt'),
    (Join-Path $PSScriptRoot 'requirements.txt')
  )
}

if (-not $req) { throw 'requirements.txt not found.' }

# venv under repo root
$venv = Join-Path $repoRoot '.venv'
if ($Recreate -and (Test-Path $venv)) {
  Remove-Item $venv -Recurse -Force
}
if (!(Test-Path $venv)) {
  # create venv (prefer "python", fallback to launcher "py -3")
  $created = $false
  try {
    & python -m venv $venv
    $created = $true
  } catch {
    $created = $false
  }
  if (-not $created) {
    try {
      & py -3 -m venv $venv
      $created = $true
    } catch {
      $created = $false
    }
  }
  if (-not $created) { throw 'failed to create venv. ensure Python is on PATH.' }
}

$py = Join-Path $venv 'Scripts\python.exe'
if (!(Test-Path $py)) { throw 'venv python not found.' }

# upgrade pip tooling
& $py -m pip install -U pip setuptools wheel

# install requirements (with optional constraints)
if ($Constraints) {
  if (!(Test-Path $Constraints)) { throw "constraints not found: $Constraints" }
  & $py -m pip install -r $req -c (Resolve-Path $Constraints).Path
} elseif (Test-Path (Join-Path $repoRoot 'constraints.txt')) {
  & $py -m pip install -r $req -c (Join-Path $repoRoot 'constraints.txt')
} else {
  & $py -m pip install -r $req
}

Write-Host "setup done. repoRoot=$repoRoot"
