@echo off
echo Testing Python execution...

:: Check Python version
python --version > python_version.txt 2>&1

echo Python version check complete. Check python_version.txt for results.
pause
