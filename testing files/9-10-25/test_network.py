import os
import sys
import platform
import subprocess
import socket

def test_ping(host):
    """Test ping to a host"""
    print(f"\nTesting ping to {host}...")
    
    # Ping parameters as function of OS
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    count = '4'  # Number of packets
    
    # Building the command
    command = ['ping', param, count, host]
    
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
        print(f"✓ Ping successful to {host}")
        print(output)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Ping failed to {host}")
        print(f"Error: {e.output}")
        return False

def test_port(host, port, timeout=5):
    """Test if a port is open on a host"""
    print(f"\nTesting connection to {host}:{port}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        
        if result == 0:
            print(f"✓ Port {port} is open on {host}")
            return True
        else:
            print(f"✗ Port {port} is closed or blocked on {host} (Error: {result})")
            return False
    except Exception as e:
        print(f"✗ Error testing port {port} on {host}: {e}")
        return False
    finally:
        if 'sock' in locals():
            sock.close()

def test_network_resources():
    """Test network resources including database server and file share"""
    print("Network Diagnostic Tool")
    print("======================")
    
    # Test database server connectivity
    db_host = '192.168.2.148'
    db_port = 3306
    
    print(f"\nTesting connectivity to database server: {db_host}")
    print("-" * 50)
    
    # Test ping to database server
    ping_result = test_ping(db_host)
    
    # Test database port
    port_result = test_port(db_host, db_port)
    
    # Test file share connectivity
    print("\nTesting file share connectivity...")
    print("-" * 50)
    
    share_path = r"\\192.168.2.19\ai_team"
    print(f"Attempting to access: {share_path}")
    
    try:
        if os.path.exists(share_path):
            print(f"✓ Successfully accessed: {share_path}")
            
            # Try to list contents
            try:
                contents = os.listdir(share_path)
                print(f"✓ Successfully listed directory contents. Found {len(contents)} items.")
                if contents:
                    print("\nFirst 5 items:")
                    for item in contents[:5]:
                        print(f"  - {item}")
            except Exception as e:
                print(f"✗ Error listing directory contents: {e}")
        else:
            print(f"✗ Could not access: {share_path}")
            print("Please check:")
            print("1. Network connectivity to 192.168.2.19")
            print("2. File share permissions")
            print("3. If the path is correct")
    except Exception as e:
        print(f"✗ Error accessing file share: {e}")

if __name__ == "__main__":
    test_network_resources()
    
    print("\nDiagnostic complete. Review the output above for any issues.")
    
    # Keep the window open if run directly
    if platform.system().lower() == 'windows':
        input("\nPress Enter to exit...")
