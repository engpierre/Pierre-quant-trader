$path = "C:\Users\Pierre\.openclaw\workspace\pierre-quant"
$file = "commander.txt"
$lastCommand = ""

Write-Host "Watcher Active. Monitoring $file for commands..." -ForegroundColor Green

while ($true) {
    if (Test-Path "$path\$file") {
        $currentCommand = Get-Content "$path\$file" -Raw
        if ($currentCommand -ne $lastCommand -and -not [string]::IsNullOrWhiteSpace($currentCommand)) {
            Write-Host "Executing: $currentCommand" -ForegroundColor Yellow
            try {
                Invoke-Expression $currentCommand
                $lastCommand = ""  # Reset last command since file is cleared
                Clear-Content "$path\$file"
            } catch {
                Write-Error "Execution Failed: $_"
                $lastCommand = ""  # Reset even on failure so file clears cleanly
                Clear-Content "$path\$file"
            }
        }
    }
    Start-Sleep -Seconds 1
}
