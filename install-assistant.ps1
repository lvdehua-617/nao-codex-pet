$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$startup = [Environment]::GetFolderPath('Startup')
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut((Join-Path $startup '奈绪助手.lnk'))
$shortcut.TargetPath = (Get-Command pythonw).Source
$shortcut.Arguments = '"' + (Join-Path $root 'app\nao_companion.py') + '"'
$shortcut.WorkingDirectory = $root
$shortcut.Save()
Write-Host '奈绪助手已加入 Windows 启动项。'
& (Join-Path $root 'start-nao.ps1')
