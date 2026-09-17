$ErrorActionPreference = "Stop"

$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$sourceDir = Join-Path $PSScriptRoot "pet"
$targetDir = Join-Path $codexRoot "pets\nao"

if (-not (Test-Path -LiteralPath (Join-Path $sourceDir "pet.json"))) {
    throw "pet/pet.json is missing."
}

if (-not (Test-Path -LiteralPath (Join-Path $sourceDir "spritesheet.webp"))) {
    throw "pet/spritesheet.webp is missing."
}

New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
Copy-Item -LiteralPath (Join-Path $sourceDir "pet.json") -Destination $targetDir -Force
Copy-Item -LiteralPath (Join-Path $sourceDir "spritesheet.webp") -Destination $targetDir -Force

Write-Host "Installed 奈绪 to $targetDir"
Write-Host "Restart Codex, then select 奈绪 from the pet picker."

