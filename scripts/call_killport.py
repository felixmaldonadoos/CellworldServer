import subprocess
import os

def run_powershell_script_as_admin(script_path):
    # Construct the command to run the PowerShell script as administrator
    command = f'powershell.exe -Command "Start-Process powershell -ArgumentList \'-ExecutionPolicy Bypass -File {script_path}\' -Verb RunAs -Wait"'

    try:
        # Run the PowerShell script and capture output
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Capture stdout and stderr
        stdout, stderr = process.communicate()

        # Wait for the process to complete
        process.wait()

        # Output results
        if stdout:
            print("Standard Output:\n", stdout)
        if stderr:
            print("Error Output:\n", stderr)

        print(f"Execution of {script_path} completed.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to run the script. Error: {e}")

if __name__ == "__main__":
    # Path to your PowerShell script
    script_path = os.path.abspath(r".\run_killport_asadmin.ps1")
    
    run_powershell_script_as_admin(script_path)
