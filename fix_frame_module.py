#!/usr/bin/env python3
"""
Script to fix common issues in the frame module
"""

import os
import sys
import logging
import traceback

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fix_frame_module.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def add_database_config():
    """Add database configuration to frame.py if it doesn't exist"""
    frame_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frame.py')
    
    if not os.path.exists(frame_path):
        logger.error(f"frame.py not found at {frame_path}")
        return False
    
    try:
        with open(frame_path, 'r+', encoding='utf-8') as f:
            content = f.read()
            
            # Check if get_database_config already exists
            if 'def get_database_config' in content:
                logger.info("get_database_config() already exists in frame.py")
                return True
            
            # Find a good place to add the function (after imports)
            imports_end = content.find('\n\n')
            if imports_end == -1:
                imports_end = 0
            
            # Prepare the database config function
            db_config = """
# Database configuration
def get_database_config():
    """""Return database connection parameters"""
    return {
        'host': '192.168.2.148',
        'user': 'hpi.python',
        'password': 'hpi.python',
        'database': 'fc_1_data_db',
        'raise_on_warnings': True
    }
"""
            # Insert the function after imports
            new_content = (
                content[:imports_end] + 
                db_config + 
                content[imports_end:]
            )
            
            # Write the updated content back to the file
            f.seek(0)
            f.write(new_content)
            f.truncate()
            
            logger.info("✅ Successfully added get_database_config() to frame.py")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error updating frame.py: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def fix_process_material_data():
    """Add error handling to process_material_data"""
    frame_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frame.py')
    
    if not os.path.exists(frame_path):
        logger.error(f"frame.py not found at {frame_path}")
        return False
    
    try:
        with open(frame_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check if process_material_data exists
            if 'def process_material_data' not in content:
                logger.error("process_material_data() not found in frame.py")
                return False
                
            logger.info("process_material_data() found in frame.py")
            
            # Check if it already has proper error handling
            if 'try:' in content.split('def process_material_data', 1)[1]:
                logger.info("process_material_data() already has error handling")
                return True
            
            # Add error handling to the function
            func_start = content.find('def process_material_data')
            func_body_start = content.find(':', func_start) + 1
            func_body = content[func_body_start:]
            
            # Find the indentation level
            indent = ' ' * 4  # Default to 4 spaces
            for line in content[func_start:].split('\n')[1:]:
                if line.strip():
                    indent = ' ' * (len(line) - len(line.lstrip()))
                    break
            
            # Create the new function body with error handling
            new_func_body = f"""
{indent}try:
{indent*2}""" + '\n'.join(f"{indent*2}{line}" for line in func_body.strip().split('\n')) + f"""
{indent}except Exception as e:
{indent*2}import traceback
{indent*2}print(f"Error in process_material_data: {str(e)}")
{indent*2}traceback.print_exc()
{indent*2}return {{"error": str(e)}}"""
            
            # Replace the function body
            new_content = content[:func_body_start] + new_func_body
            
            # Write the updated content back to the file
            with open(frame_path, 'w', encoding='utf-8') as f_write:
                f_write.write(new_content)
            
            logger.info("✅ Successfully added error handling to process_material_data()")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error updating process_material_data(): {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def main():
    logger.info("=" * 60)
    logger.info("Fixing frame module issues")
    logger.info("=" * 60)
    
    # Add database configuration
    logger.info("\n1. Checking database configuration...")
    if add_database_config():
        logger.info("✅ Database configuration check complete")
    else:
        logger.error("❌ Failed to update database configuration")
    
    # Fix process_material_data function
    logger.info("\n2. Checking process_material_data()...")
    if fix_process_material_data():
        logger.info("✅ process_material_data() check complete")
    else:
        logger.error("❌ Failed to update process_material_data()")
    
    logger.info("\nFix process completed. Check the log file for details.")
    logger.info(f"Log file: {os.path.abspath(log_file)}")

if __name__ == "__main__":
    main()
