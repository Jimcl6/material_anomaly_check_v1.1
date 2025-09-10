print("Searching for CSV files...\n")

# Try to list the AI Program directory first
path = r"\\\\192.168.2.19\\ai_team\\AI Program"
print(f"Checking: {path}")

try:
    if os.path.exists(path):
        print("✓ Path exists")
        items = os.listdir(path)
        print(f"Found {len(items)} items in this directory")
        print("First 10 items:")
        for item in items[:10]:
            print(f"- {item}")
    else:
        print("✗ Path does not exist or is not accessible")
except Exception as e:
    print(f"Error: {e}")

print("\nSearch complete.")
input("\nPress Enter to exit...")
