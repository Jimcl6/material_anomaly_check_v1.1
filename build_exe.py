#!/usr/bin/env python3
"""
Build script for Material Anomaly Detection System
Creates a standalone executable using PyInstaller
"""

import subprocess
import sys
import os
import shutil

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("Material Anomaly Detection System - EXE Builder")
    print("=" * 60)
    
    # Check if we're on a UNC path
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    if current_dir.startswith('\\\\'):
        print("\n⚠️  WARNING: Running from UNC network path!")
        print("PyInstaller doesn't support UNC paths. Copying files to local temp directory...")
        
        # Create temp directory on local drive
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix="material_anomaly_")
        print(f"Temp directory: {temp_dir}")
        
        # Copy all Python files to temp directory
        python_files = [
            "main.py", "frame.py", "csb_data_output.py", 
            "rod_blk_output.py", "em_material.py", "df_blk_output.py"
        ]
        
        for file in python_files:
            if os.path.exists(file):
                shutil.copy2(file, temp_dir)
                print(f"✓ Copied {file}")
        
        # Change to temp directory
        original_dir = current_dir
        os.chdir(temp_dir)
        print(f"✓ Changed to temp directory: {temp_dir}")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Install required packages
    packages = [
        "pyinstaller",
        "pandas",
        "openpyxl", 
        "sqlalchemy",
        "mysql-connector-python",
        "watchdog"
    ]
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"Failed to install {package}. Continuing anyway...")
    
    # Clean previous builds
    print("\nCleaning previous builds...")
    for folder in ["build", "dist", "__pycache__"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"✓ Removed {folder}")
    
    # Build executable with Windows-compatible paths
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed", 
        "--name", "MaterialAnomalyDetector",
        "--add-data", "frame.py;.",
        "--add-data", "csb_data_output.py;.",
        "--add-data", "rod_blk_output.py;.",
        "--add-data", "em_material.py;.",
        "--add-data", "df_blk_output.py;.",
        "--hidden-import", "pandas",
        "--hidden-import", "openpyxl",
        "--hidden-import", "sqlalchemy",
        "--hidden-import", "mysql.connector",
        "--hidden-import", "watchdog",
        "--exclude-module", "PyQt5",
        "--exclude-module", "PyQt6",
        "--exclude-module", "PySide2",
        "--exclude-module", "PySide6",
        "--exclude-module", "matplotlib",
        "--exclude-module", "scipy",
        "--exclude-module", "IPython",
        "--exclude-module", "jupyter",
        "--exclude-module", "notebook",
        "--exclude-module", "pygame",
        "main.py"
    ]
    
    cmd_str = " ".join(pyinstaller_cmd)
    
    if run_command(cmd_str, "Building executable with PyInstaller"):
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)
        
        exe_path = os.path.abspath("dist/MaterialAnomalyDetector.exe")
        print(f"Executable created: {exe_path}")
        
        # If we used temp directory, copy back to original location
        if current_dir.startswith('\\\\'):
            try:
                original_dist = os.path.join(original_dir, "dist")
                if not os.path.exists(original_dist):
                    os.makedirs(original_dist)
                
                original_exe = os.path.join(original_dist, "MaterialAnomalyDetector.exe")
                shutil.copy2(exe_path, original_exe)
                print(f"✓ Copied executable back to: {original_exe}")
                
                # Clean up temp directory
                os.chdir(original_dir)
                shutil.rmtree(temp_dir)
                print(f"✓ Cleaned up temp directory")
                
                print(f"\nFinal executable location: {original_exe}")
            except Exception as e:
                print(f"⚠️  Could not copy back to network location: {e}")
                print(f"Executable remains at: {exe_path}")
        
        print("\nYou can now run the application by double-clicking the executable!")
    else:
        print("\n" + "=" * 60)
        print("BUILD FAILED!")
        print("=" * 60)
        print("Please check the error messages above.")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
