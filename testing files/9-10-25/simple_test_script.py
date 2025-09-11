import sys
import os

def main():
    print("Simple Test Script")
    print("=================")
    
    # Basic info
    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Test file writing
    test_file = 'test_output_python.txt'
    try:
        with open(test_file, 'w') as f:
            f.write('Test content from Python script')
        print(f"✓ Successfully wrote to {test_file}")
    except Exception as e:
        print(f"✗ Error writing to file: {e}")
    
    # List directory contents
    try:
        print("\nCurrent directory contents:")
        for item in os.listdir('.'):
            print(f"- {item}")
    except Exception as e:
        print(f"Error listing directory: {e}")

if __name__ == "__main__":
    main()
