#!/usr/bin/env python3
"""
Test script to demonstrate CSV-Database correlation functionality with sample data
"""

import pandas as pd
from main import correlate_csv_with_database_materials, get_material_summary_for_csv_entry, DB_CONFIG

def create_sample_csv_data():
    """Create sample CSV data for testing"""
    sample_data = {
        'MODEL CODE': ['60CAT0213P', '60CAT0213P', '60CAT0213P', '60CAT0213P'],
        'PROCESS S/N': [1, 2, 3, 4],
        'OTHER_COLUMN': ['A', 'B', 'C', 'D']
    }
    return pd.DataFrame(sample_data)

def test_correlation_with_sample_data():
    """Test the correlation functionality with sample data"""
    
    print("="*70)
    print("TESTING CSV-DATABASE CORRELATION WITH SAMPLE DATA")
    print("="*70)
    
    # Create sample CSV data
    sample_csv = create_sample_csv_data()
    print("Sample CSV Data:")
    print(sample_csv)
    print(f"\nLatest CSV entry will be: MODEL CODE = {sample_csv.iloc[-1]['MODEL CODE']}, PROCESS S/N = {sample_csv.iloc[-1]['PROCESS S/N']}")
    
    try:
        # Test the complete workflow
        print("\n" + "="*70)
        print("TESTING COMPLETE MATERIAL SUMMARY WORKFLOW")
        print("="*70)
        
        material_summary = get_material_summary_for_csv_entry(sample_csv, DB_CONFIG)
        
        print("\n" + "="*70)
        print("CORRELATION TEST RESULTS")
        print("="*70)
        
        if material_summary:
            print(f"✅ Correlation function executed successfully")
            print(f"CSV Entry: {material_summary['csv_entry']['model_code']} | S/N: {material_summary['csv_entry']['process_sn']}")
            print(f"Total matches found: {material_summary['total_matches']}")
            print(f"Materials found: {len(material_summary['materials_found'])}")
            
            if material_summary['materials_found']:
                print("\nMaterial Details:")
                for material, processes in material_summary['materials_found'].items():
                    print(f"  {material}:")
                    for process_info in processes:
                        print(f"    {process_info['process']}: {process_info['material_values']}")
            else:
                print("No materials found for this CSV entry in the database")
        else:
            print("❌ No correlation results returned")
            
    except Exception as e:
        print(f"❌ Error during correlation test: {e}")
        print("This might be due to database connection issues or missing data")
        
        # Show what the correlation would look like with mock data
        print("\n" + "="*70)
        print("MOCK CORRELATION EXAMPLE")
        print("="*70)
        
        mock_process_dfs = {
            'process_1': pd.DataFrame({
                'Process_1_DATE': ['2024/08/19', '2024/08/19'],
                'Process_1_Model_Code': ['60CAT0213P', '60CAT0213P'],
                'Process_1_S_N': [4, 5],
                'Process_1_Em2p': ['EM0580106P', 'EM0580106P'],
                'Process_1_Em2p_Lot_No': ['CAT-4G03DI', 'CAT-4G03DI'],
                'Process_1_Em3p': ['EM0580107P', 'EM0580107P'],
                'Process_1_Em3p_Lot_No': ['CAT-4G10DI', 'CAT-4G10DI'],
                'Process_1_Frame': ['FM05000102-01A', 'FM05000102-01A'],
                'Process_1_Frame_Lot_No': ['072324A-40', '072324A-40']
            }),
            'process_2': pd.DataFrame({
                'Process_2_DATE': ['2024/08/19'],
                'Process_2_Model_Code': ['60CAT0213P'],
                'Process_2_S_N': [4],
                'Process_2_Df_Blk': ['DFB6600600'],
                'Process_2_Df_Blk_Lot_No': ['20240809-A'],
                'Process_2_Rod_Blk': ['RDB5200200'],
                'Process_2_Rod_Blk_Lot_No': ['20240805-B']
            })
        }
        
        print("Mock correlation with sample data:")
        mock_results = correlate_csv_with_database_materials(sample_csv, mock_process_dfs)
        
        print(f"\nMock Results Summary:")
        for proc, result in mock_results.items():
            if result['found']:
                print(f"  {proc}: ✅ Found {result['matches']} matches")
                for material, info in result['materials'].items():
                    print(f"    {material}: {info['material_values']}")
            else:
                print(f"  {proc}: ❌ No matches")

if __name__ == "__main__":
    test_correlation_with_sample_data()