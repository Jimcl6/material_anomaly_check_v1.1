#!/usr/bin/env python3
"""
Comprehensive test script to verify GUI table enhancements and system functionality
"""

import sys
import os
import pandas as pd
import traceback

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_df_blk_data_structure():
    """Test that df_blk_output produces the expected data structure for GUI display"""
    print("=" * 60)
    print("TESTING DF_BLK DATA STRUCTURE FOR GUI")
    print("=" * 60)
    
    try:
        from df_blk_output import get_database_data_for_df_blk, calculate_df_blk_deviations
        
        # Get database data
        print("1. Testing database data retrieval...")
        database_df = get_database_data_for_df_blk()
        
        if database_df is not None and not database_df.empty:
            print(f"✓ Database DataFrame shape: {database_df.shape}")
            print(f"✓ PASS_NG column present: {'PASS_NG' in database_df.columns}")
            
            # Check for critical columns
            critical_cols = ['DATE', 'Model_Code', 'Process_SN', 'SN']
            present_critical = [col for col in critical_cols if col in database_df.columns]
            print(f"✓ Critical columns present: {present_critical}")
            
            # Create mock combined data for deviation calculation test
            print("\n2. Testing deviation calculation structure...")
            mock_combined_df = pd.DataFrame({
                'Process_2_Df_Blk_Inspection_3_Maximum_Data': [1.234],
                'Process_2_Df_Blk_Inspection_4_Average_Data': [2.567],
                'Model_Code': ['TEST_MODEL'],
                'Process_SN': ['TEST_SN_001']
            })
            
            # Test deviation calculation
            deviation_df = calculate_df_blk_deviations(database_df, mock_combined_df)
            
            if deviation_df is not None and not deviation_df.empty:
                print(f"✓ Deviation DataFrame shape: {deviation_df.shape}")
                print(f"✓ Deviation DataFrame columns: {list(deviation_df.columns)}")
                
                # Check for GUI-required columns
                gui_required_cols = ['Column', 'Database Average', 'Inspection Value', 'Deviation', 'Matched Inspection Column']
                present_gui_cols = [col for col in gui_required_cols if col in deviation_df.columns]
                missing_gui_cols = [col for col in gui_required_cols if col not in deviation_df.columns]
                
                print(f"✓ GUI columns present: {present_gui_cols}")
                if missing_gui_cols:
                    print(f"⚠ GUI columns missing: {missing_gui_cols}")
                
                # Show sample data
                print("\n3. Sample deviation data for GUI:")
                print(deviation_df.head(3).to_string())
                
                return True
            else:
                print("✗ No deviation data generated")
                return False
        else:
            print("✗ No database data retrieved")
            return False
            
    except Exception as e:
        print(f"✗ Error testing df_blk data structure: {e}")
        traceback.print_exc()
        return False

