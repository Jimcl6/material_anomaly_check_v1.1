@echo off
setlocal enabledelayedexpansion
echo Building Material Anomaly Detection System...

REM Create a temporary local directory
set TEMP_DIR=%TEMP%\material_anomaly_build
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

echo Copying files to temporary directory...
xcopy /E /Y "%~dp0*" "%TEMP_DIR%\" >nul

echo Installing required packages...
cd /d "%TEMP_DIR%"
pip install -r requirements.txt

echo Building executable...
set PYINSTALLER_CMD=pyinstaller --noconfirm --onefile --windowed ^
    --name "MaterialAnomalyDetector" ^
    --icon=icon.ico ^
    --add-data "material_anomaly.log;." ^
    --add-data "*.xlsx;." ^
    --add-data "frame.py;." ^
    --add-data "csb_data_output.py;." ^
    --add-data "rod_blk_output.py;." ^
    --add-data "em_material.py;." ^
    --add-data "df_blk_output.py;." ^
    --add-data "check_table_schemas.py;." ^
    --hidden-import=tkinter ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=mysql.connector ^
    --hidden-import=sqlalchemy ^
    --hidden-import=matplotlib ^
    --hidden-import=PIL ^
    --hidden-import=mysql.connector.plugins.caching_sha2_password ^
    --hidden-import=mysql.connector.plugins.mysql_native_password ^
    --hidden-import=frame ^
    --hidden-import=csb_data_output ^
    --hidden-import=rod_blk_output ^
    --hidden-import=em_material ^
    --hidden-import=df_blk_output ^
    --hidden-import=check_table_schemas ^
    --additional-hooks-dir=.

echo Running: %PYINSTALLER_CMD%
%PYINSTALLER_CMD% main.py

echo Copying output...
if exist "dist\MaterialAnomalyDetector.exe" (
    copy "dist\MaterialAnomalyDetector.exe" "%~dp0" /Y
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo Executable created at: %~dp0MaterialAnomalyDetector.exe
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
)

echo Cleaning up...
cd /d "%~dp0"
timeout /t 3 >nul
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
pause