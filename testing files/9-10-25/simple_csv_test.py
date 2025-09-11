import os
import glob

def test_csv_access():
    # Try different path formats
    paths_to_test = [
        r"\\\\192.168.2.19\\ai_team\\AI Program\\Outputs\\PICompiled",
        r"//192.168.2.19/ai_team/AI Program/Outputs/PICompiled",
        r"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled"
    ]
    
    for path in paths_to_test:
        print(f"\nTrying path: {path}")
        try:
            # Check if path exists
            if not os.path.exists(path):
                print(f"✗ Path does not exist: {path}")
                continue
                
            print(f"✓ Path exists: {path}")
            
            # Try to list files
            try:
                files = os.listdir(path)
                print(f"✓ Successfully listed directory contents. Found {len(files)} items.")
                if files:
                    print("\nFirst 5 files/directories:")
                    for f in files[:5]:
                        full_path = os.path.join(path, f)
                        try:
                            size = os.path.getsize(full_path)
                            print(f"  - {f} ({size} bytes)")
                        except:
                            print(f"  - {f} (size unknown)")
                return True
                
            except Exception as e:
                print(f"✗ Error listing directory contents: {e}")
                
        except Exception as e:
            print(f"✗ Error accessing path: {e}")
    
    print("\nAll path access attempts failed. Please check:")
    print("1. Network connectivity to 192.168.2.19")
    print("2. File share permissions")
    print("3. If the path is correct")
    return False

if __name__ == "__main__":
    test_csv_access()
