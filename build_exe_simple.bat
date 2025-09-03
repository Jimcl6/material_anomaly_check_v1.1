@echo off
echo Building Material Anomaly Detection System executable...
echo.

REM Simple one-file executable build
echo Building single executable file...
pyinstaller --onefile --windowed --name "MaterialAnomalyDetector" --add-data "frame.py;." --add-data "csb_data_output.py;." --add-data "rod_blk_output.py;." --add-data "em_material.py;." --add-data "df_blk_output.py;." main.py

if exist "dist\MaterialAnomalyDetector.exe" (
    echo.
    echo BUILD SUCCESSFUL!
    echo Executable: dist\MaterialAnomalyDetector.exe
) else (
    echo BUILD FAILED!
)

pause
