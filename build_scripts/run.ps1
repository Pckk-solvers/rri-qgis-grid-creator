[CmdletBinding()]
param(
  [switch]$Gui,
  [string]$Module
)

$ErrorActionPreference = 'Stop'

# repo root = parent of this script folder
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$venv = Join-Path $repoRoot '.venv'
$py  = Join-Path $venv 'Scripts\python.exe'
$pyw = Join-Path $venv 'Scripts\pythonw.exe'

if (-not (Test-Path $py))  { throw "venv not found: $py. Run setup first." }
if ($Gui -and -not (Test-Path $pyw)) { throw "pythonw.exe not found: $pyw" }

# default module
if ([string]::IsNullOrWhiteSpace($Module)) {
    $Module = if ($Gui) { 'src.full_pipline_gui' } else { 'src' }
}

$exe = if ($Gui) { $pyw } else { $py }
$PassThruArgs = $args  # PS5.1/7 共通

Push-Location $repoRoot
try {
    if ($PassThruArgs -and $PassThruArgs.Count -gt 0) {
        & $exe -m $Module @PassThruArgs
    } else {
        & $exe -m $Module
    }
    $code = $LASTEXITCODE
}
finally { Pop-Location }

if ($code -ne 0 -and -not $env:CI) { Read-Host 'Press Enter' }
exit $code
