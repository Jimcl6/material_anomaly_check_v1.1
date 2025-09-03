#!/usr/bin/env python3
"""
Debug script for frame module
"""

import os
import sys
import logging
import traceback
import importlib

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'debug_frame.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_frame_import():
    """Test importing the frame module"""
    logger.info("=" * 60)
    logger.info("Testing frame module import")
    logger.info("=" * 60)
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        # Try to import frame
        logger.info("Attempting to import frame module...")
        frame = importlib.import_module('frame')
        logger.info("✅ Successfully imported frame module")
        logger.info(f"Module location: {os.path.abspath(frame.__file__)}")
        return frame
    except Exception as e:
        logger.error(f"❌ Failed to import frame module: {str(e)}")
        logger.debug(traceback.format_exc())
        return None

def test_database_connection(frame_module):
    """Test database connection using frame module"""
    if not frame_module:
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Testing database connection")
    logger.info("=" * 60)
    
    try:
        # Try to create a database connection
        if hasattr(frame_module, 'create_db_connection'):
            logger.info("Found create_db_connection() function")
            
            # Try to connect (frame.py's create_db_connection doesn't take parameters)
            logger.info("Attempting to create database connection...")
            connection = frame_module.create_db_connection()
            
            if connection and hasattr(connection, 'is_connected') and connection.is_connected():
                logger.info("✅ Successfully connected to database")
                
                # Get database info
                cursor = connection.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                logger.info(f"Database version: {version[0] if version else 'Unknown'}")
                
                cursor.close()
                connection.close()
                logger.info("Database connection closed")
                return True
            else:
                logger.error("❌ Failed to connect to database")
                return False
                
        else:
            logger.error("create_db_connection() not found in frame module")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def test_process_material_data(frame_module):
    """Test process_material_data function with detailed logging"""
    if not frame_module:
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Testing process_material_data()")
    logger.info("=" * 60)
    
    try:
        if not hasattr(frame_module, 'process_material_data'):
            logger.error("process_material_data() not found in frame module")
            return False
            
        logger.info("Calling process_material_data()...")
        
        # Log environment variables that might affect the function
        logger.info("Environment variables:")
        logger.info(f"  FILEPATH: {getattr(frame_module, 'FILEPATH', 'Not set')}")
        logger.info(f"  NETWORK_DIR: {getattr(frame_module, 'NETWORK_DIR', 'Not set')}")
        
        # Get the most recent CSV file
        import glob
        csv_files = glob.glob(os.path.join(frame_module.NETWORK_DIR, 'PICompiled*.csv'))
        if not csv_files:
            logger.error(f"No CSV files found in {frame_module.NETWORK_DIR}")
            return False
            
        # Sort files by modification time (newest first)
        latest_csv = max(csv_files, key=os.path.getmtime)
        logger.info(f"Using latest CSV file: {latest_csv}")
        
        # Update the FILEPATH to use the latest CSV
        frame_module.FILEPATH = latest_csv
        
        # Call the function
        result = frame_module.process_material_data()
        
        if result is None:
            logger.warning("process_material_data() returned None")
            
            # Check if CSV file exists
            filepath = getattr(frame_module, 'FILEPATH', '')
            if not os.path.exists(filepath):
                logger.error(f"CSV file not found: {filepath}")
            else:
                logger.info(f"CSV file exists: {filepath} (Size: {os.path.getsize(filepath)} bytes)")
                
                # Try to read the CSV file directly
                try:
                    df = pd.read_csv(filepath)
                    logger.info(f"Successfully read CSV file. Shape: {df.shape}")
                    logger.info(f"Columns: {list(df.columns)}")
                    logger.info(f"First few rows:\n{df.head(2).to_string()}")
                except Exception as e:
                    logger.error(f"Failed to read CSV file: {str(e)}")
            
            return False
            
        logger.info(f"process_material_data() returned: {type(result)}")
        
        if isinstance(result, dict):
            logger.info("Result keys:")
            for key, value in result.items():
                if value is None:
                    logger.info(f"  - {key}: None")
                elif hasattr(value, 'shape'):  # If it's a pandas DataFrame
                    logger.info(f"  - {key}: DataFrame with shape {value.shape}")
                    if not value.empty:
                        logger.info(f"    First few rows:\n{value.head(2).to_string()}")
                elif isinstance(value, dict):
                    logger.info(f"  - {key}: Dictionary with {len(value)} items")
                    # Log first few items
                    for k, v in list(value.items())[:3]:
                        logger.info(f"    {k}: {str(v)[:100]}...")
                else:
                    logger.info(f"  - {key}: {type(value).__name__} (value: {str(value)[:100]}...)")
        
        # Check if we have the expected data
        if not result.get('process_data') is None:
            logger.warning("No process_data in results")
            
        if not result.get('inspection_data') is None:
            logger.warning("No inspection_data in results")
            
        if not result.get('deviation_data') is None:
            logger.warning("No deviation_data in results")
        
        return True
            
    except Exception as e:
        logger.error(f"❌ process_material_data() test failed: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("Debugging frame module")
    logger.info("=" * 60)
    
    # Test importing the frame module
    frame_module = test_frame_import()
    
    if frame_module:
        # Test database connection
        db_ok = test_database_connection(frame_module)
        
        # Test process_material_data
        if db_ok:
            test_process_material_data(frame_module)
    
    logger.info("\nDebugging complete. Check the log file for details.")
    logger.info(f"Log file: {os.path.abspath(log_file)}")

if __name__ == "__main__":
    main()
