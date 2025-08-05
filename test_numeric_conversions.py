#!/usr/bin/env python3
"""
Test script for numeric conversion functionality in material inspection data processing.
Tests both database and inspection data conversions with various edge cases.
"""

import pandas as pd
import numpy as np
from main import convert_to_numeric_safe, perform_deviation_calculations

def test_numeric_conversion_edge_cases():
    """Test convert_to_numeric_safe with various edge cases"""
    print("\n=== Testing Numeric Conversion Edge Cases ===")
    
    test_cases = [
        (1.23, "Simple float"),
        ("1.23", "String float"),
        ("-1.23", "Negative number"),
        ("1,234.56", "Number with comma"),
        (" 1.23 ", "Whitespace padding"),
        ("abc", "Invalid string"),
        (None, "None value"),
        (np.nan, "NaN value"),
        ("", "Empty string"),
        ("1.23e-4", "Scientific notation"),
        ("inf", "Infinity"),
        ("-inf", "Negative infinity"),
        ("1.23.45", "Invalid multiple decimals"),
        ("12,34,56.78", "Multiple commas"),
    ]
    
    for value, description in test_cases:
        print(f"\n[TEST] Testing: {description}")
        print(f"Input value: {value} (type: {type(value)})")
        result, success = convert_to_numeric_safe(value, "test_column")
        print(f"Result: {result} (type: {type(result) if result is not None else None})")
        print(f"Success: {success}")

def test_database_conversions():
    """Test numeric conversions with database-style data"""
    print("\n=== Testing Database Data Conversions ===")
    
    # Create sample database data with various formats
    database_data = {
        'Process_1_Em2p_Inspection_3_Average_Data': ['0.91', '0.92', ' 0.93 ', '0,94', 'invalid', None],
        'Process_1_Em2p_Inspection_4_Average_Data': [0.38, 0.39, np.nan, '0.40', '0,41', ''],
        'Process_1_Em2p_Inspection_5_Average_Data': ['0.42e0', '4.3e-1', '0.44', '0.45', '0.46', '0.47'],
    }
    
    database_df = pd.DataFrame(database_data)
    print("\nSample database data:")
    print(database_df)
    
    # Test conversion of each column
    for col in database_df.columns:
        print(f"\n[DEBUG] Testing column: {col}")
        numeric_values = []
        for value in database_df[col]:
            converted, success = convert_to_numeric_safe(value, col)
            if success:
                numeric_values.append(converted)
        
        if numeric_values:
            numeric_series = pd.Series(numeric_values)
            print(f"Successfully converted values: {len(numeric_values)}")
            print(f"Mean: {numeric_series.mean():.4f}")
            print(f"Min: {numeric_series.min():.4f}")
            print(f"Max: {numeric_series.max():.4f}")

def test_inspection_conversions():
    """Test numeric conversions with inspection-style data"""
    print("\n=== Testing Inspection Data Conversions ===")
    
    # Create sample inspection data with various formats
    inspection_data = {
        'Inspection_3_Resistance_Average': ['0.91'],
        'Inspection_4_Dimension_Average': [0.38],
        'Inspection_5_Dimension_Average': ['0,42'],
        'Inspection_10_Pull_Test': ['2.14'],
        'Non_Numeric_Column': ['abc'],
        'Mixed_Format': ['1,234.56'],
        'Scientific_Notation': ['1.23e-4'],
        'Invalid_Number': ['1.23.45'],
    }
    
    inspection_df = pd.DataFrame(inspection_data)
    print("\nSample inspection data:")
    print(inspection_df)
    
    # Test conversion of each column
    for col in inspection_df.columns:
        print(f"\n[DEBUG] Testing column: {col}")
        value = inspection_df[col].iloc[0]
        converted, success = convert_to_numeric_safe(value, col)
        print(f"Original value: {value} (type: {type(value)})")
        print(f"Converted value: {converted} (type: {type(converted) if converted is not None else None})")
        print(f"Conversion success: {success}")

def test_full_deviation_calculation():
    """Test the complete deviation calculation process"""
    print("\n=== Testing Complete Deviation Calculation ===")
    
    # Create sample database data
    database_data = {
        'Process_1_Em2p_Inspection_3_Average_Data': np.random.normal(0.91, 0.05, 100),
        'Process_1_Em2p_Inspection_4_Average_Data': np.random.normal(0.38, 0.05, 100),
        'Process_1_Em2p_Inspection_5_Average_Data': np.random.normal(0.42, 0.05, 100),
        'Process_1_Em2p_Inspection_10_Average_Data': np.random.normal(2.14, 0.2, 100),
    }
    
    database_df = pd.DataFrame(database_data)
    
    # Create sample inspection data
    inspection_data = {
        'Inspection_3_Resistance_Average': [0.91],
        'Inspection_4_Dimension_Average': [0.38],
        'Inspection_5_Dimension_Average': [0.42],
        'Inspection_10_Pull_Test': [2.14],
    }
    
    inspection_df = pd.DataFrame(inspection_data)
    
    print("\nSample database data shape:", database_df.shape)
    print("Sample inspection data shape:", inspection_df.shape)
    
    # Run deviation calculations
    result_df = perform_deviation_calculations(database_df, inspection_df)
    
    if result_df is not None and not result_df.empty:
        print("\n[SUCCESS] Deviation calculation successful!")
        print("\nDeviation results:")
        print(result_df[['Column', 'Database_Average', 'Inspection_Value', 'Deviation']])
    else:
        print("\n[ERROR] Deviation calculation failed!")

if __name__ == "__main__":
    print("\n=== Starting numeric conversion tests... ===")
    
    # Run all tests
    test_numeric_conversion_edge_cases()
    test_database_conversions()
    test_inspection_conversions()
    test_full_deviation_calculation()
    
    print("\n=== All tests completed! ===")