@echo off
echo Building Material Anomaly Detection System executable...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

REM Build executable using PyInstaller
echo Building executable...
pyinstaller material_anomaly.spec

REM Check if build was successful
if exist "dist\MaterialAnomalyDetector.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo Executable created: dist\MaterialAnomalyDetector.exe
    echo.
    echo You can now run the application by double-clicking:
    echo %CD%\dist\MaterialAnomalyDetector.exe
    echo.
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Please check the error messages above.
    echo.
)

pause