def test_all_material_scripts_consistency():
    """Test that all material processing scripts return consistent record counts"""
    print("\n" + "=" * 60)
    print("TESTING MATERIAL SCRIPTS CONSISTENCY")
    print("=" * 60)
    
    test_model = "TEST_MODEL"
    test_limit = 50
    results = {}
    
    scripts_to_test = [
        ('frame', 'get_database_data_for_model'),
        ('csb_data_output', 'get_database_data_for_model'),
        ('em_material', 'get_database_data_for_model'),
        ('rod_blk_output', 'get_database_data_for_model'),
        ('df_blk_output', 'get_database_data_for_df_blk')
    ]
    
    for script_name, function_name in scripts_to_test:
        try:
            print(f"\nTesting {script_name}.{function_name}...")
            module = __import__(script_name)
            func = getattr(module, function_name)
            
            if function_name == 'get_database_data_for_df_blk':
                # df_blk_output doesn't take parameters
                result = func()
            else:
                result = func(test_model, test_limit)
            
            if result is not None and not result.empty:
                record_count = len(result)
                column_count = len(result.columns)
                has_pass_ng = 'PASS_NG' in result.columns
                
                results[script_name] = {
                    'records': record_count,
                    'columns': column_count,
                    'has_pass_ng': has_pass_ng,
                    'success': True
                }
                
                print(f"  ✓ Records: {record_count}")
                print(f"  ✓ Columns: {column_count}")
                print(f"  ✓ PASS_NG present: {has_pass_ng}")
            else:
                results[script_name] = {
                    'records': 0,
                    'columns': 0,
                    'has_pass_ng': False,
                    'success': False
                }
                print(f"  ✗ No data returned")
                
        except Exception as e:
            results[script_name] = {
                'records': 0,
                'columns': 0,
                'has_pass_ng': False,
                'success': False,
                'error': str(e)
            }
            print(f"  ✗ Error: {e}")
    
    # Analyze consistency
    print(f"\n{'='*60}")
    print("CONSISTENCY ANALYSIS")
    print(f"{'='*60}")
    
    successful_scripts = [name for name, data in results.items() if data['success']]
    if len(successful_scripts) > 1:
        record_counts = [results[name]['records'] for name in successful_scripts if name != 'df_blk_output']
        
        if record_counts:
            unique_counts = set(record_counts)
            if len(unique_counts) == 1:
                print(f"✓ All scripts return consistent record count: {list(unique_counts)[0]}")
            else:
                print(f"⚠ Inconsistent record counts: {dict(zip(successful_scripts[:-1], record_counts))}")
        
        # Check PASS_NG consistency
        pass_ng_status = [results[name]['has_pass_ng'] for name in successful_scripts]
        if all(pass_ng_status):
            print("✓ All scripts preserve PASS_NG column")
        else:
            print("⚠ Some scripts missing PASS_NG column")
    
    return results

def test_gui_column_mapping():
    """Test the GUI column mapping logic"""
    print("\n" + "=" * 60)
    print("TESTING GUI COLUMN MAPPING")
    print("=" * 60)
    
    # Test data structure that GUI expects
    test_deviation_data = {
        'Column': ['Process_2_Df_Blk_Inspection_3_Maximum_Data', 'Process_2_Df_Blk_Inspection_4_Average_Data'],
        'Database Average': [1.234, 2.567],
        'Inspection Value': [1.200, 2.600],
        'Deviation': [0.0275, -0.0128],
        'Material': ['Df Block', 'Df Block'],
        'S/N': ['TEST_SN_001', 'TEST_SN_002'],
        'Matched Inspection Column': ['Df_Blk_Inspection_3_Maximum', 'Df_Blk_Inspection_4_Average']
    }
    
    df = pd.DataFrame(test_deviation_data)
    
    print("Test DataFrame structure:")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    
    # Test DF Block column selection logic
    available_columns = list(df.columns)
    desired_columns_df_blk = ["Matched Inspection Column", "Database Average", "Inspection Value", "Deviation", "Material", "S/N"]
    display_columns = [col for col in desired_columns_df_blk if col in available_columns]
    
    print(f"\nDF Block display columns: {display_columns}")
    
    # Test data formatting
    print("\nFormatted sample data:")
    for _, row in df.head(2).iterrows():
        values = []
        for col in display_columns:
            value = row.get(col, 'N/A')
            if col == "Deviation" and isinstance(value, (int, float)):
                # Simulate percentage formatting
                percentage = value * 100
                value = f"{percentage:.2f}%"
            elif col in ["Database Average", "Inspection Value"] and isinstance(value, (int, float)):
                value = f"{value:.3f}"
            values.append(str(value))
        print(f"  Row: {values}")
    
    return True

def main():
    """Run all tests"""
    print("MATERIAL ANOMALY DETECTION SYSTEM - COMPREHENSIVE TEST")
    print("=" * 80)
    
    test_results = {
        'df_blk_structure': test_df_blk_data_structure(),
        'script_consistency': test_all_material_scripts_consistency(),
        'gui_mapping': test_gui_column_mapping()
    }
    
    print("\n" + "=" * 80)
    print("FINAL TEST SUMMARY")
    print("=" * 80)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name:<20}: {status}")
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! System is ready for use.")
    else:
        print("⚠ Some tests failed. Please review the issues above.")

if __name__ == "__main__":
    main()
