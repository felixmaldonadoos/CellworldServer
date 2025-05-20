powershell.exe -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -Command & { .\killport.ps1; Write-Host \"Press Enter to close...\"; Read-Host }' -Verb RunAs"
