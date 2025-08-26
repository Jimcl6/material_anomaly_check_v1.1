#!/usr/bin/env python3
"""
Test script to verify PASS_NG column preservation in df_blk_output.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from df_blk_output import get_database_data_for_df_blk

def test_pass_ng_preservation():
    """Test that PASS_NG column is preserved in the DataFrame output"""
    print("Testing PASS_NG column preservation in df_blk_output.py...")
    print("=" * 60)
    
    try:
        # Get the cleaned DataFrame
        df = get_database_data_for_df_blk()
        
        if df is not None and not df.empty:
            print(f"DataFrame shape: {df.shape}")
            print(f"Columns ({len(df.columns)}): {list(df.columns)}")
            print()
            
            # Check if PASS_NG column exists
            if 'PASS_NG' in df.columns:
                print("✓ SUCCESS: PASS_NG column is present in DataFrame")
                print(f"PASS_NG column data type: {df['PASS_NG'].dtype}")
                print(f"PASS_NG unique values: {df['PASS_NG'].unique()}")
                print(f"PASS_NG value counts:")
                print(df['PASS_NG'].value_counts())
            else:
                print("✗ FAILURE: PASS_NG column is missing from DataFrame")
                print("Available columns:")
                for i, col in enumerate(df.columns):
                    print(f"  {i+1}. {col}")
            
            print()
            print("Sample data (first 3 rows):")
            print(df.head(3).to_string())
            
        else:
            print("No data returned from get_database_data_for_df_blk()")
            
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pass_ng_preservation()
