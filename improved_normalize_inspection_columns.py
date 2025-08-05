#!/usr/bin/env python3
"""
Improved normalize_inspection_columns function with enhanced flexibility
to handle real-world material inspection table column names
"""

import pandas as pd
import re

def improved_normalize_inspection_columns(inspection_df):
    """
    Enhanced normalize inspection DataFrame column names with much more flexible pattern matching.
    
    This version:
    1. Handles real-world column naming conventions
    2. Uses multiple strategies to identify inspection types
    3. Is more tolerant of different naming patterns
    4. Provides comprehensive debug logging
    
    Args:
        inspection_df: DataFrame with inspection data
        
    Returns:
        DataFrame with normalized column names
    """
    if inspection_df is None or inspection_df.empty:
        return inspection_df
    
    print("\n=== IMPROVED NORMALIZE INSPECTION COLUMN NAMES ===")
    print(f"📊 Original columns ({len(inspection_df.columns)}): {list(inspection_df.columns)}")
    
    # Show sample data to understand what we're working with
    print(f"\n📋 [DEBUG] Sample inspection data:")
    if not inspection_df.empty:
        for col in inspection_df.columns:
            try:
                sample_value = inspection_df[col].iloc[0]
                print(f"  {col}: {sample_value} (type: {type(sample_value).__name__})")
            except:
                print(f"  {col}: <error reading value>")
    
    # Create a mapping of old column names to new standardized names
    column_mapping = {}
    
    # Enhanced inspection type mapping with more flexible detection
    inspection_strategies = {
        '3': {
            'type': 'Resistance',
            'keywords': ['resistance', 'resist', 'ohm', 'impedance', 'electrical', 'conductivity', 'continuity'],
            'patterns': [r'.*_3_.*', r'.*resistance.*', r'.*ohm.*', r'.*electrical.*', r'.*continuity.*']
        },
        '4': {
            'type': 'Dimension',
            'keywords': ['dimension', 'dim', 'size', 'measurement', 'length', 'width', 'height', 'thickness', 'diameter', 'distance'],
            'patterns': [r'.*_4_.*', r'.*dimension.*', r'.*size.*', r'.*length.*', r'.*width.*', r'.*height.*', r'.*thickness.*', r'.*diameter.*']
        },
        '5': {
            'type': 'Dimension',
            'keywords': ['dimension', 'dim', 'size', 'measurement', 'length', 'width', 'height', 'thickness', 'diameter', 'distance', 'clearance'],
            'patterns': [r'.*_5_.*', r'.*dimension.*', r'.*size.*', r'.*clearance.*', r'.*gap.*', r'.*spacing.*']
        },
        '10': {
            'type': 'Pull_Test',
            'keywords': ['pull', 'test', 'pulltest', 'tensile', 'force', 'strength', 'load', 'breaking'],
            'patterns': [r'.*_10_.*', r'.*pull.*', r'.*test.*', r'.*tensile.*', r'.*force.*', r'.*strength.*', r'.*load.*']
        }
    }
    
    print(f"\n🎯 [DEBUG] Enhanced inspection strategies:")
    for num, strategy in inspection_strategies.items():
        print(f"  Inspection {num} ({strategy['type']}): {len(strategy['keywords'])} keywords, {len(strategy['patterns'])} patterns")
    
    print(f"\n🔍 [DEBUG] Processing {len(inspection_df.columns)} columns for normalization...")
    
    # Process each column
    for col in inspection_df.columns:
        if col in ['Lot_Number', 'Material_Code', 'Date', 'DateTime', 'ID', 'id']:
            print(f"  ⏭️  [SKIP] Identifier column: {col}")
            continue  # Keep identifier columns as-is
        
        print(f"\n  🔍 [PROCESS] Analyzing column: {col}")
        
        # Strategy 1: Direct pattern matching for inspection numbers
        inspection_num = None
        matched_strategy = None
        
        for num, strategy in inspection_strategies.items():
            # Check patterns first
            for pattern in strategy['patterns']:
                if re.search(pattern, col.lower()):
                    inspection_num = num
                    matched_strategy = f"Pattern match: {pattern}"
                    print(f"    ✅ [PATTERN] Found inspection {num} using pattern: {pattern}")
                    break
            
            if inspection_num:
                break
        
        # Strategy 2: Keyword-based detection if pattern matching fails
        if not inspection_num:
            for num, strategy in inspection_strategies.items():
                for keyword in strategy['keywords']:
                    if keyword in col.lower():
                        inspection_num = num
                        matched_strategy = f"Keyword match: {keyword}"
                        print(f"    ✅ [KEYWORD] Found inspection {num} using keyword: {keyword}")
                        break
                
                if inspection_num:
                    break
        
        # Strategy 3: Numeric column heuristics
        if not inspection_num:
            # Check if it's a numeric column that might be inspection data
            try:
                # Try to convert sample values to see if it's numeric
                sample_val = inspection_df[col].iloc[0] if len(inspection_df) > 0 else None
                if sample_val is not None:
                    numeric_val = pd.to_numeric(sample_val, errors='coerce')
                    if not pd.isna(numeric_val):
                        # This is a numeric column, try to infer inspection type
                        if any(keyword in col.lower() for keyword in ['avg', 'average', 'min', 'minimum', 'max', 'maximum', 'value', 'data', 'result']):
                            # Default to inspection 4 (Dimension) for unidentified numeric columns
                            inspection_num = '4'
                            matched_strategy = "Numeric column heuristic"
                            print(f"    🔢 [HEURISTIC] Defaulting to inspection 4 (Dimension) for numeric column: {col}")
            except:
                pass
        
        # Strategy 4: Fallback - any remaining numeric columns
        if not inspection_num:
            # Check if column contains any inspection-related terms
            inspection_terms = ['inspection', 'test', 'measurement', 'value', 'result', 'data']
            if any(term in col.lower() for term in inspection_terms):
                inspection_num = '4'  # Default fallback
                matched_strategy = "Fallback to inspection 4"
                print(f"    🔄 [FALLBACK] Defaulting to inspection 4 for inspection-related column: {col}")
        
        # Process the column if we found an inspection number
        if inspection_num and inspection_num in inspection_strategies:
            strategy = inspection_strategies[inspection_num]
            inspection_type = strategy['type']
            
            # Determine the data type (Average, Minimum, Maximum)
            data_type = 'Average'  # Default
            if any(keyword in col.lower() for keyword in ['min', 'minimum']):
                data_type = 'Minimum'
            elif any(keyword in col.lower() for keyword in ['max', 'maximum']):
                data_type = 'Maximum'
            elif any(keyword in col.lower() for keyword in ['avg', 'average', 'mean']):
                data_type = 'Average'
            
            print(f"    📊 [TYPE] Determined data type: {data_type}")
            print(f"    🎯 [TYPE] Mapped inspection type: {inspection_type}")
            print(f"    🔧 [STRATEGY] Used strategy: {matched_strategy}")
            
            # Create standardized column name
            if inspection_type == 'Pull_Test':
                new_col_name = f'Inspection_{inspection_num}_Pull_Test'
            else:
                new_col_name = f'Inspection_{inspection_num}_{inspection_type}_{data_type}'
            
            column_mapping[col] = new_col_name
            print(f"    ✅ [MAP] {col} -> {new_col_name}")
        else:
            print(f"    ❌ [SKIP] No inspection mapping found for: {col}")
    
    print(f"\n📋 [SUMMARY] Created {len(column_mapping)} column mappings")
    
    # Show detailed mapping summary
    if column_mapping:
        print(f"\n📝 [MAPPINGS] Column mappings created:")
        for old_col, new_col in column_mapping.items():
            print(f"  {old_col} -> {new_col}")
        
        # Apply the column mapping
        normalized_df = inspection_df.rename(columns=column_mapping)
        print(f"\n✅ [SUCCESS] Normalized columns ({len(normalized_df.columns)}): {list(normalized_df.columns)}")
        
        # Show breakdown by inspection type
        inspection_counts = {}
        for new_col in column_mapping.values():
            if 'Inspection_' in new_col:
                parts = new_col.split('_')
                if len(parts) >= 2:
                    insp_num = parts[1]
                    if insp_num not in inspection_counts:
                        inspection_counts[insp_num] = 0
                    inspection_counts[insp_num] += 1
        
        print(f"\n📊 [BREAKDOWN] Columns by inspection type:")
        for insp_num, count in sorted(inspection_counts.items()):
            insp_type = inspection_strategies.get(insp_num, {}).get('type', 'Unknown')
            print(f"  Inspection {insp_num} ({insp_type}): {count} columns")
        
        return normalized_df
    else:
        print(f"\n⚠️  [WARNING] No columns were normalized - using original DataFrame")
        print(f"💡 [INFO] This might indicate that the inspection table column names don't match any expected patterns")
        print(f"🔍 [INFO] Consider examining the actual column names in the material inspection tables")
        
        # Show what we tried to match
        print(f"\n🔍 [DEBUG] Patterns and keywords we tried to match:")
        for num, strategy in inspection_strategies.items():
            print(f"  Inspection {num} ({strategy['type']}):")
            print(f"    Keywords: {strategy['keywords'][:5]}...")  # Show first 5 keywords
            print(f"    Patterns: {strategy['patterns'][:3]}...")   # Show first 3 patterns
        
        return inspection_df

