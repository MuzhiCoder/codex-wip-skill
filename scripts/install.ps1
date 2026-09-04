param(
    [string]$Source = (Split-Path -Parent $PSScriptRoot)
)

$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$DestRoot = Join-Path $CodexHome "skills"
$Dest = Join-Path $DestRoot "wip"

if (Test-Path $Dest) {
    Write-Error "Destination already exists: $Dest`nRemove/rename it manually or review and update it explicitly."
    exit 2
}

New-Item -ItemType Directory -Force -Path $DestRoot | Out-Null
Copy-Item -Recurse -Path $Source -Destination $Dest
Write-Host "Installed WIP skill to: $Dest"
Write-Host 'Invoke it in Codex with: $wip status'
