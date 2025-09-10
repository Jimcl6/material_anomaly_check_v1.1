def main():
    # Create a test file
    with open('test_file.txt', 'w') as f:
        f.write('This is a test file.')
    
    # Read the test file
    with open('test_file.txt', 'r') as f:
        content = f.read()
    
    print(f"Successfully wrote and read test file. Content: {content}")
    print("Python is working correctly.")

if __name__ == "__main__":
    main()
