import pandas as pd
import numpy as np
import sys
import os

# Add the current directory to the path so we can import from main.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the new functions from main.py
from main import (
    extract_material_codes_from_inspection_data,
    filter_deviation_data_by_material,
    create_material_sheet_data,
    create_excel_output
)

def create_test_data():
    """Create sample test data to verify the Excel output function"""
    
    # Create sample inspection data
    inspection_data = {
        'Material_Code': ['EM0580106P', 'EM0580107P', 'FM05000102', 'CSB6400802', 'EM0660046P'],
        'Lot_Number': ['CAT-5D24DI', 'CAT-5D24DI', '012625B-40', '042525A', 'FC6030-4F05GT'],
        'Date': ['2025-05-22', '2025-05-22', '2025-01-27', '2025-06-12', '2025-01-15'],
        'Inspection_3_Resistance_Average': [0.91, 0.91, None, None, 1.44],
        'Inspection_4_Dimension_Average': [0.36, 0.34, None, None, None],
        'Inspection_5_Dimension_Average': [0.37, 0.43, None, None, None],
        'Inspection_10_Pull_Test': [1.61, 1.46, None, None, 1.82],
        'Inspection_1_Average': [None, None, 85.42, 29.51, None],
        'Inspection_2_Average': [None, None, 77.95, None, None],
        'Inspection_3_Average': [None, None, 63.71, None, None],
        'Inspection_4_Average': [None, None, 76.83, None, None],
        'Inspection_5_Average': [None, None, 63.67, None, None],
        'Inspection_6_Average': [None, None, 76.86, None, None],
        'Inspection_7_Average': [None, None, 206.31, None, None]
    }
    inspection_df = pd.DataFrame(inspection_data)
    
    # Create sample database data
    database_data = {
        'Process_1_Em2p_Inspection_3_Average_Data': np.random.normal(0.92, 0.05, 50),
        'Process_1_Em2p_Inspection_4_Average_Data': np.random.normal(0.40, 0.05, 50),
        'Process_1_Em2p_Inspection_5_Average_Data': np.random.normal(0.46, 0.05, 50),
        'Process_1_Em2p_Inspection_10_Average_Data': np.random.normal(2.26, 0.2, 50),
        'Process_1_Em3p_Inspection_3_Average_Data': np.random.normal(0.90, 0.05, 50),
        'Process_1_Em3p_Inspection_4_Average_Data': np.random.normal(0.37, 0.05, 50),
        'Process_1_Em3p_Inspection_5_Average_Data': np.random.normal(0.47, 0.05, 50),
        'Process_1_Em3p_Inspection_10_Average_Data': np.random.normal(2.13, 0.2, 50),
        'Process_1_Frame_Inspection_1_Average_Data': np.random.normal(85.41, 1.0, 50),
        'Process_1_Frame_Inspection_2_Average_Data': np.random.normal(77.95, 1.0, 50),
        'Process_1_Frame_Inspection_3_Average_Data': np.random.normal(63.70, 1.0, 50),
        'Process_3_Casing_Block_Inspection_1_Average_Data': np.random.normal(29.52, 0.5, 50),
        'Model_Code': ['60CAT0212P'] * 50,
        'PASS_NG': [1] * 50
    }
    database_df = pd.DataFrame(database_data)
    
    # Create sample deviation data
    deviation_data = []
    
    # Add Em2p (EM0580106P) deviation data
    deviation_data.extend([
        {
            'Column': 'Process_1_Em2p_Inspection_3_Average_Data',
            'Database_Average': 0.92,
            'EM0580106P_Value': 0.91,
            'Inspection_Value': 0.91,
            'Deviation': (0.92 - 0.91) / 0.92,
            'Matched_Inspection_Column': 'Inspection_3_Resistance_Average',
            'Matching_Strategy': 'Direct Type Mapping',
            'Material': 'Em2p',
            'Process_Number': '1',
            'Inspection_Number': '3',
            'Data_Type': 'Average'
        },
        {
            'Column': 'Process_1_Em2p_Inspection_4_Average_Data',
            'Database_Average': 0.40,
            'EM0580106P_Value': 0.36,
            'Inspection_Value': 0.36,
            'Deviation': (0.40 - 0.36) / 0.40,
            'Matched_Inspection_Column': 'Inspection_4_Dimension_Average',
            'Matching_Strategy': 'Direct Type Mapping',
            'Material': 'Em2p',
            'Process_Number': '1',
            'Inspection_Number': '4',
            'Data_Type': 'Average'
        }
    ])
    
    # Add Em3p (EM0580107P) deviation data
    deviation_data.extend([
        {
            'Column': 'Process_1_Em3p_Inspection_3_Average_Data',
            'Database_Average': 0.90,
            'EM0580106P_Value': 0.91,
            'Inspection_Value': 0.91,
            'Deviation': (0.90 - 0.91) / 0.90,
            'Matched_Inspection_Column': 'Inspection_3_Resistance_Average',
            'Matching_Strategy': 'Direct Type Mapping',
            'Material': 'Em3p',
            'Process_Number': '1',
            'Inspection_Number': '3',
            'Data_Type': 'Average'
        }
    ])
    
    # Add Frame (FM05000102) deviation data
    deviation_data.extend([
        {
            'Column': 'Process_1_Frame_Inspection_1_Average_Data',
            'Database_Average': 85.41,
            'EM0580106P_Value': 85.42,
            'Inspection_Value': 85.42,
            'Deviation': (85.41 - 85.42) / 85.41,
            'Matched_Inspection_Column': 'Inspection_1_Average',
            'Matching_Strategy': 'Direct Type Mapping',
            'Material': 'Frame',
            'Process_Number': '1',
            'Inspection_Number': '1',
            'Data_Type': 'Average'
        }
    ])
    
    deviation_df = pd.DataFrame(deviation_data)
    
    return inspection_df, database_df, deviation_df

