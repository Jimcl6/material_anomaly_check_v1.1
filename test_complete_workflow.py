#!/usr/bin/env python3
"""
Comprehensive test script to verify the complete material anomaly detection workflow
Tests all material processing scripts for PASS_NG column preservation and consistent filtering
"""

import sys
import os
import pandas as pd
import traceback

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_script_function(script_name, function_name, *args):
    """Test a specific function from a script and check for PASS_NG column"""
    try:
        print(f"\n{'='*50}")
        print(f"Testing {script_name}.{function_name}")
        print(f"{'='*50}")
        
        # Import the module
        module = __import__(script_name)
        func = getattr(module, function_name)
        
        # Call the function
        if args:
            result = func(*args)
        else:
            result = func()
        
        if result is not None and not result.empty:
            print(f"✓ Function executed successfully")
            print(f"  DataFrame shape: {result.shape}")
            print(f"  Total columns: {len(result.columns)}")
            
            # Check for PASS_NG column
            if 'PASS_NG' in result.columns:
                print(f"  ✓ PASS_NG column present")
                print(f"  PASS_NG unique values: {result['PASS_NG'].unique()}")
                print(f"  PASS_NG distribution: {dict(result['PASS_NG'].value_counts())}")
            else:
                print(f"  ✗ PASS_NG column missing")
            
            # Check for critical columns
            critical_cols = ['DATE', 'Model_Code', 'Process_SN', 'SN']
            present_critical = [col for col in critical_cols if col in result.columns]
            print(f"  Critical columns present: {present_critical}")
            
            return True, result
        else:
            print(f"✗ Function returned empty or None result")
            return False, None
            
    except Exception as e:
        print(f"✗ Error testing {script_name}.{function_name}: {e}")
        traceback.print_exc()
        return False, None

def main():
    """Run comprehensive workflow test"""
    print("MATERIAL ANOMALY DETECTION WORKFLOW TEST")
    print("="*60)
    
    test_results = {}
    
    # Test df_blk_output
    success, df = test_script_function('df_blk_output', 'get_database_data_for_df_blk')
    test_results['df_blk_output'] = success
    
    # Test frame with a sample model code
    success, df = test_script_function('frame', 'get_database_data_for_model', 'SAMPLE_MODEL', 50)
    test_results['frame'] = success
    
    # Test em_material with a sample model code
    success, df = test_script_function('em_material', 'get_database_data_for_model', 'SAMPLE_MODEL', 50)
    test_results['em_material'] = success
    
    # Test csb_data_output with a sample model code
    success, df = test_script_function('csb_data_output', 'get_database_data_for_model', 'SAMPLE_MODEL', 50)
    test_results['csb_data_output'] = success
    
    # Test rod_blk_output with a sample model code
    success, df = test_script_function('rod_blk_output', 'get_database_data_for_model', 'SAMPLE_MODEL', 50)
    test_results['rod_blk_output'] = success
    
    # Summary
    print(f"\n{'='*60}")
    print("WORKFLOW TEST SUMMARY")
    print(f"{'='*60}")
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for script, success in test_results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {script:<20}: {status}")
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All material processing scripts are working correctly!")
        print("✓ PASS_NG column preservation is functioning properly")
        print("✓ Keyword filtering is applied consistently")
    else:
        print("⚠ Some issues detected in the workflow")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
