import sys
import os
import platform

def main():
    with open('environment_check.txt', 'w') as f:
        # Basic Python info
        f.write("=== Python Environment ===\n")
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Executable: {sys.executable}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write(f"Current Directory: {os.getcwd()}\n\n")
        
        # Installed packages
        f.write("=== Installed Packages ===\n")
        try:
            import pkg_resources
            installed_packages = [d for d in pkg_resources.working_set]
            for pkg in installed_packages:
                f.write(f"{pkg.key}: {pkg.version}\n")
        except Exception as e:
            f.write(f"Error getting installed packages: {e}\n")
        
        # File system access
        f.write("\n=== File System Access ===\n")
        test_path = r"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled"
        f.write(f"Testing access to: {test_path}\n")
        try:
            exists = os.path.exists(test_path)
            f.write(f"Path exists: {exists}\n")
            if exists:
                files = os.listdir(test_path)
                f.write(f"Number of files: {len(files)}\n")
                if files:
                    f.write("First 5 files:\n")
                    for filename in files[:5]:
                        f.write(f"  - {filename}\n")
        except Exception as e:
            f.write(f"Error accessing path: {e}\n")
        
        # Database connection test
        f.write("\n=== Database Connection Test ===\n")
        try:
            import mysql.connector
            f.write("mysql.connector is installed\n")
            try:
                conn = mysql.connector.connect(
                    host='192.168.2.148',
                    user='hpi.python',
                    password='hpi.python',
                    database='fc_1_data_db',
                    connection_timeout=5
                )
                f.write("✓ Successfully connected to database\n")
                cursor = conn.cursor()
                cursor.execute("SELECT DATABASE(), USER(), VERSION()")
                db_info = cursor.fetchone()
                f.write(f"  - Database: {db_info[0]}\n")
                f.write(f"  - User: {db_info[1]}\n")
                f.write(f"  - MySQL Version: {db_info[2]}\n")
                cursor.close()
                conn.close()
            except Exception as e:
                f.write(f"✗ Database connection failed: {e}\n")
        except ImportError:
            f.write("✗ mysql.connector is not installed\n")
    
    print("Environment check complete. Results saved to environment_check.txt")

if __name__ == "__main__":
    main()
