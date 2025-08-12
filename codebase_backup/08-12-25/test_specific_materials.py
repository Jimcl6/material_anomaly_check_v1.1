#!/usr/bin/env python3
"""
Test script to demonstrate extracting only the required materials:
Em2p, Em3p, Frame, Casing_Block, Df_Blk, Rod_Blk
"""

from main import get_process_dataframes, DB_CONFIG

def test_specific_materials():
    """Test extracting only the required materials from all process tables"""
    
    print("="*70)
    print("EXTRACTING REQUIRED MATERIALS ONLY")
    print("Materials: Em2p, Em3p, Frame, Casing_Block, Df_Blk, Rod_Blk")
    print("="*70)
    
    # Get data for only the required materials (this is now the default behavior)
    process_dfs = get_process_dataframes(DB_CONFIG)
    
    # Summary of what was found
    total_records = 0
    materials_found = {}
    
    for proc, df in process_dfs.items():
        process_num = int(proc.split('_')[1])
        
        # Extract material codes from column names
        material_cols = [col for col in df.columns if col.startswith(f'Process_{process_num}_') 
                        and not col.endswith('_Lot_No') 
                        and col not in [f'Process_{process_num}_DATE', f'Process_{process_num}_Model_Code', f'Process_{process_num}_S_N']]
        
        materials = [col.replace(f'Process_{process_num}_', '') for col in material_cols]
        
        print(f"\n{proc.upper()}:")
        print(f"  Records: {len(df):,}")
        print(f"  Materials: {materials}")
        print(f"  Columns: {len(df.columns)}")
        
        total_records += len(df)
        materials_found[proc] = materials
        
        # Show sample data
        if not df.empty:
            print("  Sample data:")
            for col in df.columns:
                if not col.endswith('_Lot_No'):
                    sample_val = df[col].iloc[0] if len(df) > 0 else 'N/A'
                    print(f"    {col}: {sample_val}")
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total records across all processes: {total_records:,}")
    print(f"Process tables with required materials: {len(process_dfs)}")
    
    # Show which materials are in which processes
    all_materials = set()
    for materials in materials_found.values():
        all_materials.update(materials)
    
    print(f"\nMaterials distribution:")
    for material in sorted(all_materials):
        processes = [proc for proc, materials in materials_found.items() if material in materials]
        print(f"  {material}: {', '.join(processes)}")
    
    return process_dfs

if __name__ == "__main__":
    test_specific_materials()