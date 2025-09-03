#!/usr/bin/env python3
"""
Test script to verify frame module functionality
"""

import os
import sys
import logging
import traceback

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_frame_module.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_frame_module():
    """Test the frame module functionality"""
    logger.info("=" * 60)
    logger.info("Testing frame module")
    logger.info("=" * 60)
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Test importing frame module
    try:
        logger.info("Importing frame module...")
        import frame
        logger.info("✅ Successfully imported frame module")
        logger.info(f"Module location: {os.path.abspath(frame.__file__)}")
        
        # Test getting database config
        if hasattr(frame, 'get_database_config'):
            logger.info("\nTesting get_database_config()...")
            try:
                db_config = frame.get_database_config()
                logger.info("✅ Successfully retrieved database configuration:")
                for key, value in db_config.items():
                    if 'password' in key.lower() and value:
                        logger.info(f"   {key}: {'*' * 8}")
                    else:
                        logger.info(f"   {key}: {value}")
                
                # Test database connection
                logger.info("\nTesting database connection...")
                try:
                    import mysql.connector
                    connection = mysql.connector.connect(**db_config)
                    if connection.is_connected():
                        db_info = connection.get_server_info()
                        logger.info(f"✅ Connected to MySQL Server version {db_info}")
                        
                        cursor = connection.cursor()
                        cursor.execute("SELECT DATABASE()")
                        db_name = cursor.fetchone()[0]
                        logger.info(f"   Connected to database: {db_name}")
                        
                        # Get table information
                        cursor.execute("""
                            SELECT TABLE_NAME, TABLE_ROWS 
                            FROM information_schema.tables 
                            WHERE table_schema = %s
                        """, (db_name,))
                        
                        logger.info("\nDatabase tables:")
                        for table_name, rows in cursor.fetchall():
                            logger.info(f"   {table_name}: {rows} rows")
                        
                        cursor.close()
                        connection.close()
                        logger.info("✅ Database connection closed")
                    
                except Exception as db_error:
                    logger.error(f"❌ Database connection failed: {str(db_error)}")
                    logger.debug(traceback.format_exc())
                
            except Exception as e:
                logger.error(f"❌ Error getting database config: {str(e)}")
                logger.debug(traceback.format_exc())
        else:
            logger.warning("get_database_config() not found in frame module")
        
        # List available functions in frame module
        logger.info("\nAvailable functions in frame module:")
        for func_name in dir(frame):
            if not func_name.startswith('_') and callable(getattr(frame, func_name)):
                logger.info(f"   - {func_name}()")
        
        # Test process_material_data function if it exists
        if hasattr(frame, 'process_material_data'):
            logger.info("\nTesting process_material_data()...")
            try:
                # You may need to modify these parameters based on your requirements
                result = frame.process_material_data()
                logger.info(f"✅ process_material_data() completed successfully")
                if isinstance(result, dict):
                    logger.info("Result keys:")
                    for key in result.keys():
                        logger.info(f"   - {key}")
                        if hasattr(result[key], 'shape'):  # If it's a pandas DataFrame
                            logger.info(f"     Shape: {result[key].shape}")
                else:
                    logger.info(f"Return type: {type(result)}")
            except Exception as e:
                logger.error(f"❌ Error in process_material_data(): {str(e)}")
                logger.debug(traceback.format_exc())
        
    except ImportError as e:
        logger.error(f"❌ Failed to import frame module: {str(e)}")
        logger.debug(traceback.format_exc())
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        logger.debug(traceback.format_exc())
        return False
    
    logger.info("\n✅ Frame module tests completed")
    return True

if __name__ == "__main__":
    test_frame_module()
