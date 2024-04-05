#!/bin/bash
# Check if the "venv" directory exists in the current working directory
if [ -d "venvCWU" ]; then
  # The virtual environment directory exists, activate it
  echo "Activating virtual environment..."
  source venvCWU/bin/activate
else
  # The virtual environment directory does not exist, display an error message
  echo "Error: virtual environment directory 'venvCW' not found."
fi

