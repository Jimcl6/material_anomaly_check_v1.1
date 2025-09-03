#!/usr/bin/env python3
"""
Enhanced build script for Material Anomaly Detection System
Creates a standalone executable using PyInstaller with all dependencies
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and print output in real-time"""
    print(f"\nRunning: {cmd}")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        shell=True,
        cwd=cwd
    )
    
    # Print output in real-time
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    
    return process.poll()

def main():
    print("=" * 60)
    print("Material Anomaly Detection System - Enhanced EXE Builder")
    print("=" * 60)
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()
    print(f"Script directory: {script_dir}")
    
    # Create a temporary build directory
    with tempfile.TemporaryDirectory(prefix="material_anomaly_") as temp_dir:
        print(f"\nCreated temporary build directory: {temp_dir}")
        
        # Copy all necessary files to the temp directory
        print("\nCopying project files...")
        for item in script_dir.glob('*'):
            if item.name not in ['build', 'dist', '__pycache__', '.git', '.idea', '*.spec']:
                dest = os.path.join(temp_dir, item.name)
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
        
        # Install required packages
        print("\nInstalling dependencies...")
        requirements = script_dir / 'requirements.txt'
        if requirements.exists():
            run_command(f"pip install -r {requirements}", cwd=temp_dir)
        
        # Build the executable
        print("\nBuilding executable...")
        pyinstaller_cmd = (
            f'pyinstaller --noconfirm --onefile --windowed '  # --windowed for no console
            f'--name "MaterialAnomalyDetector" '
            f'--icon="{script_dir}/icon.ico" '
            f'--add-data "{script_dir}/*.py;." '
            f'--add-data "{script_dir}/*.xlsx;." '
            f'--hidden-import=tkinter '
            f'--hidden-import=pandas '
            f'--hidden-import=openpyxl '
            f'--hidden-import=mysql.connector '
            f'--hidden-import=sqlalchemy '
            f'--hidden-import=matplotlib '
            f'--hidden-import=PIL '
            f'--hidden-import=mysql.connector.plugins.caching_sha2_password '
            f'--hidden-import=mysql.connector.plugins.mysql_native_password '
            f'--hidden-import=frame '
            f'--hidden-import=csb_data_output '
            f'--hidden-import=rod_blk_output '
            f'--hidden-import=em_material '
            f'--hidden-import=df_blk_output '
            f'--hidden-import=check_table_schemas '
            f'main.py'
        )
        
        if run_command(pyinstaller_cmd, cwd=temp_dir) != 0:
            print("\n❌ Build failed!")
            return 1
        
        # Copy the built executable back to the source directory
        exe_src = os.path.join(temp_dir, 'dist', 'MaterialAnomalyDetector.exe')
        exe_dest = os.path.join(script_dir, 'MaterialAnomalyDetector.exe')
        
        if os.path.exists(exe_src):
            shutil.copy2(exe_src, exe_dest)
            print(f"\n✅ Build successful!")
            print(f"Executable created at: {exe_dest}")
            return 0
        else:
            print("\n❌ Build failed - executable not found!")
            return 1

if __name__ == "__main__":
    sys.exit(main())