def test_excel_output():
    """Test the new Excel output function"""
    print("=== TESTING NEW EXCEL OUTPUT FUNCTION ===")
    
    # Create test data
    inspection_df, database_df, deviation_df = create_test_data()
    
    print(f"Created test data:")
    print(f"  - Inspection data: {len(inspection_df)} rows, {len(inspection_df.columns)} columns")
    print(f"  - Database data: {len(database_df)} rows, {len(database_df.columns)} columns")
    print(f"  - Deviation data: {len(deviation_df)} rows, {len(deviation_df.columns)} columns")
    
    # Test material code extraction
    print(f"\n=== TESTING MATERIAL CODE EXTRACTION ===")
    material_codes = extract_material_codes_from_inspection_data(inspection_df)
    print(f"Extracted material codes: {material_codes}")
    
    # Test material filtering
    print(f"\n=== TESTING MATERIAL FILTERING ===")
    for material_code in material_codes:
        filtered_df = filter_deviation_data_by_material(deviation_df, material_code)
        print(f"Material {material_code}: {len(filtered_df)} deviation rows")
        
        if not filtered_df.empty:
            material_sheet_df = create_material_sheet_data(filtered_df, material_code)
            print(f"  - Material sheet data: {len(material_sheet_df)} rows")
            if len(material_sheet_df) > 0:
                print(f"  - Columns: {list(material_sheet_df.columns)}")
    
    # Test full Excel output
    print(f"\n=== TESTING FULL EXCEL OUTPUT ===")
    test_filename = "test_material_data_output.xlsx"
    
    try:
        create_excel_output(
            process_df=None,  # Not used in new structure
            inspection_df=inspection_df,
            database_df=database_df,
            deviation_df=deviation_df,
            filename=test_filename
        )
        
        # Check if file was created
        if os.path.exists(test_filename):
            file_size = os.path.getsize(test_filename)
            print(f"\n[SUCCESS] Test Excel file created: {test_filename} ({file_size} bytes)")
            
            # Try to read back the Excel file to verify structure
            try:
                excel_file = pd.ExcelFile(test_filename)
                sheet_names = excel_file.sheet_names
                print(f"[SUCCESS] Excel file contains {len(sheet_names)} sheets: {sheet_names}")
                
                # Check a few sheets
                for sheet_name in sheet_names[:3]:  # Check first 3 sheets
                    df = pd.read_excel(test_filename, sheet_name=sheet_name)
                    print(f"  - Sheet '{sheet_name}': {len(df)} rows, {len(df.columns)} columns")
                    if len(df.columns) > 0:
                        print(f"    Columns: {list(df.columns)}")
                
            except Exception as e:
                print(f"[ERROR] Could not read back Excel file: {e}")
        else:
            print(f"[ERROR] Test Excel file was not created")
            
    except Exception as e:
        print(f"[ERROR] Error creating Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_excel_output()