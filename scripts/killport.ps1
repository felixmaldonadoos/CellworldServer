# KillProcessOnPort.ps1

# Define the port you want to search for
$port = 4791

# Find the process ID using netstat for the specific port
$processId = (netstat -aon | findstr $port) -split '\s+' | Select-Object -Last 1

# If a process ID was found, attempt to kill the process
if ($processId) {
    Write-Host "Process ID $processId found for port $port. Attempting to kill..."
    taskkill /F /PID $processId
} else {
    Write-Host "No process found on port $port."
}
