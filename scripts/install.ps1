param(
    [string]$Source = (Join-Path (Split-Path -Parent $PSScriptRoot) "plugins\codex-wip\skills\wip")
)

$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$DestRoot = Join-Path $CodexHome "skills"
$Dest = Join-Path $DestRoot "wip"

if (-not (Test-Path (Join-Path $Source "SKILL.md"))) {
    Write-Error "WIP skill source not found: $Source"
    exit 2
}

if (Test-Path $Dest) {
    Write-Error "Destination already exists: $Dest`nRemove/rename it manually or review and update it explicitly."
    exit 2
}

New-Item -ItemType Directory -Force -Path $DestRoot | Out-Null
Copy-Item -Recurse -Path $Source -Destination $Dest
Write-Host "Installed WIP skill to: $Dest"
Write-Host 'Invoke it in a new Codex session with: $wip status'
Write-Host 'For native plugin installation, use the marketplace commands documented in README.md.'
