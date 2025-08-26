#!/usr/bin/env python3
"""
Simple verification script to test PASS_NG column preservation
"""

import pandas as pd

def test_clean_function():
    """Test the clean_database_data_df function directly"""
    
    # Import the function
    try:
        from df_blk_output import clean_database_data_df
        print("✓ Successfully imported clean_database_data_df function")
    except Exception as e:
        print(f"✗ Failed to import function: {e}")
        return
    
    # Create a test DataFrame with PASS_NG column
    test_data = {
        'PASS_NG': ['1', '0', '1', '1'],
        'Model_Code': ['TEST1', 'TEST2', 'TEST3', 'TEST4'],
        'DATE': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04'],
        'NG_Cause_1': ['OK', 'TRIAL', 'OK', 'OK'],
        'NG_Cause_2': ['OK', 'OK', 'MASTER PUMP', 'OK'],
        'Some_Other_Column': ['Value1', 'Value2', 'Value3', 'Value4']
    }
    
    test_df = pd.DataFrame(test_data)
    print(f"\nOriginal test DataFrame:")
    print(f"Shape: {test_df.shape}")
    print(f"Columns: {list(test_df.columns)}")
    print(test_df)
    
    # Test keywords that should be filtered
    keywords_to_filter = ['NG', 'TRIAL', 'MASTER PUMP', 'RUNNING', 'RE PI']
    
    # Apply the cleaning function
    try:
        cleaned_df = clean_database_data_df(test_df, keywords_to_filter)
        print(f"\nCleaned DataFrame:")
        print(f"Shape: {cleaned_df.shape}")
        print(f"Columns: {list(cleaned_df.columns)}")
        print(cleaned_df)
        
        # Check if PASS_NG is preserved
        if 'PASS_NG' in cleaned_df.columns:
            print("\n✓ SUCCESS: PASS_NG column is preserved!")
        else:
            print("\n✗ FAILURE: PASS_NG column was removed!")
            
    except Exception as e:
        print(f"✗ Error during cleaning: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clean_function()
