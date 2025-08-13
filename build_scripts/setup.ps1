[CmdletBinding()]
param(
  [switch]$Recreate,
  [string]$Requirements,
  [string]$Constraints
)

$ErrorActionPreference = 'Stop'

# ← ここが肝：ps1 の 1 つ上を「リポジトリルート」とみなす
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $repoRoot

# requirements.txt の場所を決定（引数 > ルート > build_scripts の順に探索）
if ($Requirements) {
  $req = (Resolve-Path $Requirements).Path
} else {
  $candidates = @(
    (Join-Path $repoRoot 'requirements.txt'),
    (Join-Path $PSScriptRoot 'requirements.txt')
  )
  $req = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
  if (-not $req) { throw "requirements.txt が見つかりません。探索: `n- $($candidates -join "`n- ")" }
}

# venv はルート直下
$venv = Join-Path $repoRoot '.venv'
if ($Recreate -and (Test-Path $venv)) { Remove-Item $venv -Recurse -Force }
if (!(Test-Path $venv)) { & python -m venv $venv }

$py = Join-Path $venv 'Scripts\python.exe'
& $py -m pip install -U pip wheel

# constraints の指定があれば使用、なければルートの constraints.txt を自動検出
if ($Constraints) {
  $con = (Resolve-Path $Constraints).Path
  & $py -m pip install -r $req -c $con
} elseif (Test-Path (Join-Path $repoRoot 'constraints.txt')) {
  & $py -m pip install -r $req -c (Join-Path $repoRoot 'constraints.txt')
} else {
  & $py -m pip install -r $req
}

Write-Host "Setup OK. repoRoot = $repoRoot"
