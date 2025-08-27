# Rod_Blk Column Mapping Documentation

## Overview
This document describes the enhanced column mapping system implemented in `rod_blk_output.py` to handle the new columns added to the `rd05200200_inspection` table.

## ROD_BLK_COLUMN_MAPPING Dictionary

The `ROD_BLK_COLUMN_MAPPING` dictionary provides precise mappings between `database_data` table columns and their corresponding inspection table columns.

### Structure
```python
ROD_BLK_COLUMN_MAPPING = {
    'database_data_column_name': 'target_table_column_name',
    # ... 72 total mappings
}
```

### Column Categories

#### 1. Tesla Measurements (12 mappings)
Maps columns from `database_data` to `rdb5200200_checksheet` table:

| Database Column | Target Column | Description |
|----------------|---------------|-------------|
| `Process_2_Rod_Blk_Tesla_1_Average_Data` | `Rod_Blk_Tesla_1_Avg_Data` | Tesla 1 Average |
| `Process_2_Rod_Blk_Tesla_1_Maximum_Data` | `Rod_Blk_Tesla_1_Max_Data` | Tesla 1 Maximum |
| `Process_2_Rod_Blk_Tesla_1_Minimum_Data` | `Rod_Blk_Tesla_1_Min_Data` | Tesla 1 Minimum |
| ... | ... | Tesla 2-4 variations |

#### 2. Inspection Measurements (60 mappings)
Maps columns from `database_data` to `rd05200200_inspection` table:

| Database Column | Target Column | Description |
|----------------|---------------|-------------|
| `Process_2_Rod_Blk_Inspection_1_Average_Data` | `Inspection_1_Average` | Inspection 1 Average |
| `Process_2_Rod_Blk_Inspection_1_Maximum_Data` | `Inspection_1_Maximum` | Inspection 1 Maximum |
| `Process_2_Rod_Blk_Inspection_1_Minimum_Data` | `Inspection_1_Minimum` | Inspection 1 Minimum |
| ... | ... | Inspections 2-20 variations |

## Enhanced Deviation Calculation

### 5-Tier Matching Strategy

The `calculate_rod_blk_deviations()` function uses a hierarchical approach:

1. **Priority Mapping** - Uses `ROD_BLK_COLUMN_MAPPING` dictionary
2. **Alternative Pattern Matching** - Handles variations (Avg vs Average)
3. **Tesla Fallback** - Regex-based Tesla column matching
4. **Inspection Fallback** - Regex-based Inspection column matching  
5. **Pattern-Based Fallback** - General pattern matching

### Example Usage

```python
# Database column from database_data table
db_column = "Process_2_Rod_Blk_Inspection_15_Average_Data"

# Gets mapped to inspection table column
target_column = "Inspection_15_Average"

# Deviation calculation
deviation = (database_average - inspection_value) / database_average
```

## New Features

### Coverage of New Columns
- **Inspections 11-20**: Added support for newly added inspection columns
- **Complete coverage**: All inspection types (Average, Maximum, Minimum)
- **Tesla measurements**: Full Tesla 1-4 coverage with all data types

### Improved Error Handling
- Clear success/failure indicators (✓/✗)
- Detailed logging of matching strategies used
- Alternative pattern matching for column name variations

### Consistent Behavior
- Follows memory guidelines for consistent query limits
- Maintains PASS_NG column preservation
- Compatible with existing material processing scripts

## Integration with Material Patterns

```python
material_patterns = {
    'Rod_Blk': {
        'prefix': 'Rod_Blk',
        'inspection_table': ['rdb5200200_checksheet', 'rd05200200_inspection'],
        'column_mapping': ROD_BLK_COLUMN_MAPPING  # New integration
    }
}
```

## Testing and Verification

### Test Scripts
- `test_rod_blk_mappings.py` - Verifies mapping dictionary structure
- `verify_column_mappings.py` - Validates against actual database schema

### Validation Checks
- Total mapping count verification
- Tesla vs Inspection categorization
- Coverage analysis of inspection numbers (1-20)
- Target column existence validation

## Maintenance

### Adding New Columns
1. Add mapping to `ROD_BLK_COLUMN_MAPPING` dictionary
2. Follow naming convention: `Process_2_Rod_Blk_[Type]_[Number]_[DataType]_Data`
3. Run test scripts to verify integration
4. Update documentation

### Troubleshooting
- Check database connectivity in `DB_CONFIG`
- Verify table names: `rdb5200200_checksheet`, `rd05200200_inspection`
- Ensure column names match exactly (case-sensitive)
- Review deviation calculation logs for mapping success/failure

## Performance Considerations
- Mapping dictionary lookup is O(1) operation
- Fallback strategies only used when primary mapping fails
- Reduced regex operations through priority mapping
- Enhanced logging provides debugging information without performance impact

## Compatibility
- Works with existing `main.py` integration
- Compatible with GUI dashboard (`tkinter_dashboard.py`)
- Maintains consistency with other material processing scripts
- Preserves Excel output format and structure
