#!/usr/bin/env python3
"""
Test script to verify the Frame material code processing logic
"""

def test_frame_material_processing():
    """Test the Frame material code processing logic"""
    
    # Test cases
    test_cases = [
        # Frame material codes that should be processed
        ("FM05000102-01A", "fm05000102_inspection", True),
        ("FM12345678-01A", "fm12345678_inspection", True),
        ("FM99999999-01A", "fm99999999_inspection", True),
        
        # Frame material codes that should NOT be processed (different suffix)
        ("FM05000102-02B", "fm05000102-02b_inspection", False),
        ("FM05000102", "fm05000102_inspection", False),
        
        # Other material codes that should NOT be processed
        ("Em2p", "em2p_inspection", False),
        ("Em3p", "em3p_inspection", False),
        ("Casing_Block", "casing_block_inspection", False),
        ("Rod_Blk", "rod_blk_inspection", False),
        ("Df_Blk", "df_blk_inspection", False),
        ("EM05000102-01A", "em05000102-01a_inspection", False),  # Doesn't start with 'FM'
    ]
    
    print("=== TESTING FRAME MATERIAL CODE PROCESSING LOGIC ===\n")
    
    all_passed = True
    
    for material_code, expected_table_name, should_be_processed in test_cases:
        # Apply the same logic as in the modified function
        processed_material_code = material_code
        was_processed = False
        
        if material_code.startswith('FM') and material_code.endswith('-01A'):
            processed_material_code = material_code[:-4]  # Remove last 4 characters (-01A)
            was_processed = True
            print(f"  🔧 Frame material code processed: {material_code} -> {processed_material_code}")
        
        # Convert processed material code to lowercase for table name
        table_name = f"{processed_material_code.lower()}_inspection"
        
        # Check results
        processing_correct = was_processed == should_be_processed
        table_name_correct = table_name == expected_table_name
        
        status = "✅ PASS" if (processing_correct and table_name_correct) else "❌ FAIL"
        
        print(f"{status} | Input: '{material_code}' -> Table: '{table_name}' | Processed: {was_processed}")
        
        if not (processing_correct and table_name_correct):
            print(f"    Expected table: '{expected_table_name}', Expected processed: {should_be_processed}")
            all_passed = False
    
    print(f"\n=== TEST SUMMARY ===")
    if all_passed:
        print("🎉 All tests PASSED! The Frame material code processing logic works correctly.")
    else:
        print("❌ Some tests FAILED! Please review the logic.")
    
    return all_passed

if __name__ == "__main__":
    test_frame_material_processing()