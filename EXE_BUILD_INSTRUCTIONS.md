# Material Anomaly Detection System - EXE Build Instructions

## Overview
This guide will help you convert your Material Anomaly Detection System into a standalone .exe application using PyInstaller.

## Prerequisites
- Python 3.7+ installed
- All project dependencies available
- Windows operating system

## Files Created for EXE Build

### 1. `requirements.txt`
Contains all necessary Python packages:
- pandas (data processing)
- openpyxl (Excel file handling)
- sqlalchemy (database connections)
- mysql-connector-python (MySQL database access)
- watchdog (file monitoring)
- pyinstaller (executable creation)

### 2. `material_anomaly.spec`
PyInstaller configuration file with:
- All module dependencies included
- Material processing scripts bundled
- GUI settings optimized
- Hidden imports specified

### 3. Build Scripts
- `build_exe.bat` - Full build with dependency installation
- `build_exe_simple.bat` - Quick build option

## Build Instructions

### Option 1: Full Build (Recommended)
1. Open Command Prompt as Administrator
2. Navigate to your project directory:
   ```
   cd "\\192.168.2.19\ai_team\INDIVIDUAL FOLDER\Jed-san\JHUN DEVIATION\jed_material_anomaly_check"
   ```
3. Run the build script:
   ```
   build_exe.bat
   ```

### Option 2: Simple Build
1. Open Command Prompt
2. Navigate to project directory
3. Run:
   ```
   build_exe_simple.bat
   ```

### Option 3: Manual Build
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Build using spec file:
   ```
   pyinstaller material_anomaly.spec
   ```

## Output
- Executable will be created in `dist\MaterialAnomalyDetector.exe`
- File size: ~50-100MB (includes all dependencies)
- No Python installation required on target machines

## Important Notes

### Database Connectivity
- Ensure target machines can access database server (192.168.2.148)
- Network paths must be accessible from target machines
- Database credentials are embedded in the executable

### File Paths
- CSV monitoring paths are hardcoded to network locations
- Ensure network drives are mapped on target machines
- Output files will be saved to user's Desktop

### Dependencies Included
- Complete Python runtime
- All required packages (pandas, tkinter, etc.)
- Material processing modules
- Database connectors

## Troubleshooting

### Common Issues
1. **Build fails**: Check Python installation and PATH
2. **Missing modules**: Verify all imports in requirements.txt
3. **Large file size**: Normal for bundled applications
4. **Slow startup**: First run may take longer due to extraction

### Testing the Executable
1. Copy `MaterialAnomalyDetector.exe` to a clean machine
2. Ensure network access to database and file paths
3. Test all functionality:
   - Data refresh
   - Material selection
   - CSV monitoring
   - Excel export

## Distribution
- Single file executable: `MaterialAnomalyDetector.exe`
- No installation required
- Can be distributed via network share or USB
- Approximately 50-100MB file size

## Security Considerations
- Database credentials are embedded in executable
- Consider using environment variables for sensitive data
- Executable contains full source code (compiled)
