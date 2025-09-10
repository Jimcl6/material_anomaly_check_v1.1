print("Testing different network path formats...\n")

paths_to_test = [
    r"\\\\192.168.2.19\\ai_team\\AI Program\\Outputs\\PICompiled",  # Double backslashes
    r"//192.168.2.19/ai_team/AI Program/Outputs/PICompiled",  # Forward slashes
    r"\\\\192.168.2.19\\ai_team\\AI Program\\Outputs",  # Parent directory
    r"\\\\192.168.2.19\\ai_team",  # Root of ai_team share
]

def test_path(path):
    print(f"Testing path: {path}")
    try:
        import os
        exists = os.path.exists(path)
        print(f"  - Exists: {exists}")
        
        if exists:
            try:
                files = os.listdir(path)
                print(f"  - Contains {len(files)} items")
                if files:
                    print("  - First 5 items:")
                    for item in files[:5]:
                        print(f"    - {item}")
            except Exception as e:
                print(f"  - Error listing directory: {e}")
        
        return exists
    except Exception as e:
        print(f"  - Error: {e}")
        return False

print("\n=== Testing Paths ===")
for path in paths_to_test:
    test_path(path)
    print()

input("\nPress Enter to exit...")
