[CmdletBinding()]
param(
  [switch]$Gui,
  [string]$Module = 'src',   # 実行したいモジュール名 (例: src, mypkg, mypkg.cli など)
  [Parameter(ValueFromRemainingArguments=$true)]
  [String[]]$PassThruArgs
)

$ErrorActionPreference = 'Stop'

# repo root = parent of this script folder
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$venv = Join-Path $repoRoot '.venv'
$py  = Join-Path $venv 'Scripts\python.exe'
$pyw = Join-Path $venv 'Scripts\pythonw.exe'

if (!(Test-Path $py)) { throw 'venv not found. Run setup.cmd first.' }

# choose interpreter (python / pythonw)
$exe = $py
if ($Gui) { $exe = $pyw }

# 実行は repoRoot に移動して行う（これで python -m <module> が src を見つけられる）
Push-Location $repoRoot
try {
    if ($PassThruArgs -and $PassThruArgs.Count -gt 0) {
        & $exe -m $Module @PassThruArgs
    } else {
        & $exe -m $Module
    }
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}

if ($code -ne 0 -and -not $env:CI) { Read-Host 'Press Enter' }
exit $code
