@echo off
echo Starting diagnostic... > diagnostic.log
echo %DATE% %TIME% >> diagnostic.log
echo. >> diagnostic.log

:: Check Python version
echo Checking Python version...
python --version >> diagnostic.log 2>&1
echo. >> diagnostic.log

:: Run a simple Python command
echo Running simple Python command...
python -c "import sys; print('Python path:', sys.executable)" >> diagnostic.log 2>&1
echo. >> diagnostic.log

:: Test file access
echo Testing file access... >> diagnostic.log
if exist "\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled" (
    echo Directory exists >> diagnostic.log
    dir "\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled\*.csv" /b >> diagnostic.log
) else (
    echo Directory does not exist or is not accessible >> diagnostic.log
)
echo. >> diagnostic.log

:: Test database connectivity
echo Testing database connectivity... >> diagnostic.log
python -c "import mysql.connector; print('MySQL Connector version:', mysql.connector.__version__)" >> diagnostic.log 2>&1
echo. >> diagnostic.log

echo Diagnostic complete. Check diagnostic.log for results.
pause
