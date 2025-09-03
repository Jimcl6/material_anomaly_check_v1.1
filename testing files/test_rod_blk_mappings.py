#!/usr/bin/env python3
"""
Test script to verify the updated ROD_BLK column mappings
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_column_mappings():
    """Test the ROD_BLK_COLUMN_MAPPING dictionary"""
    try:
        from rod_blk_output import ROD_BLK_COLUMN_MAPPING, material_patterns
        
        print("=== ROD_BLK COLUMN MAPPING VERIFICATION ===\n")
        
        # Test 1: Check total mappings
        total_mappings = len(ROD_BLK_COLUMN_MAPPING)
        print(f"✓ Total column mappings defined: {total_mappings}")
        
        # Test 2: Check Tesla mappings
        tesla_mappings = {k: v for k, v in ROD_BLK_COLUMN_MAPPING.items() if 'Tesla' in k}
        print(f"✓ Tesla mappings: {len(tesla_mappings)}")
        
        # Show sample Tesla mappings
        print("  Sample Tesla mappings:")
        for i, (db_col, insp_col) in enumerate(tesla_mappings.items()):
            if i < 3:
                print(f"    {db_col} -> {insp_col}")
        
        # Test 3: Check Inspection mappings
        inspection_mappings = {k: v for k, v in ROD_BLK_COLUMN_MAPPING.items() if 'Inspection' in k}
        print(f"✓ Inspection mappings: {len(inspection_mappings)}")
        
        # Show sample Inspection mappings
        print("  Sample Inspection mappings:")
        for i, (db_col, insp_col) in enumerate(inspection_mappings.items()):
            if i < 5:
                print(f"    {db_col} -> {insp_col}")
        
        # Test 4: Check coverage of inspection numbers
        inspection_numbers = set()
        for db_col in inspection_mappings.keys():
            if 'Inspection_' in db_col:
                # Extract inspection number
                parts = db_col.split('_')
                for i, part in enumerate(parts):
                    if part == 'Inspection' and i + 1 < len(parts):
                        try:
                            insp_num = int(parts[i + 1])
                            inspection_numbers.add(insp_num)
                        except ValueError:
                            pass
        
        print(f"✓ Inspection numbers covered: {sorted(inspection_numbers)}")
        print(f"  Range: {min(inspection_numbers)} to {max(inspection_numbers)}")
        
        # Test 5: Check material patterns integration
        rod_blk_config = material_patterns.get('Rod_Blk', {})
        print(f"✓ Rod_Blk material configuration loaded")
        print(f"  Prefix: {rod_blk_config.get('prefix', 'Not found')}")
        print(f"  Tables: {rod_blk_config.get('inspection_table', 'Not found')}")
        print(f"  Has column mapping: {'column_mapping' in rod_blk_config}")
        
        if 'column_mapping' in rod_blk_config:
            mapping_count = len(rod_blk_config['column_mapping'])
            print(f"  Column mapping entries: {mapping_count}")
            
            # Verify the mapping is the same as ROD_BLK_COLUMN_MAPPING
            if rod_blk_config['column_mapping'] == ROD_BLK_COLUMN_MAPPING:
                print("  ✓ Column mapping correctly integrated")
            else:
                print("  ✗ Column mapping integration issue")
        
        # Test 6: Check for common patterns
        data_types = ['Average', 'Maximum', 'Minimum']
        missing_mappings = []
        
        for insp_num in range(1, 21):  # Check inspections 1-20
            for data_type in data_types:
                expected_db_col = f'Process_2_Rod_Blk_Inspection_{insp_num}_{data_type}_Data'
                if expected_db_col not in ROD_BLK_COLUMN_MAPPING:
                    missing_mappings.append(expected_db_col)
        
        if missing_mappings:
            print(f"⚠ Missing mappings found: {len(missing_mappings)}")
            for missing in missing_mappings[:5]:  # Show first 5
                print(f"    {missing}")
            if len(missing_mappings) > 5:
                print(f"    ... and {len(missing_mappings) - 5} more")
        else:
            print("✓ All expected inspection mappings present")
        
        print(f"\n=== SUMMARY ===")
        print(f"Total mappings: {total_mappings}")
        print(f"Tesla mappings: {len(tesla_mappings)}")
        print(f"Inspection mappings: {len(inspection_mappings)}")
        print(f"Inspection range: {min(inspection_numbers)}-{max(inspection_numbers)}")
        print(f"Missing mappings: {len(missing_mappings)}")
        
        if len(missing_mappings) == 0 and total_mappings > 60:
            print("\n🎉 All tests passed! Column mapping system is ready.")
            return True
        else:
            print(f"\n⚠ Some issues found. Please review the mappings.")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_column_mappings()
    exit(0 if success else 1)
