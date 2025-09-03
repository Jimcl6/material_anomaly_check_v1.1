import pandas as pd
import os

# Test script to verify Excel output functionality
def test_excel_output():
    """Test if the Excel file contains the Frame_Deviations sheet with complete data"""
    
    excel_file = "frame_data_output.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"Excel file '{excel_file}' not found")
        return False
    
    try:
        # Read the Excel file to check its contents
        xl_file = pd.ExcelFile(excel_file)
        sheet_names = xl_file.sheet_names
        
        print(f"Found Excel file with {len(sheet_names)} sheets:")
        for sheet in sheet_names:
            print(f"  - {sheet}")
        
        # Check if Frame_Deviations sheet exists
        if 'Frame_Deviations' in sheet_names:
            print("\n✓ Frame_Deviations sheet found!")
            
            # Read the Frame_Deviations sheet
            deviation_df = pd.read_excel(excel_file, sheet_name='Frame_Deviations')
            print(f"Frame_Deviations sheet contains {len(deviation_df)} rows and {len(deviation_df.columns)} columns")
            print(f"Columns: {list(deviation_df.columns)}")
            
            if len(deviation_df) > 0:
                print("\nSample data from Frame_Deviations sheet:")
                print(deviation_df.head())
                return True
            else:
                print("Frame_Deviations sheet is empty")
                return False
        else:
            print("\n✗ Frame_Deviations sheet not found")
            return False
            
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Excel Output ===")
    success = test_excel_output()
    
    if success:
        print("\n✓ Excel output test PASSED")
    else:
        print("\n✗ Excel output test FAILED")
