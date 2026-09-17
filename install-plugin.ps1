$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $root 'plugins\nao-companion'
$destination = Join-Path $HOME 'plugins\nao-companion'
New-Item -ItemType Directory -Force (Split-Path -Parent $destination) | Out-Null
if (Test-Path $destination) { Remove-Item -LiteralPath $destination -Recurse -Force }
Copy-Item -LiteralPath $source -Destination $destination -Recurse
& codex plugin add 'nao-companion@personal'
if ($LASTEXITCODE -ne 0) { throw "Codex 插件安装失败，退出码：$LASTEXITCODE" }
Write-Host '奈绪助手 Codex 插件已安装。请在新的 Codex 任务中使用。'