# Test function to demonstrate the improvements
def test_improved_normalization():
    """Test the improved normalization with various column name scenarios"""
    
    # Test case 1: Real-world column names that might exist
    test_data_1 = {
        'Lot_Number': ['TEST123'],
        'Material_Code': ['EM0580106P'],
        'Resistance_Ohm': [0.91],
        'Resistance_Min': [0.88],
        'Resistance_Max': [0.96],
        'Dimension_Length_mm': [0.38],
        'Dimension_Width_mm': [0.42],
        'Pull_Test_Force_N': [2.14],
        'Electrical_Continuity': [1],
        'Size_Measurement': [0.35],
        'Test_Result_10': [2.20],
        'Unknown_Value': [1.5]
    }
    
    test_df_1 = pd.DataFrame(test_data_1)
    print("="*80)
    print("🧪 TEST CASE 1: Real-world column names")
    print("="*80)
    result_1 = improved_normalize_inspection_columns(test_df_1)
    
    # Test case 2: Column names with numbers
    test_data_2 = {
        'Lot_Number': ['TEST456'],
        'Material_Code': ['FM05000102'],
        'Insp_3_Resistance': [13.5],
        'Insp_4_Dimension': [7.94],
        'Insp_5_Size': [7.94],
        'Test_10_Pull': [2.15],
        'Value_3_Min': [13.50],
        'Value_4_Avg': [7.94],
        'Measurement_5': [7.95]
    }
    
    test_df_2 = pd.DataFrame(test_data_2)
    print("\n" + "="*80)
    print("🧪 TEST CASE 2: Column names with inspection numbers")
    print("="*80)
    result_2 = improved_normalize_inspection_columns(test_df_2)
    
    return result_1, result_2

if __name__ == "__main__":
    print("🚀 Testing improved normalize_inspection_columns function...")
    test_improved_normalization()