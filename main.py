import math
import tkinter as tk
from tkinter import ttk, messagebox
from settings import center_window, full_path
from components import LoginPage, ComponentStyle, ColumnSelectionWindow
from models import CustomLogger
from connector import MSSQLDatabase

class DBManager(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        center_window(self, 1200, 600, top=True)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.title("DataBase Management Software")
        icon_path = full_path("icon.ico")
        self.iconbitmap(icon_path)
        ComponentStyle(self)
        self.logger = CustomLogger()
        self.auth_user = None
        self.login_page = LoginPage(self, on_login_success=self.show_main_page)
        self.login_page.pack(expand=True, fill="both")
        self.mainloop()

    def show_login_page(self):
        self.main_page.forget()
        self.login_page.pack(expand=True, fill="both")
        self.auth_user = None
        self.login_page.info_label.config(text="Logout Successful")
        self.logger.info(f"{self.auth_user} logged out successfully")

    def show_main_page(self, host_name, port, user_name, password, db_name):
        self.connection = MSSQLDatabase(host_name, port, user_name, password, db_name)
        if not self.connection.conn and not self.connection.cursor:
            self.logger.info(f"User login failed, user does not exits.")
            return 'Connection Issue, check connection parameters'
        else:
            self.login_page.forget()
            self.main_page = MainPage(self)
            self.main_page.pack(expand=True, fill="both")
            return 'Connection was Successful'

class MainPage(ttk.Frame):
    def __init__(self, root):
        self.root = root
        super().__init__(self.root, style="Primary.TFrame")
 
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        self.selected_columns=[]
        self.table_columns=[]

        submenu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Action", menu=submenu)
        menu_bar.add_command(label="Logout", command=self.root.show_login_page)

        submenu.add_command(label='Select Table', command=self.table_mode)
        submenu.add_command(label='Raw Query', command=self.query_mode)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.table_mode_frame = ttk.Frame(self, style="Primary.TFrame")
        self.table_mode_frame.grid(row=0, column=0, sticky="nwes", padx=5, pady=2)
        self.table_mode_frame.columnconfigure(1, weight=1)
        self.create_table_mode_frame(self.table_mode_frame)
        #self.table_mode_frame.grid_remove()

        self.query_mode_frame = ttk.Frame(self, style="Primary.TFrame")
        self.query_mode_frame.grid(row=0, column=0, sticky="nwes", padx=5, pady=0)
        self.query_mode_frame.grid_remove()

        self.tree_frame = ttk.Frame(self, style="Primary.TFrame")
        self.tree_frame.grid(row=1, column=0, sticky="nwes", padx=5, pady=5)
        self.tree_frame.rowconfigure(0, weight=1)
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.columnconfigure(1, weight=1)
        self.tree_frame.columnconfigure(2, weight=1)
        self.create_tree_frame(self.tree_frame)
        #self.tree_frame.grid_remove()

        self.manupulation_frame = ttk.Frame(self, style="Primary.TFrame")
        self.manupulation_frame.grid(row=1, column=0, sticky="nwes", padx=5, pady=5)
        self.manupulation_frame.rowconfigure(0, weight=1)
        self.manupulation_frame.columnconfigure(0, weight=1)
        self.manupulation_frame.grid_remove()

        self.export_frame = ttk.Frame(self, style="Primary.TFrame")
        self.export_frame.grid(row=2, column=0, sticky="nwes", padx=5, pady=5)
        self.export_frame.rowconfigure(0, weight=1)
        self.export_frame.columnconfigure(0, weight=1)
    
    def table_mode(self):
        self.query_mode_frame.grid_remove()
        self.table_mode_frame.grid()

    def query_mode(self):
        self.table_mode_frame.grid_remove()
        self.query_mode_frame.grid()
    
    def create_table_mode_frame(self, frame):
        self.selected_table_var = tk.StringVar(value='')
        self.selected_table = None
        self.tables = self.root.connection.fetch_tables()
        table_label = ttk.Label(
                frame, style="Main.TLabel", text="Select Table : "
                
        )
        table_label.grid(row=0, column=0, sticky="nwes", padx=0, pady=0)

        table_combobox = ttk.Combobox(
                frame,
                textvariable=self.selected_table_var,
                values=[table_name[0] for table_name in self.tables.values],
                state="readonly",
                width=50
                )
        table_combobox.bind("<<ComboboxSelected>>", self.select_table)
        table_combobox.grid(row=0, column=1, sticky="nwes", padx=0, pady=0)

        separator = ttk.Separator(frame, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=6, sticky="we", padx=0, pady=5)


        table_label = ttk.Label(
                frame, style="Main.TLabel", text="Select Columns : "
        )
        table_label.grid(row=2, column=0, sticky="w", pady=(5,0))


        column_button = ttk.Button( frame, text="Filter Columns", style="Bold.TButton", command=lambda:ColumnSelectionWindow(self, notification_type="info") ) 
        column_button.grid(row=2, column=1, sticky="we", pady=(5,0))

        self.new_button = ttk.Button(
            frame, text="New Entry", style="Bold.TButton", command=self.new_entry_wiegets
        )
        self.new_button.grid(row=2, column=2, sticky="we", pady=(5,0))

        self.update_button = ttk.Button( frame, text="Update Entry", style="Bold.TButton", command=self.update_entry_widgets,)
        self.update_button.grid(row=2, column=3, sticky="we", pady=(5,0))

        self.delete_button = ttk.Button(
            frame,
            text="Delete Entries",
            style="Bold.TButton",
            command=self.delete_rows,
        )
        self.delete_button.grid(row=2, column=4, sticky="we", pady=(5,0))

    def create_query_mode_frame(self, frame):
        option_frame = ttk.Frame(self.query_mode_frame, style="Primary.TFrame")
        option_frame.grid(row=0, column=0, sticky="nwes", padx=10, pady=10)
        option_frame.columnconfigure(0, weight=0)
        option_frame.rowconfigure(0, weight=0)

        separator = ttk.Separator(self.query_mode_frame, orient="horizontal")
        separator.grid(row=1, column=0, sticky="we", padx=(0, 10), pady=(0, 5))

        action_frame = ttk.Frame(self.query_mode_frame, style="Primary.TFrame")
        action_frame.grid(row=2, column=0, sticky="nwes", padx=(10), pady=(0, 5))
        action_frame.rowconfigure(0, weight=0)
        action_frame.rowconfigure(1, weight=1)
        action_frame.columnconfigure(0, weight=1)

        query_label = ttk.Label(
            option_frame, style="Main.TLabel", text="Raw Query"
        )
        query_label.pack(pady=(0, 5), side='left')

        button = ttk.Button(
            option_frame, text="Execute", style="Bold.TButton", command=self.show_selected_columns
        )
        button.pack(pady=(0, 5), side='left')
    
    def create_tree_frame(self, frame):
        self.tree = ttk.Treeview(frame, show="headings")
        self.tree.grid(
            row=0, column=0, columnspan=6, sticky="nsew", padx=(0, 0), pady=(0, 2)
        )
        # self.tree.bind('<<TreeviewSelect>>', self.update_entry_widgets)

        self.scrollbar = ttk.Scrollbar(
            frame, orient="vertical", command=self.tree.yview
        )
        self.scrollbar.grid(row=0, column=7, sticky="ns", padx=(0, 0), pady=0)

        self.tree.configure(yscrollcommand=self.scrollbar.set)

        style = ttk.Style()
        style.configure(
            "Treeview.Heading",
            background="blue",
            foreground="black",
            font=("Helvetica", 10, "bold"),
        )
        style.configure("Treeview", rowheight=25, borderwidth=1, relief="solid")
        style.map("Treeview.Heading", background=[("active", "blue")])

        self.save_button = ttk.Button(
            frame, text="Save", style="Bold.TButton", command=self.save_method
        )
        self.save_button.grid(row=1, column=0, sticky="we")

        self.cancel_button = ttk.Button(
            frame, text="Cancel", style="Bold.TButton", command=self.clear_input_fields
        )
        self.cancel_button.grid(row=1, column=1, sticky="we")    

        self.previous_button = ttk.Button(
                frame, text="< Previous", style="Bold.TButton", command=self.get_previous_page
                )
        self.previous_button.grid(row=1, column=0, sticky="we")    
 
        self.page_number_label = ttk.Label(
                frame, style="Main.TLabel", text="", justify='center', anchor='c'
            )
        self.page_number_label.grid(row=1, column=1, sticky="we")
                
        self.next_button = ttk.Button(
            frame, text="Next >", style="Bold.TButton", command=self.get_next_page
        )
        self.next_button.grid(row=1, column=2, sticky="we")
    
    def get_next_page(self):
        page = self.page_number + 1
        if page > self.total_pages:
            messagebox.showerror('Max page reached', 'Max Page Reached')
            return
        self.show_selected_columns(page=page)

    def get_previous_page(self):
        page = self.page_number - 1
        if page<1:
            print(dir(messagebox))
            messagebox.showerror('Min page reached', 'Min Page Reached')
            return
        self.show_selected_columns(page=page)

    def show_all(self):
        result = self.root.connection.fetch_table_data(self.selected_table)
        self.selected_columns = []
        self.table_columns = result.columns
        self.manupulation_frame.grid_remove()
        self.tree_frame.grid()
        self.update_treeview("Showing All Entries", result.columns, result.values)

    def show_selected_columns(self, selected_table=None, page=1):
        if selected_table:
            self.selected_columns = []
            self.selected_table = selected_table

        if not self.validate():
            return

        self.page_number = page
        table_name = self.selected_table
        columns = ', '.join(self.selected_columns) or '*'
        primary_key = 'GID'
        page_size = 2
        skip_rows = (self.page_number - 1) * page_size
        fetch_rows = page_size
        print(f'{skip_rows=}, {fetch_rows=}\n', table_name, columns, primary_key, skip_rows, fetch_rows)
        result = self.root.connection.get_paginated_results(table_name, columns, primary_key, skip_rows, fetch_rows)
        if selected_table:
            self.table_columns = result.columns
            self.total_pages = math.ceil(self.root.connection.get_page_size(table_name).values[0]/page_size)
        self.manupulation_frame.grid_remove()
        self.page_number_label.config(text=f'{self.page_number} / {self.total_pages}')
        self.tree_frame.grid()
        self.update_treeview("Showing Selected Columns Entries", result.columns, result.values)

    def update_treeview(self, title, headers, data):
        print('\n**Updating Treeview**\n', title, headers, data)
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = headers

        for header in headers:
            self.tree.heading(header, anchor=tk.W, text=header)
            self.tree.column(header, anchor=tk.W)

        for row in data:
            self.tree.insert("", "end", iid=row[0], values=[*row])
    
    def validate(self):
        if not self.selected_table:
            messagebox.showerror('Select Table', 'Please Select a Table')
            return False
        else:return True

    def new_entry_wiegets(self):
        self.tree_frame.grid_remove()
        self.manupulation_frame.grid()
    
    def update_entry_widgets(self):
        self.tree_frame.grid_remove()
        self.manupulation_frame.grid()

    def delete_rows(self):
        ...

    def save_method(self):
        ...

    def clear_input_fields(self):
        ...

    def select_table(self, event=None):
        self.show_selected_columns(selected_table=self.selected_table_var.get())
    
    def get_selected_columns(self, selected_columns):
        self.selected_columns = selected_columns
        print(f'{self.selected_columns=}')
        self.show_selected_columns()

if __name__ == '__main__':
    DBManager()

