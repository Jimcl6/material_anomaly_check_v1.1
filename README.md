# Material Anomaly Check System

## Overview

This system correlates CSV file data with database material information to perform material anomaly checks and deviation calculations. It extracts specific material codes (Em2p, Em3p, Frame, Casing_Block, Df_Blk, Rod_Blk) from database process tables, relates them to the latest CSV entry using MODEL CODE and PROCESS S/N, and calculates deviations between inspection data and database averages.

## Problem Solved

The original `get_process_dataframes()` function had hardcoded column references that didn't exist in the database:
- Line 60: `MATERIAL_CODE AS Process_{i}_Material_Code` ❌
- Line 61: `Process_{i}_MATERIAL_CODE_Lot_No AS Process_{i}_Lot_No` ❌
- Line 62: `Process_{i}_material_Model_Code AS Process_{i}_material_Model_Code` ❌

**Root Cause**: Material codes are embedded in column names like `Process_1_Em2p`, `Process_2_Rod_Blk`, `Process_3_Frame_Gasket`, etc.

## Solution Architecture

### 1. Dynamic Material Detection
- **Function**: `get_material_columns_from_table()`
- **Purpose**: Automatically discovers material columns using regex patterns
- **Pattern**: `Process_X_MaterialName` (excluding standard columns)
- **Handles**: Simple names (Em2p) and compound names (Frame_Gasket)

### 2. Flexible Material Extraction
- **Function**: `get_process_dataframes()`
- **Default Materials**: Em2p, Em3p, Frame, Casing_Block, Df_Blk, Rod_Blk
- **Features**: 
  - Dynamic column detection
  - Automatic lot number pairing
  - Case-insensitive material matching
  - Configurable material filtering

### 3. CSV-Database Correlation
- **Function**: `correlate_csv_with_database_materials()`
- **Purpose**: Match latest CSV row with database records
- **Matching Criteria**: MODEL CODE + PROCESS S/N
- **Output**: Material information for matching records

### 4. Complete Workflow
- **Function**: `get_material_summary_for_csv_entry()`
- **Purpose**: End-to-end material analysis for CSV entry
- **Features**: Aggregated results, detailed reporting, error handling

## Database Structure

### Process Tables
- `process1_data`: Em2p, Em3p, Frame, Harness, Bushing
- `process2_data`: Rod_Blk, Df_Blk, M4x40_Screw, Df_Ring, Washer, Lock_Nut
- `process3_data`: Casing_Block, Frame_Gasket, Casing_Gasket, etc.
- `process4_data`: Tank, Upper_Housing, Cord_Hook, etc.
- `process5_data`: Rating_Label
- `process6_data`: Vinyl

### Required Materials Distribution
- **Process 1**: Em2p, Em3p, Frame
- **Process 2**: Df_Blk, Rod_Blk  
- **Process 3**: Casing_Block
- **Process 4-6**: None of the required materials

## Usage Examples

### Basic Usage
```python
from main import get_process_dataframes, DB_CONFIG

# Get data for required materials (default behavior)
process_dfs = get_process_dataframes(DB_CONFIG)
```

### CSV Correlation
```python
from main import get_material_summary_for_csv_entry, load_csv

# Load CSV and correlate with database
csv_df = load_csv("path/to/file.csv")
summary = get_material_summary_for_csv_entry(csv_df, DB_CONFIG)
```

### Custom Material Selection
```python
# Get specific materials only
custom_materials = ['Em2p', 'Frame']
process_dfs = get_process_dataframes(DB_CONFIG, specific_materials=custom_materials)

# Get all available materials
all_materials = get_process_dataframes(DB_CONFIG, specific_materials=[])
```

## File Structure

```
jed_material_anomaly_check/
├── main.py                      # Main GUI implementation
├── frame.py                     # Frame material processing
├── em_material.py               # Em2p/Em3p material processing  
├── csb_data_output.py           # Casing Block material processing
├── df_blk_output.py             # Df Block material processing
├── rod_blk_output.py            # Rod Block material processing
├── tkinter_dashboard.py         # GUI dashboard interface
├── test_*.py                    # Various testing scripts
├── explore_database_schema.py   # Database exploration utility
├── database_exploration_plan.md # Planning document
└── README.md                    # This documentation
```

## Key Functions

### `get_process_dataframes(db_config, num_processes=6, specific_materials=None)`
- **Purpose**: Extract material data from database process tables
- **Default**: Returns Em2p, Em3p, Frame, Casing_Block, Df_Blk, Rod_Blk
- **Returns**: Dictionary of DataFrames keyed by process number

### `correlate_csv_with_database_materials(csv_df, process_dfs)`
- **Purpose**: Match CSV entry with database materials
- **Input**: CSV DataFrame and process DataFrames
- **Returns**: Correlation results with material details

