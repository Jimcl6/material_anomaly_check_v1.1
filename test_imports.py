#!/usr/bin/env python3
"""
Test script to verify imports and basic functionality
"""

import os
import sys
import logging
import traceback

# Set up logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_imports.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_import(module_name):
    """Test importing a module and log the result"""
    try:
        module = __import__(module_name)
        logger.info(f"✅ Successfully imported {module_name}")
        logger.info(f"   Location: {getattr(module, '__file__', 'unknown')}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to import {module_name}")
        logger.error(f"   Error: {str(e)}")
        logger.error("   " + "\n   ".join(traceback.format_exc().split("\n")))
        return False

def main():
    logger.info("=" * 60)
    logger.info("Testing Material Anomaly Detection System Imports")
    logger.info("=" * 60)
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Test basic Python environment
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Script location: {os.path.abspath(__file__)}")
    
    # Test required modules
    required_modules = [
        'tkinter',
        'pandas',
        'numpy',
        'openpyxl',
        'mysql.connector',
        'watchdog',
        'sqlalchemy'
    ]
    
    # Test material modules
    material_modules = [
        'frame',
        'csb_data_output',
        'rod_blk_output',
        'em_material',
        'df_blk_output'
    ]
    
    logger.info("\nTesting required Python packages...")
    for module in required_modules:
        test_import(module)
    
    logger.info("\nTesting material processing modules...")
    for module in material_modules:
        test_import(module)
    
    logger.info("\nTest completed. Check the log file for details.")
    logger.info(f"Log file: {os.path.abspath(log_file)}")

if __name__ == "__main__":
    main()
