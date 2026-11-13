# init.ps1: set up a fresh clone on Windows (PowerShell 5.1 or 7). Safe to re-run.
#   1. fetch the git submodules (the 3d-print-design skill) at the commit this repo pins
#   2. create the Python environment: `uv sync` (.venv at the repo root), or without uv
#      `pipeline.py setup` (a pip venv inside the 3d-print-design submodule)
# On macOS, Linux or Git Bash use init.sh instead.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

$Submodule = '.claude/skills/3d-print-design'
$Pipeline = '.claude/skills/3d-design-pipeline/scripts/pipeline.py'

function Invoke-Native {
    param([string]$Exe, [string[]]$Arguments)
    Write-Host "$ $Exe $($Arguments -join ' ')"
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "'$Exe $($Arguments -join ' ')' failed with exit code $LASTEXITCODE" }
}

Write-Host '== git submodules'
Invoke-Native git @('submodule', 'sync', '--recursive')
Invoke-Native git @('submodule', 'update', '--init', '--recursive')
if (-not (Test-Path -LiteralPath "$Submodule/scripts/cad.py")) {
    throw "$Submodule is still empty after the submodule update"
}

Write-Host '== Python environment'
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Invoke-Native uv @('sync')
    Invoke-Native uv @('run', 'python', '-I', '-c', "import numpy, trimesh, manifold3d, shapely; print('geometry stack ok')")
}
else {
    $py = $null
    foreach ($cand in 'python', 'py') {
        if (Get-Command $cand -ErrorAction SilentlyContinue) { $py = $cand; break }
    }
    if (-not $py) { throw 'neither uv nor Python found; install uv (https://docs.astral.sh/uv/) and re-run' }
    Write-Host 'uv not found: falling back to a pip venv'
    Invoke-Native $py @($Pipeline, 'setup')
}

Write-Host '== done. Try: uv run pipeline materials'