### `get_material_summary_for_csv_entry(csv_df, db_config)`
- **Purpose**: Complete workflow for material analysis
- **Input**: CSV DataFrame and database config
- **Returns**: Comprehensive material summary

## Testing

### Test Scripts
1. **`test_correlation.py`**: Tests correlation with sample data
2. **`test_specific_materials.py`**: Tests material extraction
3. **`main.py`**: Full workflow demonstration

### Sample Test Results
```
Latest CSV Entry: MODEL CODE = 60CAT0213P, PROCESS S/N = 4

PROCESS_1 CORRELATION: ✅ Found 1 matching record(s)
  Em2p: ['EM0580106P'] (Lot: ['CAT-4G03DI'])
  Em3p: ['EM0580107P'] (Lot: ['CAT-4G10DI'])
  Frame: ['FM05000102-01A'] (Lot: ['072324A-40'])

PROCESS_2 CORRELATION: ✅ Found 1 matching record(s)
  Df_Blk: ['DFB6600600'] (Lot: ['20240809-A'])
  Rod_Blk: ['RDB5200200'] (Lot: ['20240805-B'])
```

## Configuration

### Database Configuration
```python
DB_CONFIG = {
    'host': '192.168.2.148',
    'user': 'hpi.python',
    'password': 'hpi.python',
    'database': 'fc_1_data_db'
}
```

### CSV File Configuration
```python
NETWORK_DIR = r"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled"
FILENAME = f"PICompiled{x.year}-{x.strftime("%m")}-{x.strftime('%d')}.csv
# FILENAME = "PICompiled2025-08-20.csv"
```

## Error Handling

The system handles:
- Missing CSV files
- Database connection timeouts
- Empty datasets
- Missing material columns
- No matching records

## Performance

- **Database Records**: ~33,916 total records across 3 process tables
- **Material Extraction**: Dynamic detection with regex patterns
- **Memory Efficient**: Only loads required materials by default
- **Scalable**: Supports additional processes and materials

## Build and Deployment

### Building the Executable

#### Using build_local.bat (Recommended)
1. Run `build_local.bat` as administrator
2. The script will:
   - Create a temporary local directory
   - Copy all necessary files
   - Install required dependencies
   - Build the executable using PyInstaller
   - Copy the final `MaterialAnomalyDetector.exe` to the project directory
   - Clean up temporary files

#### Manual Build
```bash
# Install required packages
pip install -r requirements.txt

# Build the executable
pyinstaller --noconfirm --onefile --windowed \
    --name "MaterialAnomalyDetector" \
    --icon=icon.ico \
    --add-data "material_anomaly.log;." \
    --add-data "*.xlsx;." \
    --hidden-import=tkinter \
    --hidden-import=pandas \
    --hidden-import=openpyxl \
    --hidden-import=mysql.connector \
    --hidden-import=sqlalchemy \
    --hidden-import=matplotlib \
    --hidden-import=PIL \
    main.py
```

## Recent Updates (September 2025)

### 1. Executable Build System
- Added `build_local.bat` for reliable executable creation
- Created `material_anomaly.spec` for PyInstaller configuration
- Added comprehensive error handling for build process
- Included all necessary data files in the build

### 2. Debugging and Testing
- Added `debug_frame.py` for troubleshooting frame module
- Implemented detailed logging in `material_anomaly.log`
- Created test scripts for module verification
- Added error handling for missing CSV files

### 3. Performance Optimizations
- Improved database query performance
- Optimized memory usage during material processing
- Added batch processing for large datasets
- Implemented connection pooling for database access

### 4. User Interface Improvements
- Enhanced error messages and logging
- Added progress indicators for long-running operations
- Improved data validation and error recovery
- Added tooltips and help text

### 5. Documentation
- Updated README with build instructions
- Added EXE_BUILD_INSTRUCTIONS.md
- Documented all new features and changes
- Added troubleshooting section

### 5. Material Processing Enhancements
- **Individual material files** for specialized processing
- **Excel output generation** with material-specific sheets
- **Deviation calculations** between inspection data and database averages
- **GUI integration** through tkinter dashboard

## System Architecture

### Material Processing Files
- **`frame.py`**: Frame material deviation analysis
- **`em_material.py`**: Em2p/Em3p material processing
- **`csb_data_output.py`**: Casing Block material analysis  
- **`df_blk_output.py`**: Df Block material processing
- **`rod_blk_output.py`**: Rod Block material analysis

### Key Features
- **Automated deviation calculations**
- **Excel report generation**
- **Database correlation with inspection data**
- **Keyword-based data filtering**
- **GUI dashboard interface**

## Future Enhancements

1. **Anomaly Detection**: Compare expected vs actual materials
2. **Historical Analysis**: Track material changes over time
3. **Alert System**: Notify on material discrepancies
4. **Batch Processing**: Handle multiple CSV entries
5. **Export Features**: Generate reports in various formats