#!/usr/bin/env python3
"""
Simple test GUI for Material Anomaly Detection System
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import sys
import os

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_gui.log')

# Custom formatter that handles Unicode characters
class UnicodeFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)
        # Replace problematic characters with safe alternatives
        message = message.replace('✅', '[OK]')
        message = message.replace('❌', '[ERROR]')
        message = message.replace('⚠️', '[WARN]')
        return message

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# File handler with UTF-8 encoding
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setFormatter(UnicodeFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
root_logger.addHandler(file_handler)

# Console handler with safe encoding
console_handler = logging.StreamHandler()
console_handler.setFormatter(UnicodeFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)

class TestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Material Anomaly Test")
        self.root.geometry("600x400")
        
        # Main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="Material Anomaly Detection Test", 
            font=('Helvetica', 14, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Test buttons
        self.test_buttons = [
            ("Test Frame Module", self.test_frame_module),
            ("Test Database Connection", self.test_database_connection),
            ("Test CSV Reading", self.test_csv_reading),
            ("Show Logs", self.show_logs)
        ]
        
        for i, (text, command) in enumerate(self.test_buttons, 1):
            btn = ttk.Button(
                self.main_frame,
                text=text,
                command=command,
                width=30
            )
            btn.grid(row=i, column=0, pady=5, padx=10, sticky=tk.W)
        
        # Log display
        log_frame = ttk.LabelFrame(self.main_frame, text="Test Results", padding="5")
        log_frame.grid(row=1, column=1, rowspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, width=50, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            self.main_frame, 
            textvariable=self.status_var,
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        logger.info("Test GUI initialized successfully")
    
    def log_message(self, message, level="info"):
        """Add a message to the log display"""
        try:
            # Clean the message for display
            clean_message = (
                str(message)
                .replace('✅', '[OK]')
                .replace('❌', '[ERROR]')
                .replace('⚠️', '[WARN]')
            )
            
            self.log_text.insert(tk.END, f"{clean_message}\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
            
            # Log the original message with proper encoding
            if level.lower() == "error":
                logger.error(message)
            elif level.lower() == "warning":
                logger.warning(message)
            else:
                logger.info(message)
                
        except Exception as e:
            # Fallback logging if there's an encoding issue
            safe_message = str(message).encode('ascii', 'replace').decode('ascii')
            self.log_text.insert(tk.END, f"[LOG ERROR] {safe_message}\n")
            logger.error(f"Error in log_message: {str(e)}")
            logger.debug(f"Original message: {message}")
    
    def test_frame_module(self):
        """Test the frame module functionality"""
        self.log_message("Testing frame module...")
        try:
            import frame
            self.log_message("✅ Frame module imported successfully")
            
            # Test a simple function from frame module
            try:
                # Check if get_database_config exists
                if hasattr(frame, 'get_database_config'):
                    db_config = frame.get_database_config()
                    self.log_message("✅ Database configuration loaded successfully")
                    self.log_message(f"   Host: {db_config.get('host', 'Not found')}")
                    self.log_message(f"   Database: {db_config.get('database', 'Not found')}")
                    
                    # Test database connection
                    self.log_message("\nTesting database connection...")
                    try:
                        import mysql.connector
                        connection = mysql.connector.connect(**db_config)
                        if connection.is_connected():
                            db_info = connection.get_server_info()
                            self.log_message(f"✅ Connected to MySQL Server version {db_info}")
                            cursor = connection.cursor()
                            cursor.execute("SELECT DATABASE()")
                            db_name = cursor.fetchone()[0]
                            self.log_message(f"   Connected to database: {db_name}")
                            cursor.close()
                            connection.close()
                    except Exception as db_error:
                        self.log_message(f"❌ Database connection failed: {str(db_error)}", "error")
                else:
                    self.log_message("⚠️  get_database_config() not found in frame module", "warning")
                    
                # List available functions in frame module
                self.log_message("\nAvailable functions in frame module:")
                for func_name in dir(frame):
                    if not func_name.startswith('_') and callable(getattr(frame, func_name)):
                        self.log_message(f"   - {func_name}()")
                        
            except Exception as e:
                self.log_message(f"❌ Error accessing frame module functions: {str(e)}", "error")
                
        except Exception as e:
            self.log_message(f"❌ Error importing frame module: {str(e)}", "error")
    
    def test_database_connection(self):
        """Test database connection"""
        self.log_message("Testing database connection...")
        try:
            import mysql.connector
            from mysql.connector import Error
            
            # Get database config from frame module
            import frame
            db_config = frame.get_database_config()
            
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():
                db_info = connection.get_server_info()
                self.log_message(f"✅ Connected to MySQL Server version {db_info}")
                
                # Test a simple query
                cursor = connection.cursor()
                cursor.execute("SELECT DATABASE();")
                record = cursor.fetchone()
                self.log_message(f"   Connected to database: {record[0]}")
                
                cursor.close()
                connection.close()
                
        except Error as e:
            self.log_message(f"❌ Error connecting to MySQL: {str(e)}", "error")
    
    def test_csv_reading(self):
        """Test reading CSV files"""
        self.log_message("Testing CSV file reading...")
        try:
            import pandas as pd
            
            # Test reading a sample CSV file
            sample_file = os.path.join(os.path.dirname(__file__), "sample_data.csv")
            if os.path.exists(sample_file):
                df = pd.read_csv(sample_file)
                self.log_message(f"✅ Successfully read {len(df)} rows from {sample_file}")
                self.log_message(f"   Columns: {', '.join(df.columns)}")
            else:
                self.log_message("⚠️  Sample data file not found. Create a sample_data.csv for testing.", "warning")
                
        except Exception as e:
            self.log_message(f"❌ Error reading CSV file: {str(e)}", "error")
    
    def show_logs(self):
        """Show the contents of the log file"""
        log_file = os.path.join(os.path.dirname(__file__), "test_gui.log")
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = f.read()
                self.log_message("\n=== LOG FILE CONTENTS ===")
                self.log_text.insert(tk.END, logs)
                self.log_text.see(tk.END)
        else:
            self.log_message("Log file not found yet. Run some tests first.", "warning")

def main():
    try:
        # Log system information
        logger.info("=" * 60)
        logger.info("Starting Material Anomaly Test GUI")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Script location: {os.path.abspath(__file__)}")
        logger.info("-" * 60)
        
        # Check Python path
        logger.info("Python path:")
        for path in sys.path:
            logger.info(f"  {path}")
        
        # Create and run the GUI
        root = tk.Tk()
        app = TestGUI(root)
        root.mainloop()
        
    except ImportError as e:
        logger.critical(f"Import error: {str(e)}", exc_info=True)
        messagebox.showerror("Import Error", 
            f"Failed to import required modules:\n{str(e)}\n\n"
            "Please check that all dependencies are installed.\n"
            "Run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Fatal error in GUI: {str(e)}", exc_info=True)
        messagebox.showerror("Error", 
            f"A fatal error occurred:\n{str(e)}\n\n"
            f"Check {os.path.abspath(log_file)} for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
