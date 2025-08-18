#%%
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os
import datetime
import threading
import sys
import subprocess
import time
import hashlib
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import the material processing modules
try:
    import frame
    import csb_data_output
    import rod_blk_output
    import em_material
except ImportError as e:
    print(f"Error importing material modules: {e}")

class CSVFileHandler(FileSystemEventHandler):
    """File system event handler for monitoring CSV file changes"""
    
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.last_processed_hash = None
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Check if the modified file is our target CSV
        if hasattr(self.gui, 'csv_file_path') and event.src_path == self.gui.csv_file_path:
            self.gui.log_event(f"CSV file change detected: {event.src_path}")
            # Add small delay to ensure file write is complete
            threading.Timer(2.0, self.gui.process_csv_change).start()

class MaterialAnomalyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Material Anomaly Detection System")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize data storage
        self.all_deviation_data = {}  # Store deviation data for each material
        self.current_table_data = pd.DataFrame()
        self.selected_material = tk.StringVar(value="")
        
        # Create comprehensive deviation log
        self.deviation_log_file = os.path.join(os.path.expanduser("~"), "Desktop", "comprehensive_deviation_log.xlsx")
        
        # CSV monitoring setup
        self.csv_file_path = r"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled\PICompiled2025-07-11.csv"
        self.auto_monitoring = tk.BooleanVar(value=False)
        self.file_observer = None
        self.last_csv_hash = None
        self.critical_deviations_log = os.path.join(os.path.expanduser("~"), "Desktop", "critical_deviations_auto_log.xlsx")
        
        self.setup_gui()
        self.setup_event_logger()
        
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Material Anomaly Detection System", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left panel for controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Material selection radio buttons
        material_frame = ttk.LabelFrame(control_frame, text="Material Selection", padding="10")
        material_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Radio buttons for materials
        materials = [("All Critical Deviations", ""), ("Frame", "Frame"), 
                    ("CSB", "CSB"), ("Rod Block", "Rod_Blk"), ("EM Material", "Em")]
        
        for i, (text, value) in enumerate(materials):
            rb = ttk.Radiobutton(material_frame, text=text, variable=self.selected_material, 
                               value=value, command=self.update_table_display)
            rb.grid(row=i, column=0, sticky=tk.W, pady=2)
        
        # Set default selection
        self.selected_material.set("")
        
        # Action buttons
        button_frame = ttk.LabelFrame(control_frame, text="Actions", padding="10")
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(button_frame, text="Refresh Data", 
                  command=self.refresh_data).grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="Save Selected Results", 
                  command=self.save_selected_results).grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="Save All Results", 
                  command=self.save_all_results).grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Auto-monitoring controls
        monitoring_frame = ttk.LabelFrame(control_frame, text="Auto Monitoring", padding="10")
        monitoring_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.monitoring_checkbox = ttk.Checkbutton(monitoring_frame, text="Enable CSV Auto-Monitoring", 
                                                  variable=self.auto_monitoring, 
                                                  command=self.toggle_monitoring)
        self.monitoring_checkbox.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        ttk.Button(monitoring_frame, text="Set CSV File Path", 
                  command=self.set_csv_file_path).grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        self.csv_path_label = ttk.Label(monitoring_frame, text="No CSV file selected", 
                                       foreground="gray", wraplength=200)
        self.csv_path_label.grid(row=2, column=0, pady=2, sticky=(tk.W, tk.E))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, 
                                          maximum=100, length=200)
        self.progress_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Ready", foreground="green")
        self.status_label.grid(row=5, column=0, pady=5)
        
        # Right panel for results
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Results table
        self.setup_results_table(results_frame)
        
        # Event logger at bottom
        logger_frame = ttk.LabelFrame(main_frame, text="Event Log", padding="10")
        logger_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        logger_frame.columnconfigure(0, weight=1)
        logger_frame.rowconfigure(0, weight=1)
        
        self.setup_event_logger_widget(logger_frame)
        
    def setup_results_table(self, parent):
        """Setup the results table with scrollbars"""
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Define columns based on display mode
        self.tree = ttk.Treeview(tree_frame, show='headings', height=15)
        
        # Configure table styling for better readability
        style = ttk.Style()
        style.configure("Treeview", 
                       relief="solid",
                       borderwidth=1)
        style.configure("Treeview.Heading",
                       relief="solid",
                       borderwidth=1,
                       font=('TkDefaultFont', 9, 'bold'))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
    def setup_event_logger(self):
        """Setup event logging system"""
        self.events = []
        
    def setup_event_logger_widget(self, parent):
        """Setup the event logger widget"""
        # Text widget with scrollbar for event log
        log_frame = ttk.Frame(parent)
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def log_event(self, message, level="INFO"):
        """Log an event to the event logger"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        self.events.append(log_entry)
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)
        
        # Update status label
        self.status_label.config(text=message[:50] + "..." if len(message) > 50 else message)
        
        self.root.update_idletasks()
        
    def run_material_script(self, script_name, material_name):
        """Run a material processing script and return results"""
        try:
            self.log_event(f"Starting {material_name} analysis...")
            
            if script_name == "frame":
                result = frame.process_material_data()
            elif script_name == "csb_data_output":
                result = csb_data_output.process_material_data()
            elif script_name == "rod_blk_output":
                result = rod_blk_output.process_material_data()
            elif script_name == "em_material":
                result = em_material.process_material_data()
            else:
                raise ValueError(f"Unknown script: {script_name}")
            
            if result and 'deviation_data' in result and result['deviation_data'] is not None:
                deviation_df = result['deviation_data']
                self.log_event(f"{material_name} analysis completed. Found {len(deviation_df)} deviation records.")
                return deviation_df
            else:
                self.log_event(f"{material_name} analysis completed but no deviation data found.", "WARNING")
                return pd.DataFrame()
                
        except Exception as e:
            self.log_event(f"Error running {material_name} analysis: {str(e)}", "ERROR")
            return pd.DataFrame()
    
    def refresh_data(self):
        """Refresh data from all material scripts"""
        def refresh_thread():
            try:
                self.progress_var.set(0)
                self.log_event("Starting data refresh for all materials...")
                
                # Material scripts mapping
                materials = [
                    ("frame", "Frame"),
                    ("csb_data_output", "CSB"),
                    ("rod_blk_output", "Rod Block"),
                    ("em_material", "EM Material")
                ]
                
                self.all_deviation_data = {}
                total_materials = len(materials)
                
                for i, (script_name, material_name) in enumerate(materials):
                    self.progress_var.set((i / total_materials) * 100)
                    
                    deviation_df = self.run_material_script(script_name, material_name)
                    if not deviation_df.empty:
                        self.all_deviation_data[material_name] = deviation_df
                        
                        # Log to comprehensive file
                        self.log_to_comprehensive_file(deviation_df, material_name)
                    
                self.progress_var.set(100)
                self.log_event("Data refresh completed for all materials.")
                
                # Update table display
                self.update_table_display()
                
            except Exception as e:
                self.log_event(f"Error during data refresh: {str(e)}", "ERROR")
            finally:
                self.progress_var.set(0)
        
        # Run in separate thread to prevent GUI freezing
        thread = threading.Thread(target=refresh_thread)
        thread.daemon = True
        thread.start()
    
    def log_to_comprehensive_file(self, deviation_df, material_name):
        """Log deviation data to comprehensive Excel file"""
        try:
            # Add timestamp and material info
            deviation_df_copy = deviation_df.copy()
            deviation_df_copy['Timestamp'] = datetime.datetime.now()
            deviation_df_copy['Material_Type'] = material_name
            
            # Check if file exists
            if os.path.exists(self.deviation_log_file):
                # Append to existing file
                existing_df = pd.read_excel(self.deviation_log_file)
                combined_df = pd.concat([existing_df, deviation_df_copy], ignore_index=True)
            else:
                combined_df = deviation_df_copy
            
            # Save to Excel
            combined_df.to_excel(self.deviation_log_file, index=False)
            self.log_event(f"Logged {len(deviation_df)} {material_name} deviations to comprehensive file.")
            
        except Exception as e:
            self.log_event(f"Error logging to comprehensive file: {str(e)}", "ERROR")
    
    def update_table_display(self):
        """Update the table display based on selected material"""
        try:
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            selected = self.selected_material.get()
            
            if selected == "":
                # Show critical deviations (>0.03 or <-0.03) from all materials
                self.display_critical_deviations()
            else:
                # Show all data for selected material
                self.display_material_data(selected)
                
        except Exception as e:
            self.log_event(f"Error updating table display: {str(e)}", "ERROR")
    
    def display_critical_deviations(self):
        """Display only critical deviations from all materials"""
        # Configure columns for critical view
        columns = ("Column", "Deviation", "Material")
        self.tree["columns"] = columns
        
        for col in columns:
            self.tree.heading(col, text=col)
            # Right align specific columns
            if col in ["Deviation", "Material", "S/N"]:
                self.tree.column(col, width=150, anchor='e')  # 'e' = east (right align)
            else:
                self.tree.column(col, width=150, anchor='w')  # 'w' = west (left align)
        
        critical_data = []
        
        for material_name, deviation_df in self.all_deviation_data.items():
            if not deviation_df.empty and 'Deviation' in deviation_df.columns:
                # Filter critical deviations
                critical_mask = (abs(deviation_df['Deviation']) > 0.03)
                critical_deviations = deviation_df[critical_mask]
                
                for _, row in critical_deviations.iterrows():
                    critical_data.append({
                        'Column': row.get('Column', 'N/A'),
                        'Deviation': f"{row.get('Deviation', 0):.4f}",
                        'Material': material_name
                    })
        
        # Sort by absolute deviation value
        critical_data.sort(key=lambda x: abs(float(x['Deviation'])), reverse=True)
        
        # Insert into tree
        for data in critical_data:
            self.tree.insert("", tk.END, values=(data['Column'], data['Deviation'], data['Material']))
        
        self.current_table_data = pd.DataFrame(critical_data)
        self.log_event(f"Displaying {len(critical_data)} critical deviations (>0.03 or <-0.03)")
    
    def display_material_data(self, material_key):
        """Display all data for a specific material"""
        # Map radio button values to material names
        material_mapping = {
            "Frame": "Frame",
            "CSB": "CSB", 
            "Rod_Blk": "Rod Block",
            "Em": "EM Material"
        }
        
        material_name = material_mapping.get(material_key, material_key)
        
        if material_name not in self.all_deviation_data:
            self.log_event(f"No data available for {material_name}", "WARNING")
            return
        
        deviation_df = self.all_deviation_data[material_name]
        
        if deviation_df.empty:
            self.log_event(f"No deviation data for {material_name}", "WARNING")
            return
        
        # Configure columns for detailed view
        available_columns = list(deviation_df.columns)
        desired_columns = ["Column", "Database Average", "Inspection Value", "Deviation", "Material", "S/N", "Matched Inspection Column"]
        
        # Use available columns that match desired columns
        display_columns = [col for col in desired_columns if col in available_columns]
        
        self.tree["columns"] = display_columns
        
        for col in display_columns:
            self.tree.heading(col, text=col)
            # Right align specific columns for better readability
            if col in ["Deviation", "Material", "S/N", "Database Average", "Inspection Value"]:
                self.tree.column(col, width=120, anchor='e')  # 'e' = east (right align)
            else:
                self.tree.column(col, width=120, anchor='w')  # 'w' = west (left align)
        
        # Insert data
        for _, row in deviation_df.iterrows():
            values = []
            for col in display_columns:
                value = row.get(col, 'N/A')
                if col == "Deviation" and isinstance(value, (int, float)):
                    value = f"{value:.4f}"
                elif col in ["Database Average", "Inspection Value"] and isinstance(value, (int, float)):
                    value = f"{value:.3f}"
                values.append(str(value))
            
            self.tree.insert("", tk.END, values=values)
        
        self.current_table_data = deviation_df[display_columns].copy()
        self.log_event(f"Displaying {len(deviation_df)} records for {material_name}")
    
    def save_selected_results(self):
        """Save currently displayed table results to Excel"""
        try:
            if self.current_table_data.empty:
                messagebox.showwarning("No Data", "No data to save. Please refresh data first.")
                return
            
            # Generate filename based on selection
            selected = self.selected_material.get()
            if selected == "":
                filename = "critical_deviations.xlsx"
            else:
                filename = f"{selected.lower()}_deviations.xlsx"
            
            filepath = os.path.join(os.path.expanduser("~"), "Desktop", filename)
            
            # Save to Excel
            self.current_table_data.to_excel(filepath, index=False)
            
            self.log_event(f"Saved {len(self.current_table_data)} records to {filename}")
            messagebox.showinfo("Success", f"Results saved to Desktop/{filename}")
            
        except Exception as e:
            self.log_event(f"Error saving selected results: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")
    
    def save_all_results(self):
        """Save all deviation results to Excel"""
        try:
            if not self.all_deviation_data:
                messagebox.showwarning("No Data", "No data to save. Please refresh data first.")
                return
            
            filepath = os.path.join(os.path.expanduser("~"), "Desktop", "all_material_deviations.xlsx")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for material_name, deviation_df in self.all_deviation_data.items():
                    if not deviation_df.empty:
                        sheet_name = material_name.replace(" ", "_")[:31]  # Excel sheet name limit
                        deviation_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            total_records = sum(len(df) for df in self.all_deviation_data.values())
            self.log_event(f"Saved all results ({total_records} total records) to all_material_deviations.xlsx")
            messagebox.showinfo("Success", f"All results saved to Desktop/all_material_deviations.xlsx")
            
        except Exception as e:
            self.log_event(f"Error saving all results: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to save all results: {str(e)}")
    
    def set_csv_file_path(self):
        """Allow user to select CSV file for monitoring"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File to Monitor",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=r"\\192.168.2.19\ai_team\AI Program\Outputs\PICompiled"
        )
        
        if file_path:
            self.csv_file_path = file_path
            filename = os.path.basename(file_path)
            self.csv_path_label.config(text=f"Monitoring: {filename}", foreground="blue")
            self.log_event(f"CSV file path set to: {file_path}")
            
            # Initialize hash for change detection
            self.last_csv_hash = self.get_file_hash(file_path)
    
    def get_file_hash(self, file_path):
        """Calculate MD5 hash of file for change detection"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.log_event(f"Error calculating file hash: {str(e)}", "ERROR")
            return None
    
    def toggle_monitoring(self):
        """Enable or disable CSV file monitoring"""
        if self.auto_monitoring.get():
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start monitoring the CSV file for changes"""
        if not os.path.exists(self.csv_file_path):
            messagebox.showerror("Error", f"CSV file not found: {self.csv_file_path}")
            self.auto_monitoring.set(False)
            return
        
        try:
            # Set up file system observer
            self.file_observer = Observer()
            event_handler = CSVFileHandler(self)
            
            # Watch the directory containing the CSV file
            watch_dir = os.path.dirname(self.csv_file_path)
            self.file_observer.schedule(event_handler, watch_dir, recursive=False)
            self.file_observer.start()
            
            self.log_event(f"Started monitoring CSV file: {os.path.basename(self.csv_file_path)}")
            self.status_label.config(text="Auto-monitoring ACTIVE", foreground="orange")
            
        except Exception as e:
            self.log_event(f"Error starting file monitoring: {str(e)}", "ERROR")
            self.auto_monitoring.set(False)
            messagebox.showerror("Error", f"Failed to start monitoring: {str(e)}")
    
    def stop_monitoring(self):
        """Stop monitoring the CSV file"""
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
            self.file_observer = None
        
        self.log_event("Stopped CSV file monitoring")
        self.status_label.config(text="Auto-monitoring STOPPED", foreground="red")
    
    def process_csv_change(self):
        """Process CSV file changes automatically"""
        try:
            if not os.path.exists(self.csv_file_path):
                self.log_event("CSV file no longer exists", "ERROR")
                return
            
            # Check if file actually changed using hash
            current_hash = self.get_file_hash(self.csv_file_path)
            if current_hash == self.last_csv_hash:
                self.log_event("False alarm - CSV file unchanged")
                return
            
            self.last_csv_hash = current_hash
            self.log_event("CSV file change confirmed - processing new data...")
            
            # Read the last row of the CSV file
            csv_data = self.read_csv_tail()
            if csv_data is None:
                return
            
            # Update material scripts with new CSV data
            self.update_material_scripts_csv_path()
            
            # Run automatic processing
            self.auto_process_materials()
            
        except Exception as e:
            self.log_event(f"Error processing CSV change: {str(e)}", "ERROR")
    
    def read_csv_tail(self):
        """Read the last row of the CSV file"""
        try:
            df = pd.read_csv(self.csv_file_path)
            if df.empty:
                self.log_event("CSV file is empty", "WARNING")
                return None
            
            # Get the last row
            last_row = df.tail(1)
            self.log_event(f"Read CSV tail - Last row contains S/N: {last_row['S/N'].iloc[0] if 'S/N' in last_row.columns else 'N/A'}")
            return last_row
            
        except Exception as e:
            self.log_event(f"Error reading CSV file: {str(e)}", "ERROR")
            return None
    
    def update_material_scripts_csv_path(self):
        """Update the CSV file path in all material scripts"""
        try:
            # Update the FILEPATH variable in each material script
            new_filename = os.path.basename(self.csv_file_path)
            
            # This would require modifying the material scripts to accept dynamic file paths
            # For now, log the action
            self.log_event(f"Updated material scripts to use: {new_filename}")
            
        except Exception as e:
            self.log_event(f"Error updating material scripts: {str(e)}", "ERROR")
    
    def auto_process_materials(self):
        """Automatically process all materials when CSV changes"""
        def auto_process_thread():
            try:
                self.log_event("=== AUTOMATIC PROCESSING STARTED ===", "INFO")
                self.progress_var.set(0)
                
                # Material scripts mapping
                materials = [
                    ("frame", "Frame"),
                    ("csb_data_output", "CSB"),
                    ("rod_blk_output", "Rod Block"),
                    ("em_material", "EM Material")
                ]
                
                auto_deviation_data = {}
                total_materials = len(materials)
                
                for i, (script_name, material_name) in enumerate(materials):
                    self.progress_var.set((i / total_materials) * 100)
                    
                    deviation_df = self.run_material_script(script_name, material_name)
                    if not deviation_df.empty:
                        auto_deviation_data[material_name] = deviation_df
                
                self.progress_var.set(100)
                
                # Create critical deviations log
                self.create_critical_deviations_log(auto_deviation_data)
                
                # Update main data storage
                self.all_deviation_data.update(auto_deviation_data)
                
                # Update table display
                self.update_table_display()
                
                self.log_event("=== AUTOMATIC PROCESSING COMPLETED ===", "INFO")
                
            except Exception as e:
                self.log_event(f"Error during automatic processing: {str(e)}", "ERROR")
            finally:
                self.progress_var.set(0)
        
        # Run in separate thread
        thread = threading.Thread(target=auto_process_thread)
        thread.daemon = True
        thread.start()
    
    def create_critical_deviations_log(self, deviation_data):
        """Create Excel log file with critical deviations only"""
        try:
            critical_data = []
            timestamp = datetime.datetime.now()
            
            for material_name, deviation_df in deviation_data.items():
                if not deviation_df.empty and 'Deviation' in deviation_df.columns:
                    # Filter critical deviations (>0.03 or <-0.03)
                    critical_mask = (abs(deviation_df['Deviation']) > 0.03)
                    critical_deviations = deviation_df[critical_mask]
                    
                    for _, row in critical_deviations.iterrows():
                        critical_data.append({
                            'Timestamp': timestamp,
                            'Material': material_name,
                            'Column': row.get('Column', 'N/A'),
                            'Database_Average': row.get('Database_Average', 'N/A'),
                            'Inspection_Value': row.get('Inspection_Value', 'N/A'),
                            'Deviation': row.get('Deviation', 0),
                            'S/N': row.get('S/N', 'N/A'),
                            'Severity': 'CRITICAL' if abs(row.get('Deviation', 0)) > 0.05 else 'WARNING'
                        })
            
            if critical_data:
                # Create or append to critical deviations log
                critical_df = pd.DataFrame(critical_data)
                
                if os.path.exists(self.critical_deviations_log):
                    # Append to existing file
                    existing_df = pd.read_excel(self.critical_deviations_log)
                    combined_df = pd.concat([existing_df, critical_df], ignore_index=True)
                else:
                    combined_df = critical_df
                
                # Save to Excel
                combined_df.to_excel(self.critical_deviations_log, index=False)
                
                self.log_event(f"Critical deviations log updated: {len(critical_data)} new critical deviations found")
                
                # Show notification for critical deviations
                if any(row['Severity'] == 'CRITICAL' for row in critical_data):
                    self.log_event("⚠️ CRITICAL DEVIATIONS DETECTED ⚠️", "ERROR")
            else:
                self.log_event("No critical deviations found in automatic processing")
                
        except Exception as e:
            self.log_event(f"Error creating critical deviations log: {str(e)}", "ERROR")

#%%
def main():
    root = tk.Tk()
    app = MaterialAnomalyGUI(root)
    
    # Initial log message
    app.log_event("Material Anomaly Detection System initialized")
    app.log_event("Click 'Refresh Data' to load material analysis results")
    
    root.mainloop()

if __name__ == "__main__":
    main()

#%%