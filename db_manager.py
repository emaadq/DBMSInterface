"""
db_manager.py
Made for MySQL Workbench to manage a clothing retail store database.
Does all the basic CRUD operations as per assignment requirements.

CP363 - Database Systems
Assignment 9
March 28, 2025
"""

import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class ClothingStoreDBApp:
    def __init__(self, root):
        """Set up the main application window and database stuff"""
        self.root = root
        self.root.title("Clothing Store DB Manager")
        self.root.geometry("800x500")
        
        # Need these for database connection
        self.conn = None  # will hold the active connection
        self.cursor = None  # will be our cursor for executing commands
        
        # Build the GUI
        self.create_widgets()
    
    def create_widgets(self):
        """Create all the GUI elements - connection area, tabs, etc."""
        # Top part is for database connection
        conn_frame = ttk.LabelFrame(self.root, text="Database Connection")
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # All the fields we need to connect to MySQL
        ttk.Label(conn_frame, text="Host:").grid(row=0, column=0, padx=5, pady=5)
        self.host_var = tk.StringVar(value="localhost")
        ttk.Entry(conn_frame, textvariable=self.host_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, padx=5, pady=5)
        self.port_var = tk.StringVar(value="3306")  # default MySQL port
        ttk.Entry(conn_frame, textvariable=self.port_var, width=6).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(conn_frame, text="User:").grid(row=0, column=4, padx=5, pady=5)
        self.user_var = tk.StringVar(value="root")  # most people use root for local dev
        ttk.Entry(conn_frame, textvariable=self.user_var, width=10).grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(conn_frame, text="Password:").grid(row=0, column=6, padx=5, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(conn_frame, textvariable=self.password_var, show="*", width=10).grid(row=0, column=7, padx=5, pady=5)
        
        ttk.Label(conn_frame, text="Database:").grid(row=0, column=8, padx=5, pady=5)
        self.db_var = tk.StringVar(value="clothing_retail_store")  # our database name
        ttk.Entry(conn_frame, textvariable=self.db_var, width=20).grid(row=0, column=9, padx=5, pady=5)
        
        # Connect button and status indicator
        button_frame = ttk.Frame(conn_frame)
        button_frame.grid(row=1, column=0, columnspan=10, pady=5)
        
        ttk.Button(button_frame, text="Connect", command=self.connect_db).pack(side=tk.LEFT, padx=5)
        
        # Status indicator - turns green when connected
        self.conn_status = ttk.Label(button_frame, text="Not Connected", foreground="red")
        self.conn_status.pack(side=tk.LEFT, padx=20)
        
        # Notebook with tabs for different functions
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # First tab - for viewing and editing tables
        self.tables_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tables_tab, text="Tables")
        self.setup_tables_tab()
        
        # Second tab - for running custom SQL
        self.query_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.query_tab, text="SQL Query")
        self.setup_query_tab()
        
        # Status bar at the bottom
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_tables_tab(self):
        """Creates the table view tab with all the CRUD controls"""
        # Put selection stuff on the left
        left_panel = ttk.Frame(self.tables_tab)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(left_panel, text="Select Table:").pack(anchor=tk.W, pady=5)
        
        # Dropdown for table selection - will be populated after connection
        self.table_var = tk.StringVar()
        self.table_list = ttk.Combobox(left_panel, textvariable=self.table_var, state="readonly", width=20)
        self.table_list.pack(pady=5)
        self.table_list.bind("<<ComboboxSelected>>", self.load_table_data)
        
        # CRUD operation buttons
        ttk.Button(left_panel, text="View Data", command=self.load_table_data).pack(fill=tk.X, pady=2)
        ttk.Button(left_panel, text="Add Record", command=self.add_record).pack(fill=tk.X, pady=2)
        ttk.Button(left_panel, text="Edit Record", command=self.edit_record).pack(fill=tk.X, pady=2)
        ttk.Button(left_panel, text="Delete Record", command=self.delete_record).pack(fill=tk.X, pady=2)
        
        # Data display area on the right
        right_panel = ttk.Frame(self.tables_tab)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for displaying table data with scrollbars
        tree_frame = ttk.Frame(right_panel)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_frame)
        
        # Need both vertical and horizontal scrollbars for large datasets
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout makes scrollbars work properly
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        # This makes the treeview resize with the window
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
    
    def setup_query_tab(self):
        """Creates the SQL query tab for running custom queries"""
        # Top part for entering SQL
        input_frame = ttk.LabelFrame(self.query_tab, text="Enter SQL Query")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Text area for SQL input - multiline
        self.query_text = tk.Text(input_frame, height=5, wrap=tk.WORD)
        self.query_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Execute button
        ttk.Button(input_frame, text="Execute Query", command=self.execute_query).pack(anchor=tk.E, padx=5, pady=5)
        
        # Bottom part for query results
        results_frame = ttk.LabelFrame(self.query_tab, text="Query Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Another treeview for displaying query results
        tree_frame = ttk.Frame(results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.query_tree = ttk.Treeview(tree_frame)
        
        # Scrollbars again
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.query_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.query_tree.xview)
        self.query_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.query_tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
    
    def connect_db(self):
        """Tries to connect to the database with the given credentials"""
        try:
            # Close any existing connection first to avoid resource leaks
            if self.conn:
                self.cursor.close()
                self.conn.close()
            
            # Get all the connection info from the input fields
            host = self.host_var.get()
            port = self.port_var.get()
            user = self.user_var.get()
            password = self.password_var.get()
            database = self.db_var.get()
            
            # Try to connect - this will throw an exception if it fails
            self.conn = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            
            self.cursor = self.conn.cursor()
            
            # Update the UI to show we're connected
            self.conn_status.config(text="Connected", foreground="green")
            self.status_var.set(f"Connected to {database}")
            
            # Load table names into the dropdown
            self.load_tables()
            
            messagebox.showinfo("Connection", "Successfully connected to the database!")
            
        except mysql.connector.Error as e:
            # Show a helpful error message if connection fails
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            self.conn_status.config(text="Connection Failed", foreground="red")
            self.status_var.set("Connection failed")
    
    def load_tables(self):
        """Gets the list of tables from the database after connecting"""
        if not self.conn:
            messagebox.showwarning("No Connection", "Please connect to a database first.")
            return
        
        try:
            # SHOW TABLES is a MySQL command that lists all tables
            self.cursor.execute("SHOW TABLES")
            tables = [table[0] for table in self.cursor.fetchall()]
            
            # Put the table names in the dropdown
            self.table_list['values'] = tables
            if tables:
                self.table_list.current(0)  # select the first one
                self.load_table_data()  # and load its data
        
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to load tables: {e}")
    
    def load_table_data(self, event=None):
        """Loads and displays data from the selected table"""
        selected_table = self.table_var.get()
        
        if not selected_table:
            return
        
        try:
            # First get the column names and types
            self.cursor.execute(f"DESCRIBE {selected_table}")
            columns = [column[0] for column in self.cursor.fetchall()]
            
            # Set up the treeview columns based on table structure
            self.tree['columns'] = columns
            self.tree.column('#0', width=0, stretch=tk.NO)  # hide the first column
            
            # Clear existing headings first
            for col in self.tree['columns']:
                self.tree.heading(col, text='')
            
            # Set up the headers
            for col in columns:
                self.tree.column(col, anchor=tk.W, width=100)
                self.tree.heading(col, text=col, anchor=tk.W)
            
            # Get all the data with a simple SELECT *
            self.cursor.execute(f"SELECT * FROM {selected_table}")
            
            # Clear any existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Add all the rows to the treeview
            for i, row in enumerate(self.cursor.fetchall()):
                self.tree.insert('', 'end', iid=i, values=row)
            
            self.status_var.set(f"Loaded data from {selected_table}")
            
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to load table data: {e}")
    
    def add_record(self):
        """Creates and displays a form to add a new record to the current table"""
        selected_table = self.table_var.get()
        
        if not selected_table or not self.conn:
            messagebox.showwarning("Error", "Please select a table and ensure you're connected.")
            return
        
        try:
            # Need to know the table structure to create the right form fields
            self.cursor.execute(f"DESCRIBE {selected_table}")
            columns = self.cursor.fetchall()
            
            # Create a popup dialog for the new record form
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Add Record to {selected_table}")
            dialog.geometry("400x300")
            dialog.transient(self.root)
            dialog.grab_set()  # makes the dialog modal
            
            # If there are lots of fields, we need scrolling
            canvas = tk.Canvas(dialog)
            scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            # This makes the scrolling work
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            scrollbar.pack(side="right", fill="y")
            
            # Create input fields for each column
            entries = {}
            for i, col in enumerate(columns):
                col_name = col[0]
                col_type = col[1]
                is_auto = col[5] == 'auto_increment'  # skip auto_increment fields
                is_required = col[2] == 'NO'  # mark required fields
                
                # Don't need to enter auto_increment fields - the DB handles those
                if is_auto:
                    continue
                
                # Show field info in the label
                label_text = f"{col_name} ({col_type})"
                if is_required:
                    label_text += " *"  # asterisk for required fields
                    
                ttk.Label(scrollable_frame, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
                
                # Create an entry field
                entry_var = tk.StringVar()
                ttk.Entry(scrollable_frame, textvariable=entry_var, width=30).grid(row=i, column=1, padx=10, pady=5)
                
                entries[col_name] = entry_var
            
            # Button frame at the bottom
            button_frame = ttk.Frame(dialog)
            button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
            
            # Submit function for the add button
            def submit():
                # Get values from all fields
                values = {col: var.get() for col, var in entries.items() if var.get() or var.get() == '0'}
                
                # Check that required fields are filled
                missing_fields = []
                for col in columns:
                    col_name = col[0]
                    is_required = col[2] == 'NO'
                    is_auto = col[5] == 'auto_increment'
                    
                    if is_required and not is_auto and col_name in entries and not entries[col_name].get():
                        missing_fields.append(col_name)
                
                if missing_fields:
                    messagebox.showwarning("Required Fields", f"Please fill in required fields: {', '.join(missing_fields)}")
                    return
                
                if not values:
                    messagebox.showwarning("Empty Data", "Please enter data for at least one field.")
                    return
                
                try:
                    # Build the INSERT query - can't use string formatting for values due to SQL injection risk
                    cols = list(values.keys())
                    vals = list(values.values())
                    placeholders = ["%s"] * len(vals)  # use parameterized query
                    
                    query = f"INSERT INTO {selected_table} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
                    
                    # Execute and commit the insert
                    self.cursor.execute(query, vals)
                    self.conn.commit()
                    
                    messagebox.showinfo("Success", "Record added successfully!")
                    dialog.destroy()
                    
                    # Refresh the table view
                    self.load_table_data()
                    
                except mysql.connector.Error as e:
                    messagebox.showerror("Error", f"Failed to add record: {e}")
            
            # Add the submit button
            ttk.Button(button_frame, text="Add Record", command=submit).pack(pady=5)
            
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to get table structure: {e}")
    
    def edit_record(self):
        """Creates a form to edit the selected record"""
        selected_table = self.table_var.get()
        selected_items = self.tree.selection()
        
        if not selected_table or not self.conn:
            messagebox.showwarning("Error", "Please select a table and ensure you're connected.")
            return
        
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a record to edit.")
            return
        
        try:
            # Get the table structure
            self.cursor.execute(f"DESCRIBE {selected_table}")
            columns = self.cursor.fetchall()
            
            # Need to find the primary key to build the WHERE clause
            primary_key = None
            primary_key_index = -1
            
            for i, col in enumerate(columns):
                if col[3] == 'PRI':  # PRI means primary key in DESCRIBE results
                    primary_key = col[0]
                    primary_key_index = i
                    break
            
            if primary_key is None:
                messagebox.showerror("Error", "Could not identify primary key for this table.")
                return
            
            # Get the current values for the selected record
            selected_values = self.tree.item(selected_items[0])['values']
            primary_key_value = selected_values[primary_key_index]
            
            # Create dialog for the edit form
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Edit Record in {selected_table}")
            dialog.geometry("400x300")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Scrolling for lots of fields
            canvas = tk.Canvas(dialog)
            scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            scrollbar.pack(side="right", fill="y")
            
            # Create fields with current values filled in
            entries = {}
            for i, col in enumerate(columns):
                col_name = col[0]
                col_type = col[1]
                is_primary = col[3] == 'PRI'
                is_required = col[2] == 'NO'
                
                # Label with extra info
                label_text = f"{col_name} ({col_type})"
                if is_primary:
                    label_text += " [PK]"  # mark primary key
                if is_required:
                    label_text += " *"  # mark required fields
                    
                ttk.Label(scrollable_frame, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
                
                # Fill with current value
                current_value = str(selected_values[i]) if i < len(selected_values) else ""
                entry_var = tk.StringVar(value=current_value)
                entry = ttk.Entry(scrollable_frame, textvariable=entry_var, width=30)
                entry.grid(row=i, column=1, padx=10, pady=5)
                
                # Can't edit primary key - would change record identity
                if is_primary:
                    entry.config(state='readonly')
                
                entries[col_name] = entry_var
            
            # Button frame
            button_frame = ttk.Frame(dialog)
            button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
            
            # The update function for the submit button
            def submit():
                # Get all field values except primary key
                values = {col: var.get() for col, var in entries.items() if col != primary_key}
                
                # Check required fields
                missing_fields = []
                for col in columns:
                    col_name = col[0]
                    is_required = col[2] == 'NO'
                    is_primary = col[3] == 'PRI'
                    
                    if is_required and not is_primary and col_name in entries and not entries[col_name].get():
                        missing_fields.append(col_name)
                
                if missing_fields:
                    messagebox.showwarning("Required Fields", f"Please fill in required fields: {', '.join(missing_fields)}")
                    return
                
                try:
                    # Build the UPDATE query with SET clauses for each field
                    set_clauses = []
                    vals = []
                    
                    for col, var in entries.items():
                        if col != primary_key:  # Skip primary key in SET clause
                            set_clauses.append(f"{col} = %s")
                            vals.append(var.get())
                    
                    vals.append(primary_key_value)  # For WHERE clause
                    
                    # UPDATE table SET col1 = val1, col2 = val2 WHERE primary_key = primary_key_value
                    query = f"UPDATE {selected_table} SET {', '.join(set_clauses)} WHERE {primary_key} = %s"
                    
                    # Execute and commit
                    self.cursor.execute(query, vals)
                    self.conn.commit()
                    
                    messagebox.showinfo("Success", "Record updated successfully!")
                    dialog.destroy()
                    
                    # Refresh the view
                    self.load_table_data()
                    
                except mysql.connector.Error as e:
                    messagebox.showerror("Error", f"Failed to update record: {e}")
            
            # Add the submit button
            ttk.Button(button_frame, text="Update Record", command=submit).pack(pady=5)
            
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to prepare edit form: {e}")
    
    def delete_record(self):
        """Deletes the selected record after confirmation"""
        selected_table = self.table_var.get()
        selected_items = self.tree.selection()
        
        if not selected_table or not self.conn:
            messagebox.showwarning("Error", "Please select a table and ensure you're connected.")
            return
        
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a record to delete.")
            return
        
        try:
            # Need to find the primary key for the WHERE clause
            self.cursor.execute(f"DESCRIBE {selected_table}")
            columns = self.cursor.fetchall()
            
            # Find the primary key
            primary_key = None
            primary_key_index = -1
            
            for i, col in enumerate(columns):
                if col[3] == 'PRI':  # PRI means primary key
                    primary_key = col[0]
                    primary_key_index = i
                    break
            
            if primary_key is None:
                messagebox.showerror("Error", "Could not identify primary key for this table.")
                return
            
            # Get the primary key value for the selected record
            selected_values = self.tree.item(selected_items[0])['values']
            primary_key_value = selected_values[primary_key_index]
            
            # Always confirm before deleting! Too easy to delete wrong record
            if not messagebox.askyesno("Confirm", f"Delete record with {primary_key}={primary_key_value}?"):
                return
            
            # DELETE FROM table WHERE primary_key = value
            self.cursor.execute(f"DELETE FROM {selected_table} WHERE {primary_key} = %s", (primary_key_value,))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Record deleted successfully!")
            
            # Refresh the view
            self.load_table_data()
            
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to delete record: {e}")
    
    def execute_query(self):
        """Runs a custom SQL query and displays results for SELECT queries"""
        query = self.query_text.get("1.0", tk.END).strip()
        
        if not query:
            messagebox.showwarning("Empty Query", "Please enter an SQL query.")
            return
        
        if not self.conn:
            messagebox.showwarning("No Connection", "Please connect to a database first.")
            return
        
        try:
            # Run the query as is
            self.cursor.execute(query)
            
            # Handle SELECT queries differently - need to display results
            if query.lower().strip().startswith("select"):
                # Get column names from the result
                columns = [col[0] for col in self.cursor.description]
                
                # Set up the results treeview
                self.query_tree['columns'] = columns
                self.query_tree.column('#0', width=0, stretch=tk.NO)
                
                # Clear existing headers
                for col in self.query_tree['columns']:
                    self.query_tree.heading(col, text='')
                
                # Set column headings
                for col in columns:
                    self.query_tree.column(col, anchor=tk.W, width=100)
                    self.query_tree.heading(col, text=col, anchor=tk.W)
                
                # Clear any existing data
                for item in self.query_tree.get_children():
                    self.query_tree.delete(item)
                
                # Add all result rows to the treeview
                for i, row in enumerate(self.cursor.fetchall()):
                    self.query_tree.insert('', 'end', iid=i, values=row)
                
                self.status_var.set("Query executed successfully.")
            else:
                # For INSERT, UPDATE, DELETE we need to commit and just show a message
                self.conn.commit()
                messagebox.showinfo("Success", f"Query executed successfully. Affected rows: {self.cursor.rowcount}")
                self.status_var.set(f"Query executed. Affected rows: {self.cursor.rowcount}")
        
        except mysql.connector.Error as e:
            # Show details of any SQL errors
            messagebox.showerror("Query Error", f"Failed to execute query: {e}")