import sys
import os
import platform

def write_to_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

def main():
    output = []
    
    # Basic system info
    output.append("=== System Information ===")
    output.append(f"Platform: {platform.platform()}")
    output.append(f"Python Version: {sys.version}")
    output.append(f"Python Executable: {sys.executable}")
    output.append(f"Current Directory: {os.getcwd()}")
    
    # Environment variables
    output.append("\n=== Environment Variables ===")
    for var in ['PATH', 'PYTHONPATH', 'PYTHONHOME']:
        output.append(f"{var}: {os.environ.get(var, 'Not set')}")
    
    # Installed packages
    output.append("\n=== Installed Packages ===")
    try:
        import pkg_resources
        installed_packages = [d for d in pkg_resources.working_set]
        for pkg in installed_packages:
            output.append(f"{pkg.key}: {pkg.version}")
    except Exception as e:
        output.append(f"Error getting installed packages: {e}")
    
    # File system access
    output.append("\n=== File System Access ===")
    test_path = r"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled"
    output.append(f"Testing access to: {test_path}")
    try:
        exists = os.path.exists(test_path)
        output.append(f"Path exists: {exists}")
        if exists:
            files = os.listdir(test_path)
            output.append(f"Number of files: {len(files)}")
            if files:
                output.append("First 5 files:")
                for f in files[:5]:
                    output.append(f"  - {f}")
    except Exception as e:
        output.append(f"Error accessing path: {e}")
    
    # Database connection test
    output.append("\n=== Database Connection Test ===")
    try:
        import mysql.connector
        output.append("mysql.connector is installed")
        try:
            conn = mysql.connector.connect(
                host='192.168.2.148',
                user='hpi.python',
                password='hpi.python',
                database='fc_1_data_db',
                connection_timeout=5
            )
            output.append("✓ Successfully connected to database")
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE(), USER(), VERSION()")
            db_info = cursor.fetchone()
            output.append(f"  - Database: {db_info[0]}")
            output.append(f"  - User: {db_info[1]}")
            output.append(f"  - MySQL Version: {db_info[2]}")
            cursor.close()
            conn.close()
        except Exception as e:
            output.append(f"✗ Database connection failed: {e}")
    except ImportError:
        output.append("mysql.connector is not installed")
    
    # Write all output to file
    output_str = "\n".join(output)
    output_file = "environment_check.txt"
    write_to_file(output_file, output_str)
    print(f"Environment check complete. Results saved to {output_file}")

if __name__ == "__main__":
    main()
