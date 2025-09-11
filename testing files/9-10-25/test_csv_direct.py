import os

def main():
    print("Testing CSV File Access")
    print("=====================")
    
    # Test different path formats
    test_paths = [
        r"\\\\192.168.2.19\\ai_team\\AI Program\\Outputs\\PICompiled",
        r"//192.168.2.19/ai_team/AI Program/Outputs/PICompiled",
        r"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled"
    ]
    
    for path in test_paths:
        print(f"\nTesting path: {path}")
        try:
            # Check if path exists
            exists = os.path.exists(path)
            print(f"Path exists: {exists}")
            
            if exists:
                # Try to list directory contents
                try:
                    files = os.listdir(path)
                    print(f"Directory listing successful. Found {len(files)} items.")
                    if files:
                        print("First 5 items:")
                        for f in files[:5]:
                            print(f"  - {f}")
                    return  # Success
                        
                except Exception as e:
                    print(f"Error listing directory: {e}")
                    print(f"Error type: {type(e).__name__}")
            
        except Exception as e:
            print(f"Error accessing path: {e}")
            print(f"Error type: {type(e).__name__}")
    
    print("\nAll path access attempts failed.")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
