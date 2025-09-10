import os
import sys
import platform
import socket
import subprocess
from datetime import datetime

def print_section(title):
    print(f"\n{'='*80}")
    print(f"{title.upper()}")
    print(f"{'='*80}")

def get_system_info():
    print_section("System Information")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Version: {platform.version()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Python Executable: {sys.executable}")

def check_network_resources():
    print_section("Network Resources Check")
    
    # Check CSV directory
    csv_dir = r"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled"
    print(f"Checking CSV directory: {csv_dir}")
    try:
        if os.path.exists(csv_dir):
            print("✓ Directory exists")
            files = os.listdir(csv_dir)
            print(f"Found {len(files)} files in directory")
            if files:
                print("First 5 files:")
                for f in files[:5]:
                    print(f"  - {f}")
        else:
            print("✗ Directory does not exist or is not accessible")
    except Exception as e:
        print(f"✗ Error accessing directory: {e}")
    
    # Check database server
    db_host = '192.168.2.148'
    db_port = 3306
    print(f"\nChecking database server: {db_host}:{db_port}")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((db_host, db_port))
        if result == 0:
            print(f"✓ Successfully connected to {db_host}:{db_port}")
        else:
            print(f"✗ Could not connect to {db_host}:{db_port} (Error: {result})")
        sock.close()
    except Exception as e:
        print(f"✗ Error checking database server: {e}")

def check_python_environment():
    print_section("Python Environment")
    try:
        import pandas as pd
        print(f"pandas version: {pd.__version__}")
    except ImportError:
        print("✗ pandas is not installed")
    
    try:
        import mysql.connector
        print(f"mysql-connector-python version: {mysql.connector.__version__}")
    except ImportError:
        print("✗ mysql-connector-python is not installed")
    except Exception as e:
        print(f"✗ Error checking mysql-connector: {e}")
    
    try:
        import sqlalchemy
        print(f"SQLAlchemy version: {sqlalchemy.__version__}")
    except ImportError:
        print("✗ SQLAlchemy is not installed")

def check_script_permissions():
    print_section("Script Permissions")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {script_dir}")
    
    # Check write permissions in script directory
    test_file = os.path.join(script_dir, "test_permission.txt")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✓ Write permission in script directory: Yes")
    except Exception as e:
        print(f"✗ No write permission in script directory: {e}")

def save_diagnostic_report():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"diagnostic_report_{timestamp}.txt"
    
    # Redirect stdout to capture all output
    original_stdout = sys.stdout
    with open(report_file, 'w') as f:
        sys.stdout = f
        run_diagnostics()
        sys.stdout = original_stdout
    
    print(f"\nDiagnostic report saved to: {os.path.abspath(report_file)}")

def run_diagnostics():
    print(f"Diagnostic Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    get_system_info()
    check_network_resources()
    check_python_environment()
    check_script_permissions()
    
    print("\nDiagnostics completed. Please review the information above for any issues.")

if __name__ == "__main__":
    run_diagnostics()
    save_diagnostic = input("\nWould you like to save this diagnostic report to a file? (y/n): ")
    if save_diagnostic.lower() == 'y':
        save_diagnostic_report()
