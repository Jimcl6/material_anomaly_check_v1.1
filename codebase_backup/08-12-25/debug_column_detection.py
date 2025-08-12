#!/usr/bin/env python3
"""
Debug script to examine actual column names from material inspection tables
and understand why normalize_inspection_columns is only detecting Inspection_10_Pull_Test
"""

import os
import pandas as pd
import mysql.connector
import re

# Database configuration
DB_CONFIG = {
    'host': '192.168.2.148',
    'user': 'hpi.python',
    'password': 'hpi.python',
    'database': 'fc_1_data_db'
}

def create_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("✅ Database connection established successfully!")
        return connection
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def get_all_inspection_tables():
    """Get all tables that end with '_inspection'"""
    connection = create_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES LIKE '%_inspection'")
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()
        connection.close()
        return tables
    except Exception as e:
        print(f"❌ Error getting inspection tables: {e}")
        if connection:
            connection.close()
        return []

def analyze_inspection_table_columns(table_name):
    """Analyze columns in a specific inspection table"""
    connection = create_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print(f"\n🔍 ANALYZING TABLE: {table_name}")
        print("=" * 60)
        
        # Get table structure
        cursor.execute(f"DESCRIBE {table_name}")
        columns_info = cursor.fetchall()
        
        print(f"📊 Total columns: {len(columns_info)}")
        print(f"📋 Column details:")
        
        all_columns = []
        numeric_columns = []
        potential_inspection_columns = []
        
        for i, col in enumerate(columns_info, 1):
            col_name = col['Field']
            col_type = col['Type']
            all_columns.append(col_name)
            
            print(f"  {i:2d}. {col_name:<30} | {col_type}")
            
            # Check if it's a numeric column
            if any(num_type in col_type.lower() for num_type in ['int', 'float', 'double', 'decimal', 'numeric']):
                numeric_columns.append(col_name)
            
            # Check if it might be an inspection-related column
            inspection_keywords = ['inspection', 'test', 'measurement', 'value', 'result', 'data', 
                                 'resistance', 'dimension', 'pull', 'force', 'avg', 'average', 
                                 'min', 'minimum', 'max', 'maximum']
            
            if any(keyword in col_name.lower() for keyword in inspection_keywords):
                potential_inspection_columns.append(col_name)
        
        print(f"\n📈 Numeric columns ({len(numeric_columns)}):")
        for col in numeric_columns:
            print(f"  - {col}")
        
        print(f"\n🎯 Potential inspection columns ({len(potential_inspection_columns)}):")
        for col in potential_inspection_columns:
            print(f"  - {col}")
        
        # Try to get sample data to understand the values
        print(f"\n📋 SAMPLE DATA FROM {table_name}:")
        try:
            # Get latest 3 records
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY Lot_Number DESC LIMIT 3")
            sample_data = cursor.fetchall()
            
            if sample_data:
                print(f"Found {len(sample_data)} sample records:")
                for i, record in enumerate(sample_data, 1):
                    print(f"\n  Record {i}:")
                    for key, value in record.items():
                        if key not in ['ID', 'id']:  # Skip ID columns
                            print(f"    {key}: {value}")
            else:
                print("  No data found in table")
                
        except Exception as e:
            print(f"  ❌ Error getting sample data: {e}")
        
        cursor.close()
        connection.close()
        
        return {
            'table_name': table_name,
            'total_columns': len(all_columns),
            'all_columns': all_columns,
            'numeric_columns': numeric_columns,
            'potential_inspection_columns': potential_inspection_columns,
            'sample_data': sample_data if 'sample_data' in locals() else []
        }
        
    except Exception as e:
        print(f"❌ Error analyzing table {table_name}: {e}")
        if connection:
            connection.close()
        return None

def analyze_column_patterns():
    """Analyze patterns in inspection table column names"""
    print("\n" + "="*80)
    print("🔍 COMPREHENSIVE INSPECTION TABLE COLUMN ANALYSIS")
    print("="*80)
    
    # Get all inspection tables
    inspection_tables = get_all_inspection_tables()
    
    if not inspection_tables:
        print("❌ No inspection tables found!")
        return
    
    print(f"📊 Found {len(inspection_tables)} inspection tables:")
    for table in inspection_tables:
        print(f"  - {table}")
    
    # Analyze each table
    all_analysis = {}
    all_columns_combined = []
    
    for table in inspection_tables:
        analysis = analyze_inspection_table_columns(table)
        if analysis:
            all_analysis[table] = analysis
            all_columns_combined.extend(analysis['all_columns'])
    
    # Pattern analysis across all tables
    print(f"\n" + "="*80)
    print("🎯 PATTERN ANALYSIS ACROSS ALL INSPECTION TABLES")
    print("="*80)
    
    # Look for patterns that might indicate inspection numbers
    inspection_number_patterns = {}
    for col in all_columns_combined:
        # Look for numbers in column names
        numbers = re.findall(r'\d+', col)
        for num in numbers:
            if num not in inspection_number_patterns:
                inspection_number_patterns[num] = []
            inspection_number_patterns[num].append(col)
    
    print(f"📊 Numbers found in column names:")
    for num, columns in sorted(inspection_number_patterns.items()):
        if num in ['3', '4', '5', '10']:  # Focus on target inspections
            print(f"  🎯 Number '{num}' appears in {len(columns)} columns:")
            for col in columns[:5]:  # Show first 5 examples
                print(f"    - {col}")
            if len(columns) > 5:
                print(f"    ... and {len(columns) - 5} more")
        else:
            print(f"  Number '{num}': {len(columns)} columns")
    
    # Look for keyword patterns
    keyword_analysis = {
        'resistance': [],
        'dimension': [],
        'pull': [],
        'test': [],
        'average': [],
        'minimum': [],
        'maximum': [],
        'inspection': []
    }
    
    for col in all_columns_combined:
        col_lower = col.lower()
        for keyword in keyword_analysis.keys():
            if keyword in col_lower:
                keyword_analysis[keyword].append(col)
    
    print(f"\n📋 Keyword analysis:")
    for keyword, columns in keyword_analysis.items():
        if columns:
            print(f"  '{keyword}': {len(columns)} columns")
            for col in columns[:3]:  # Show first 3 examples
                print(f"    - {col}")
            if len(columns) > 3:
                print(f"    ... and {len(columns) - 3} more")
    
    # Generate recommendations
    print(f"\n" + "="*80)
    print("💡 RECOMMENDATIONS FOR NORMALIZE_INSPECTION_COLUMNS")
    print("="*80)
    
    target_inspections = ['3', '4', '5', '10']
    found_patterns = {}
    
    for inspection_num in target_inspections:
        if inspection_num in inspection_number_patterns:
            found_patterns[inspection_num] = inspection_number_patterns[inspection_num]
            print(f"✅ Inspection {inspection_num}: Found {len(inspection_number_patterns[inspection_num])} potential columns")
            
            # Show examples of actual column names for this inspection
            examples = inspection_number_patterns[inspection_num][:5]
            for example in examples:
                print(f"    Example: {example}")
        else:
            print(f"❌ Inspection {inspection_num}: No columns found with this number")
    
    return all_analysis

if __name__ == "__main__":
    print("🚀 Starting comprehensive inspection table column analysis...")
    analysis_results = analyze_column_patterns()
    
    if analysis_results:
        print(f"\n✅ Analysis complete! Found data for {len(analysis_results)} tables.")
        print("📝 Check the output above for detailed column information and recommendations.")
    else:
        print("❌ Analysis failed - no data retrieved.")