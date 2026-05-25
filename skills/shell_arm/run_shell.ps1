param([string]$cmd)
Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
