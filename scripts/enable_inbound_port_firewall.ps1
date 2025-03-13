# Ensure the script runs with administrative privileges
$adminCheck = [System.Security.Principal.WindowsPrincipal] `
    [System.Security.Principal.WindowsIdentity]::GetCurrent()
$adminRole = [System.Security.Principal.WindowsBuiltInRole]::Administrator
if (-not $adminCheck.IsInRole($adminRole)) {
    Write-Host "This script requires administrative privileges. Please run as administrator."
    exit
}

# Enable Windows Firewall if not already enabled
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True

# Define the ports
$ports = @(4790, 4791)

# Loop through each port and create a rule
foreach ($port in $ports) {
    New-NetFirewallRule -DisplayName "Allow Port $port Inbound" `
                        -Direction Inbound `
                        -Action Allow `
                        -Protocol TCP `
                        -LocalPort $port `
                        -Profile Any `
                        -Enabled True
}

Write-Host "Inbound rules for ports 4790 and 4791 have been successfully added to Windows Firewall."
