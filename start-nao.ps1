$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process pythonw -ArgumentList @((Join-Path $root 'app\nao_companion.py')) -WorkingDirectory $root
