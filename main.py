import math
import tkinter as tk
from tkinter import ttk, messagebox
from settings import center_window, full_path
from components import ( 
                        LoginPage,
                        ComponentStyle,
                        ColumnSelectionWindow,
                        DateWidget,
                        DateTimeWidget,
                        TimeWidget, StringWidget,
                        IntegerWidget,
                        BinaryEntryWidget,
                        BooleanWidget,
                        FloatWidget,
                        JsonWidget, 
                        XmlWidget, 
                        UUIDWidget,
                        GeometryWidget, 
                        GeographyWidget,
                        ImageWidget,
                        ForeignKeyComboBoxWidget,
                        SQLWidget,
                        ErrorWindow,
                        BinaryFileWidget,
                        HierarchyWidget
                        )
from models import CustomLogger, ValueSetter
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

        self.list_view = False
        self.entry_view = False
        self.update_view = False
        self.delete_view = False

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

        self.manipulation_frame = ttk.Frame(self, style="Primary.TFrame")
        self.manipulation_frame.grid(row=1, column=0, sticky="nwes", padx=5, pady=5)
        self.manipulation_frame.columnconfigure(1, weight=1)
        self.manipulation_frame.columnconfigure(3, weight=1)
        self.manipulation_frame.grid_remove()

        self.export_frame = ttk.Frame(self, style="Primary.TFrame")
        self.export_frame.grid(row=2, column=0, sticky="nwes", padx=5, pady=5)
        self.export_frame.rowconfigure(0, weight=1)
        self.export_frame.columnconfigure(0, weight=1)

    def reset_all(self):
        self.list_view = False
        self.entry_view = False
        self.update_view = False
        self.delete_view = False
        self.column_button.config(state='disabled')
        self.new_button.config(state='disabled')
        self.update_button.config(state='disabled')
        self.delete_button.config(state='disabled')

    def table_mode(self):
        self.query_mode_frame.grid_remove()
        self.table_mode_frame.grid()

    def query_mode(self):
        self.table_mode_frame.grid_remove()
        self.query_mode_frame.grid()
    
    def create_table_mode_frame(self, frame):
        self.selected_table_var = tk.StringVar(value='')
        self.selected_table = None
        self.tables = self.root.connection.fetch_table_names()
        table_label = ttk.Label(
                frame, style="Normal_Bold.TLabel", text="Select Table : "
                
        )
        table_label.grid(row=0, column=0, sticky="nwes", padx=0, pady=0)

        table_combobox = ttk.Combobox(
                frame,
                textvariable=self.selected_table_var,
                values=sorted([table_name[0] for table_name in self.tables.values]),
                state="readonly",
                width=50
                )
        table_combobox.bind("<<ComboboxSelected>>", self.select_table)
        table_combobox.grid(row=0, column=1, sticky="nwes", padx=0, pady=0)

        separator = ttk.Separator(frame, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=6, sticky="we", padx=0, pady=5)


        table_label = ttk.Label(
                frame, style="Normal_Bold.TLabel", text="Select Columns : "
        )
        table_label.grid(row=2, column=0, sticky="w", pady=(5,0))


        self.column_button = ttk.Button(
                frame,
                text="Filter Columns",
                style="Bold.TButton",
                state='disabled',
                command=lambda:ColumnSelectionWindow(self, notification_type="info")
                ) 
        self.column_button.grid(row=2, column=1, sticky="we", pady=(5,0))

        self.new_button = ttk.Button(
            frame, text="New Entry", style="Bold.TButton", state='disabled', command=self.new_entry_widgets
        )
        self.new_button.grid(row=2, column=2, sticky="we", pady=(5,0))

        self.update_button = ttk.Button( frame, text="Update Entry", state='disabled', style="Bold.TButton", command=self.update_entry_widgets,)
        self.update_button.grid(row=2, column=3, sticky="we", pady=(5,0))

        self.delete_button = ttk.Button(frame, text="Delete Entries", state='disabled', style="Bold.TButton", command=self.delete_rows,)
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
            option_frame, style="Normal_Bold.TLabel", text="Raw Query"
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
        style.configure("Custom.Treeview.Heading", background="yellow", foreground="black", font=("Arial", 10, "bold"))
        self.save_button = ttk.Button(
            frame, text="Save", style="Bold.TButton", command=self.save_method
        )
        self.save_button.grid(row=1, column=0, sticky="we")

        self.cancel_button = ttk.Button(
            frame, text="Cancel", style="Bold.TButton", command=self.clear_input_fields
        )
        self.cancel_button.grid(row=1, column=1, sticky="we")    

        self.previous_button = ttk.Button(
                frame, text="< Previous", state='disabled', style="Bold.TButton", command=self.get_previous_page
                )
        self.previous_button.grid(row=1, column=0, sticky="we")    
 
        self.page_number_label = ttk.Label(
                frame, style="Normal.TLabel", text="", justify='center', anchor='c'
            )
        self.page_number_label.grid(row=1, column=1, sticky="we")
                
        self.next_button = ttk.Button(
            frame, text="Next >", style="Bold.TButton", state='disabled', command=self.get_next_page
        )
        self.next_button.grid(row=1, column=2, sticky="we")

        specific_label = ttk.Label(
                frame, style="Normal.TLabel", text="Enter Page Number", justify='center', anchor='c'
            )
        specific_label.grid(row=2, column=0, sticky="we")
 
        self.specific_page_entry = ttk.Entry(frame)
        self.specific_page_entry.grid(row=2, column=1, sticky="we")
        
        self.specific_page_button = ttk.Button(
            frame, text="Get Page", style="Bold.TButton", state='disabled', command=self.get_specific_page
        )
        self.specific_page_button.grid(row=2, column=2, sticky="we")   
    
    def get_specific_page(self):
        page = self.specific_page_entry.get()
        try:
            page = int(page)
        except:
            messagebox.showerror('Invalid Value', 'Please Enter Integer value')
            return
        if page > self.total_pages or page<1:
            messagebox.showerror('Page out of reached', 'Page Does not Exists')
            return
        self.show_selected_columns(page=page)

    def get_next_page(self):
        page = self.page_number + 1
        if page > self.total_pages:
            messagebox.showerror('Max page reached', 'Max Page Reached')
            return
        self.show_selected_columns(page=page)

    def get_previous_page(self):
        page = self.page_number - 1
        if page<1:
            messagebox.showerror('Min page reached', 'Min Page Reached')
            return
        self.show_selected_columns(page=page)

    def show_all(self):
        result = self.root.connection.fetch_table_data(self.selected_table)
        self.selected_columns = []
        self.table_columns = result.columns
        self.manipulation_frame.grid_remove()
        self.tree_frame.grid()
        self.update_treeview("Showing All Entries", result.columns, result.values)

    def show_selected_columns(self, selected_table=None, page=1):
        self.page_number = page
        page_size = 20

        if selected_table:
            self.selected_columns = []
            self.selected_table = selected_table
            self.primary_keys = [i[1] for i in self.root.connection.fetch_primary_key_details(selected_table).values]
            info = self.root.connection.fetch_table_details(selected_table)
            self.table_info = {detail[1]: ValueSetter(info.columns, detail) for detail in info.values}
            self.table_columns = list(self.table_info.keys())
            self.total_pages = math.ceil(self.root.connection.fetch_row_count(selected_table).values[0]/page_size)
            
        if not self.validate():
            return
        for index, col in enumerate(self.table_info.items()):
            print(index, f' -> {col}\n')
        table_name = self.selected_table
        skip_rows = (self.page_number - 1) * page_size
        fetch_rows = page_size
        columns = ', '.join(set(self.primary_keys + self.selected_columns)) if self.selected_columns else '*'
        sort_key = self.primary_keys[0] if self.primary_keys else self.table_columns[0]

        result = self.root.connection.get_paginated_results(table_name, columns, sort_key, skip_rows, fetch_rows)

        self.manipulation_frame.grid_remove()
        self.tree_frame.grid()
        self.page_number_label.config(text=f'{self.page_number} / {self.total_pages}')
        self.update_treeview("Showing Selected Columns Entries", result.columns, result.values)

        
        if self.page_number+1 > self.total_pages:
            self.next_button.config(state='disabled')
        else:
            self.next_button.config(state='normal')
        if self.page_number-1<1:
            self.previous_button.config(state='disabled')
        else:
            self.previous_button.config(state='normal')

    def update_treeview(self, title, headers, data):
        headers = ['Sr. NO.', *headers]
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = headers

        for header in headers:
            self.tree.heading(header, anchor=tk.W, text=header)
            self.tree.column(header, anchor=tk.W)

        for index, row in enumerate(data):
            self.tree.insert("", "end", iid=index, values=[index, *row])

    def validate(self):
        if not self.selected_table:
            messagebox.showerror('Select Table', 'Please Select a Table')
            return False
        else:return True

    def new_entry_widgets(self):
        self.tree_frame.grid_remove()
        self.clean_manipulation_frame()
        self.manipulation_frame.grid()

        label = ttk.Label(self.manipulation_frame, text=f'New Entry for {self.selected_table}', style="Heading.TLabel")
        label.grid(row=0, column=0, columnspan=3, sticky="new", padx=(0, 5), pady=(0, 5))

        column_details_for_entry = [
                column for key, column in self.table_info.items()
                if (
                    key in set(self.primary_keys + self.selected_columns)
                    or column.IS_NULLABLE == 'NO'
                    ) and column.HAS_IDENTITY == 'NO'
                and column.COLUMN_DEFAULT != '(getdate())'
                and column.DATA_TYPE != 'timestamp'
                ]

        for key, column in self.table_info.items():
            print(f'''
            {key} ->
            --------
            DATA_TYPE - {column.DATA_TYPE},
            IS_NULLABLE {column.IS_NULLABLE},
            HAS_IDENTITY - {column.HAS_IDENTITY},
            CHARACTER_MAXIMUM_LENGTH - {column.CHARACTER_MAXIMUM_LENGTH},
            NUMERIC_SCALE - {column.NUMERIC_SCALE},
            NUMERIC_PRECISION - {column.NUMERIC_PRECISION},
            COLUMN_DEFAULT - {column.COLUMN_DEFAULT},
            IDENTITY_SEED - {column.IDENTITY_SEED},
            IDENTITY_INCREMENT - {column.IDENTITY_INCREMENT},
            IsComputed - {column.IsComputed},
            ComputedColumnDefinition - {column.ComputedColumnDefinition},
            HasDefaultConstraint - {column.HasDefaultConstraint},
            DefaultConstraintDefinition - {column.DefaultConstraintDefinition},
            ForeignKey - {column.ForeignKey},
            PrimaryTable - {column.PrimaryTable},
            PrimaryColumn - {column.PrimaryColumn}
            \n'''
                  )
        self.entry_details = []
        index = 1
        for index, column_detail in enumerate(column_details_for_entry, 2):

            label_text = f"{column_detail.COLUMN_NAME} {'*' if column_detail.IS_NULLABLE == 'NO' else ''}"
            label = ttk.Label(self.manipulation_frame, text=label_text, style="Small_Bold.TLabel")
            label.grid(row=index//2, column=(2 if index%2 else 0), sticky="new", padx=(0, 5), pady=(0, 5))

            entry = self.get_widget_for_data_type(self.manipulation_frame, column_detail)
            entry.grid(row=index//2, column=(3 if index%2 else 1), sticky="new", padx=(0, 50), pady=(0, 5))
            self.entry_details.append(entry)

        save_button = ttk.Button(self.manipulation_frame, text="Save", style="Bold.TButton", command=self.save_new_entry_data)
        save_button.grid(row=index+1, columnspan=2, column=0, sticky="we")
 
        cancel_button = ttk.Button(self.manipulation_frame, text="Cancel", style="Bold.TButton", command=self.reset_new_entry_data)
        cancel_button.grid(row=index+1, columnspan=2, column=2, sticky="we")
        return
    
    def validate_new_entry_data(self):
        errors = []
        for entry in self.entry_details:
            success, message = entry.validate()
            if not success:
                errors.append(f'{entry.column_details.COLUMN_NAME} - {message}')
        return errors

    def save_new_entry_data(self):
        validation_errors = self.validate_new_entry_data()
        if validation_errors:
            ErrorWindow(self, errors=validation_errors)
            return False, 'Validation Error'
        else:
            columns = []
            values = []
            placeholders = []
            for details in self.entry_details:
                try:
                    value = details.get_value()
                    if value:
                        columns.append(details.column_details.COLUMN_NAME)
                        if isinstance(value, str) and ((value.startswith("geometry::") or value.startswith("geography::")) or details.column_details.DATA_TYPE in ['binary', 'varbinary', 'image']):
                                placeholders.append(value)
                        else:
                            values.append(value)
                            placeholders.append("?")

                except Exception as e:
                    print(f"Error processing column '{column_name}': {str(e)}")
                    return False, str(e)

            query = f"INSERT INTO [{self.selected_table}] ([{'], ['.join(columns)}]) VALUES ({', '.join(placeholders)})"
            print(query, values, sep='\n\n')
            insert_result = self.root.connection.insert_data(query, values)
            if insert_result.status:
                messagebox.showinfo('Operation Successful', f'Data has been saved in table {self.selected_table}')
                self.reset_new_entry_data()
            else:
                messagebox.showerror('Operation Failed', f'Data could not be saved in table {self.selected_table} due to {insert_result.message}')

    def reset_new_entry_data(self):
        for entry in self.entry_details:
            entry.reset()

    def get_widget_for_data_type(self, frame, column_details):
        data_type = column_details.DATA_TYPE.lower()

        string_types = ['char', 'varchar', 'nchar', 'nvarchar', 'text']
        binary_types = ['binary', 'varbinary']
        integer_types = ['tinyint', 'smallint', 'int', 'bigint']
        float_types = ['decimal', 'numeric', 'smallmoney', 'money', 'float', 'real']
        datetime_types = ['datetime', 'smalldatetime', 'datetime2', 'datetimeoffset']
        
        if column_details.ForeignKey:
            vals = self.root.connection.fetch_foreign_table_data(column_details.PrimaryTable, column_details.PrimaryColumn)
            print(vals.columns, vals.values)
            foreign_key_values = [i[0] for i in vals.values]
            return ForeignKeyComboBoxWidget(frame, column_details, foreign_key_values)
        elif data_type in string_types:
            return StringWidget(frame, column_details)
        elif data_type in integer_types:
            return IntegerWidget(frame, column_details)
        elif data_type in float_types:
            return FloatWidget(frame, column_details)
        elif data_type in binary_types:
            return BinaryFileWidget(frame, column_details)
        elif data_type in datetime_types:
            return DateTimeWidget(frame, column_details)
        elif data_type == 'bit':
            return BooleanWidget(frame, column_details)
        elif data_type == 'date':
            return DateWidget(frame, column_details)
        elif data_type == 'time':
            return TimeWidget(frame, column_details)
        elif data_type == 'uniqueidentifier':
            return UUIDWidget(frame, column_details)
        elif data_type == 'xml':
            return XmlWidget(frame, column_details)
        elif data_type == 'json':
            return JsonWidget(frame, column_details)
        elif data_type == 'geography':
            return GeographyWidget(frame, column_details)
        elif data_type == 'geometry':
            return GeometryWidget(frame, column_details)
        elif data_type == 'image':
            return ImageWidget(frame, column_details)
        elif data_type == 'sql_variant':
            return SQLWidget(frame, column_details)
        elif data_type == 'hierarchyid':
            return HierarchyWidget(frame, column_details)
        else:
            return StringWidget(frame, column_details)

    def temporary(self):
        self.table_info = db_manager.fetch_table_details(self.selected_table)
        self.action_label.configure(text=f"New Entry for {self.selected_table_name}")
        column_details = db_manager.fetch_foreign_key_details(self.selected_table)
        self.entry_details = []
        for index in range(0, len(self.table_info.values), 2):
            col = 0
            for row in self.table_info.values[index : index + 2]:
                info = ValueSetter(self.table_info.columns, row)
                foreign_column_info = self.get_foreign_key_details(column_details, info.COLUMN_NAME)
                default_value = info.COLUMN_DEFAULT[2:-2] if info.COLUMN_DEFAULT else ""
                info.entry_label = info.COLUMN_NAME
                info.entry_properties = info
                info.entry_foreign_properties = foreign_column_info
                info.entry_default = default_value

                label = ttk.Label(
                    self.action_frame, text=info.COLUMN_NAME, style="Plane.TLabel"
                )
                label.grid(
                    row=index, column=0 + col, sticky="new", padx=(0, 5), pady=(0, 5)
                )

                if foreign_column_info:
                    info.entry_variable = tk.StringVar(value=default_value)
                    vals = db_manager.fetch_table_data(foreign_column_info.PrimaryTable)
                    foreign_key_values = [i[self.table_primary_key_index] for i in vals.values]
                    entry = ttk.Combobox(
                        self.action_frame,
                        textvariable=info.entry_variable,
                        values=foreign_key_values,
                        state="readonly",
                    )
                    entry.grid(
                        row=index,
                        column=1 + col,
                        sticky="new",
                        padx=(0, 10),
                        pady=(0, 5),
                    )

                elif info.HAS_IDENTITY=='YES':
                    print('Name', info.COLUMN_NAME, 'Identity', info.HAS_IDENTITY)
                    info.entry_variable = tk.StringVar(value=default_value)
                    pass

                elif info.DATA_TYPE == "int":
                    info.entry_variable = tk.StringVar(value=default_value)
                    entry = ttk.Entry(
                        self.action_frame, textvariable=info.entry_variable
                    )
                    entry.grid(
                        row=index,
                        column=1 + col,
                        sticky="new",
                        padx=(0, 10),
                        pady=(0, 5),
                    )

                elif info.DATA_TYPE == "bit":
                    info.entry_variable = tk.StringVar(value=default_value)
                    entry = ttk.Combobox(self.action_frame, textvariable=info.entry_variable, values=[1, 0], state="readonly")
                    entry.grid(row=index, column=1 + col, sticky="new", padx=(0, 10), pady=(0, 5))

                elif info.DATA_TYPE == "datetime" or info.DATA_TYPE == "date":
                    print(default_value.split(' ')[0])
                    info.entry_variable = tk.StringVar(value=default_value.split(' ')[0])
                    entry = DateEntry(
                        self.action_frame,
                        width=12,
                        borderwidth=2,
                        date_pattern='y-mm-dd',
                        textvariable=info.entry_variable,
                    )
                    entry.grid(
                        row=index,
                        column=1 + col,
                        sticky="new",
                        padx=(0, 10),
                        pady=(0, 5),
                    )

                elif info.DATA_TYPE == "time":
                    info.entry_variable = TimeEntry(
                        self.action_frame, index, (1 + col), default_value
                    )
                else:
                    info.entry_variable = tk.StringVar(value=default_value)
                    entry = ttk.Entry(
                        self.action_frame, textvariable=info.entry_variable
                    )
                    entry.grid(
                        row=index,
                        column=1 + col,
                        sticky="new",
                        padx=(0, 10),
                        pady=(0, 5),
                    )

                self.entry_details.append(info)
                col += 3

            separator = ttk.Separator(self.action_frame, orient="vertical")
            separator.grid(row=index, column=2, sticky="ns", padx=(0, 10), pady=(0, 5))










    def update_entry_widgets(self):
        self.tree_frame.grid_remove()
        self.manipulation_frame.grid()

    def delete_rows(self):
        ...

    def save_method(self):
        ...

    def clear_input_fields(self):
        ...

    def select_table(self, event=None):
        self.column_button.config(state='normal')
        self.new_button.config(state='normal')
        self.update_button.config(state='normal')
        self.delete_button.config(state='normal')
        self.specific_page_button.config(state='normal')
        self.show_selected_columns(selected_table=self.selected_table_var.get())
    
    def get_selected_columns(self, selected_columns):
        self.selected_columns = selected_columns
        print(f'{self.selected_columns=}')
        self.show_selected_columns()
    
    def clean_manipulation_frame(self):
        for widget in self.manipulation_frame.winfo_children():
            widget.destroy()

if __name__ == '__main__':
    DBManager()

