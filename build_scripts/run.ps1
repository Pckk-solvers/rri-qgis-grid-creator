[CmdletBinding()]
param(
  [switch]$Gui,
  [string]$Entry = 'src\full_pipline_gui.py'
)

$ErrorActionPreference = 'Stop'

# repo root = parent of this script folder
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$venv = Join-Path $repoRoot '.venv'
$py  = Join-Path $venv 'Scripts\python.exe'
$pyw = Join-Path $venv 'Scripts\pythonw.exe'
$main = (Resolve-Path (Join-Path $repoRoot $Entry)).Path

if (!(Test-Path $py)) { throw 'venv not found. Run setup.cmd first.' }

# PowerShell 5.1 has no ternary operator. Use if/else.
$exe = $py
if ($Gui) { $exe = $pyw }

& $exe $main
$code = $LASTEXITCODE
if ($code -ne 0 -and -not $env:CI) { Read-Host 'Press Enter' }
exit $code
