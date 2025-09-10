import os
import sys

def test_csv_access():
    print("Testing CSV file access...")
    
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
    # First, run the test and capture output
    import io
    from contextlib import redirect_stdout
    
    output_file = 'csv_test_output.txt'
    
    # Capture the output
    f = io.StringIO()
    with redirect_stdout(f):
        test_csv_access()
    
    # Get the output as a string
    output = f.getvalue()
    
    # Write to file
    try:
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"CSV access test complete. Check {output_file} for results.")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")
    
    # Print to console
    print("\n=== Test Results ===")
    print(output)
