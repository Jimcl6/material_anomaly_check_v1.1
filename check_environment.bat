@echo off
echo Checking Python environment...
echo =============================

:: Check Python version
echo Python Version:
python --version

:: Check Python path
echo.
echo Python Path:
where python

:: Check directory listing
echo.
echo Directory Listing:
dir /b

:: Check network share access
echo.
echo Checking network share access...
if exist "\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled" (
    echo Network share is accessible
    echo.
    echo First 5 files in PICompiled:
    dir /b "\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled\*.*" | findstr /n "^" | findstr /b "[1-5]:"
) else (
    echo Cannot access network share
)

echo.
pause
