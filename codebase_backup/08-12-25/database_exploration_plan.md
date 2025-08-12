# Database Schema Exploration Plan

## Problem Statement
The `get_process_dataframes()` function in lines 60-61 needs to extract material codes from database columns that follow patterns like:
- `Process_1_Em2p`
- `Process_1_Frame_Gasket`

## Database Exploration Steps

### 1. Connect to Database and List Tables
```sql
SHOW TABLES;
```

### 2. Examine Process Table Schemas
For each process table (process1_data, process2_data, etc.):
```sql
DESCRIBE process1_data;
DESCRIBE process2_data;
-- ... continue for all process tables
```

### 3. Sample Data Examination
```sql
SELECT * FROM process1_data LIMIT 5;
SELECT * FROM process2_data LIMIT 5;
-- ... continue for all process tables
```

### 4. Identify Column Patterns
Look for columns that contain material codes or follow the `Process_X_MaterialName` pattern.

## Expected Findings
Based on the Excel data patterns, we expect to find:
- Columns with material codes like: Em2p, Em3p, Frame, Rod_Blk, Df_Blk
- Possible patterns: `Process_{i}_{material_code}` or similar variations

## Solution Approach
Once we understand the schema:
1. Create a function to extract material codes from column names using regex
2. Modify the SQL query in `get_process_dataframes()` to dynamically select columns based on material patterns
3. Handle different material code formats (single word vs. compound like Frame_Gasket)

## Regex Patterns to Consider
- Extract material code: `Process_\d+_([A-Za-z_]+)`
- Handle compound materials: `Process_\d+_([A-Za-z]+(?:_[A-Za-z]+)*)`

## Next Steps
1. Switch to Code mode to implement database exploration script
2. Run the exploration and analyze results
3. Design and implement the solution based on findings