import json
from tkinter import ttk
import threading
import tkinter as tk
from models import TkImages, ValueSetter, TransactionData,CustomLogger, CustomImages
from pymodbus.client import ModbusTcpClient
from settings import center_window, full_path
from ping3 import ping


class Header:
    def __init__(self, frame, column, row, colspan, rowspan, plaza_details):
        header_frame = ttk.Frame(frame, padding=2, style='Primary.TFrame')
        header_frame.grid(
            column=column, row=row, columnspan=colspan, rowspan=rowspan, sticky="ewn", pady=(0,2)
        )
        header_frame.columnconfigure(0, weight=3)
        header_frame.columnconfigure(1, weight=3)
        header_frame.columnconfigure(2, weight=3)
        header_frame.columnconfigure(3, weight=0)

        logo_label = ttk.Label(header_frame, background="white")
        logo_label.image = TkImages(active_image="apl_techno.png").active_image
        logo_label.config(image=logo_label.image)
        logo_label.grid(column=0, row=0, rowspan=1, sticky="w")

        name_frame = ttk.Frame(header_frame, style='Primary.TFrame')
        name_frame.grid(column=1, row=0)
        system_label = ttk.Label(
            name_frame,
            text=plaza_details.Name,
            font=("Helvetica", 12, "bold"),
            background="white",
            padding=0,
        )

        system_label.grid(column=1, row=0)
        system_label = ttk.Label(
            name_frame,
            text=plaza_details.Authority,
            font=("Helvetica", 10, "bold"),
            background="white",
            padding=0,
        )

        system_label.grid(column=1, row=1)
        nhi_logo_label = ttk.Label(header_frame, background="white")
        nhi_logo_label.image = TkImages(
            active_image="nhai.png", subsample=16
        ).active_image
        nhi_logo_label.config(image=nhi_logo_label.image)
        nhi_logo_label.grid(column=3, row=0, rowspan=1, sticky="e")

class UserPanel:
    def __init__(self, parent, column, row, colspan, rowspan):
        self.parent = parent
        user_frame = ttk.Frame(parent, padding=5, style="Primary.TFrame")
        user_frame.grid(
            column=column, row=row, columnspan=colspan, rowspan=rowspan, sticky="nwe", pady=(0, 0)
        )
        user_frame.columnconfigure(0, weight=0)
        user_frame.columnconfigure(1, weight=1)
        user_frame.columnconfigure(2, weight=0)
        user_frame.columnconfigure(3, weight=1)
        user_frame.columnconfigure(4, weight=0)
        user_frame.columnconfigure(5, weight=1)
        user_frame.columnconfigure(6, weight=0)
        user_frame.columnconfigure(7, weight=1)

        ttk.Label( user_frame, text="User : ", justify="left", font=("Helvetica", 10), background="white",).grid(row=0, column=0, sticky="ew")

        ttk.Label( user_frame, text="Lane : ", justify="left", font=("Helvetica", 10), background="white",).grid(row=0, column=2, sticky="ew")

        ttk.Label( user_frame, text="Shift : ", justify="left", font=("Helvetica", 10), background="white",).grid(row=0, column=4, sticky="ew")

        ttk.Label( user_frame, text="Date-Time : ", justify="left", font=("Helvetica", 10), background="white",).grid(row=0, column=6, sticky="ew")

        self.user_label = ttk.Label(
            user_frame,
            text=self.parent.auth_user.GID,
            justify="left",
            font=("Helvetica", 10, "bold"),
            background="white",
        ).grid(row=0, column=1, sticky="ew")

        self.lane_label = ttk.Label(
            user_frame,
            text=self.parent.lane_details.Name,
            justify="left",
            font=("Helvetica", 10, "bold"),
            background="white",
        ).grid(row=0, column=3, sticky="ew")

        self.shift_label = ttk.Label(
            user_frame,
            text=self.parent.shift_details.Name,
            justify="left",
            font=("Helvetica", 10, "bold"),
            background="white",
        ).grid(row=0, column=5, sticky="ew")

        self.datetime_label = ttk.Label(
            user_frame,
            textvariable=self.parent.datetime_var,
            justify="left",
            font=("Helvetica", 10, "bold"),
            background="white",
        ).grid(row=0, column=7, sticky="ew")

class LoginPage(ttk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, style="Primary.TFrame")
        self.on_login_success = on_login_success
        self.parent = parent
       
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)

        self.bind("<Return>", self.login)
        self.parent.bind("<Escape>", lambda x : self.parent.destroy())

        frame = ttk.Frame(self, padding=20, style="Border.TFrame")
        frame.columnconfigure(0, weight=1)
        frame.grid(column=1, row=0, sticky="wne", pady=(50), padx=20, ipadx=20)

        self.heading = ("Helvetica", 16, "bold")
        self.normal_font = ("Helvetica", 12)
        self.small_font = ("Helvetica", 10)
        self.small_bold_font = ("Helvetica", 10, "bold")
        
        self.host_name_var = tk.StringVar(value='localhost')
        self.port_var = tk.StringVar(value='3306')
        self.user_name_var = tk.StringVar(value='shubham')
        self.password_var = tk.StringVar(value='dubey')
        self.db_name_var = tk.StringVar(value='TMS_Client')

        _label = ttk.Label( frame, text="Please Login", font=self.heading, background='white',)
        _label.grid(column=0, row=1, pady=(0, 20))

        label = ttk.Label( frame, text="Host Name/IP : ", font=self.small_bold_font, background='white',)
        label.grid(column=0, row=2, sticky="w")

        with open('config.json', 'r') as f:
            self.config = json.load(f)
            print(self.config)
        host_combobox = ttk.Combobox(
                frame,
                textvariable=self.host_name_var,
                values=[users for users in self.config.get('Users', [])],
                )
        host_combobox.bind("<<ComboboxSelected>>", self.select_host)
        host_combobox.grid(column=0, row=3, sticky="we", pady=(0, 10))

        host_combobox.focus_set()
        
        label = ttk.Label( frame, text="Port : ", font=self.small_bold_font, background='white',)
        label.grid(column=0, row=4, sticky="w")
        entry = ttk.Entry( frame, width=26, textvariable=self.port_var, font=("Helvetica", 9), background="white",)
        entry.grid(column=0, row=5, sticky="we", pady=(0, 10))

        label = ttk.Label( frame, text="User Name : ", font=self.small_bold_font, background='white',)
        label.grid(column=0, row=6, sticky="w")
        self.user_combobox = ttk.Combobox(
                frame,
                textvariable=self.user_name_var,
                values=[],
                )
        self.user_combobox.bind("<<ComboboxSelected>>", self.select_user)
        self.user_combobox.grid(column=0, row=7, sticky="we", pady=(0, 10))

        label = ttk.Label( frame, text="Password : ", font=self.small_bold_font, background="white",)
        label.grid(column=0, row=8, sticky="w")
        entry = ttk.Entry( frame, width=26, show="*", textvariable=self.password_var, font=("Helvetica", 9), background="white",)
        entry.grid(column=0, row=9, sticky="we", pady=(0, 10))

        label = ttk.Label( frame, text="DataBase Name :", font=self.small_bold_font, background="white",)
        label.grid(column=0, row=10, sticky="w")
        entry = ttk.Entry( frame, width=26, textvariable=self.db_name_var, font=("Helvetica", 9), background="white",)
        entry.grid(column=0, row=11, sticky="we", pady=(0, 10))

        self.login_button = ttk.Button( frame, style="Custom.TButton", text="Login", compound="left", command=self.login,)
        self.login_button.grid(column=0, row=12, pady=(0, 20))
        
        self.info_label = ttk.Label( frame, text='', font=self.small_bold_font, background='white',)
        self.info_label.grid(column=0, row=13, sticky="w", pady=(0, 10))

    def select_host(self, event=None):
        users = self.config.get("Users")
        if users:
            hosts = users.get(self.host_name_var.get())
            self.port_var.set(hosts.get('port', ''))
            users = [user for user in hosts.get('details', [])]
            self.user_combobox.config(value=users)

    def select_user(self, event=None):
        if self.config.get('Users'):
            for user, details in self.config.get('Users').get(self.host_name_var.get()).get('details').items():
                if user == self.user_name_var.get():
                    self.db_name_var.set(details.get('db_name', ''))
                    self.password_var.set(details.get('password', ''))

    def login(self, event=None):
        host_name = self.host_name_var.get()
        port = self.port_var.get()
        user_name = self.user_name_var.get()
        password = self.password_var.get()
        db_name = self.db_name_var.get()
        print(host_name, port, user_name, password, db_name) 
        if all((host_name, port, user_name, password, db_name)):
            self.config = {
                    **self.config,
                    "Users": {
                        **self.config.get('Users', {}),
                        self.host_name_var.get(): {
                            'port': self.port_var.get(),
                            'details': 
                                {
                                    **self.config.get('Users', {}).get(self.host_name_var.get(),{}).get('details', {}),
                                    self.user_name_var.get(): {
                                        **self.config.get('Users', {}).get(self.host_name_var.get(),{}).get('details', {}).get(self.user_name_var.get(), {}),
                                        'db_name': self.db_name_var.get(),
                                        'password': self.password_var.get()
                                    }
                                }
                            }
                        }
                    }
            print(self.config)
            with open('config.json', 'w') as f:
                json.dump(self.config, f)
            self.login_button.config(state='disabled')
            value = self.on_login_success(host_name, port, user_name, password, db_name)
            self.login_button.config(state='Normal')
            self.info_label.config(text=value)
        else:
            self.info_label.config(text='Enter All the Details')

class ColumnSelectionWindow(tk.Toplevel):
    def __init__( self, parent, notification_type="warning", title="APL Techno"):
        super().__init__(parent)
        self.parent = parent
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        center_window(self, 250, 200, top=False)

        def dismiss(event=None):
            self.grab_release()
            self.destroy()
        self.focus_set()
        self.bind("<Return>", dismiss)
        self.protocol("WM_DELETE_WINDOW", dismiss)
        self.iconbitmap(full_path(f"{notification_type}.ico"))
        self.title(notification_type)

        main_frame = ttk.Frame(self, style="Plane.TFrame")
        main_frame.grid(column=0, row=0, sticky="wnes")
        main_frame.columnconfigure(0, weight=1)

        main_frame.rowconfigure(0, weight=1)

        self.listbox = tk.Listbox(main_frame, selectmode="multiple")

        for option in self.parent.table_columns:
            self.listbox.insert(tk.END, option)

        for index, option in enumerate(self.parent.table_columns):
            if option in self.parent.selected_columns:
                self.listbox.selection_set(index)

        self.listbox.pack(padx=5, pady=(5), expand=True, fill='both')

        select_button = ttk.Button(main_frame, text="Select", command=self.get_selection)
        select_button.pack(padx=5, fill='x')
        
        self.wait_visibility()
        self.grab_set()
        self.wait_window()

    def get_selection(self):
        selected_indices = self.listbox.curselection()
        selected_columns = [self.listbox.get(i) for i in selected_indices]
        self.parent.get_selected_columns(selected_columns)
        self.grab_release()
        self.destroy()

class FleetWindow(tk.Toplevel):
    def __init__( self, parent, vehicle_count_var, notification_type="warning", title="APL Techno", image="setup.png", subsample=5):
        super().__init__(parent)
        self.parent = parent
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        center_window(self, 400, 400, top=False)

        def dismiss(event=None):
            self.grab_release()
            self.destroy()
            self.parent.transaction.fleet = False
            self.parent.status_panel.modbus_devices.barrier.write(value=0)
            self.parent.status_panel.modbus_devices.traffic_light.write(value=0)

        self.focus_set()

        self.parent.status_panel.modbus_devices.barrier.write(value=1)
        self.parent.status_panel.modbus_devices.traffic_light.write(value=1)

        self.protocol("WM_DELETE_WINDOW", dismiss)
        self.iconbitmap(full_path("warning.ico"))
        self.title("Passing Fleet/Convoy")

        main_frame = ttk.Frame(self, style="Plane.TFrame")
        main_frame.grid(column=0, row=0, sticky="wnes")
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        ttk.Label(
            main_frame,
            text="Fleet Passing",
            font=("Helvetica", 14, "bold"),
            background="white",
            padding=5,
        ).grid(column=0, row=0, columnspan=2)
        image = CustomImages(active_image="passing_fleet.png", subsample=2)

        show_image = ttk.Label(
            main_frame, font=("Helvetica", 12, "bold"), background="white", padding=0
        )
        show_image.grid(column=0, row=1, columnspan=2)
        show_image.image = image.get_active_image
        show_image.config(image=show_image.image)

        ttk.Label(
            main_frame,
            text="Vehicle Count : ",
            font=("Helvetica", 12, "bold"),
            background="white",
            padding=5,
        ).grid(column=0, row=2, sticky="e")
        ttk.Label(
            main_frame,
            textvariable=vehicle_count_var,
            font=("Helvetica", 12, "bold"),
            background="white",
            padding=5,
        ).grid(column=1, row=2, sticky="w")

        self.wait_visibility()
        self.grab_set()
        self.wait_window()

class VehiclePanel(ttk.Frame):
    def __init__(self, parent, column, row, colspan, rowspan):
        self.parent = parent
        super().__init__(parent, style="Primary.TFrame")
        self.grid(column=column, row=row, columnspan=colspan, rowspan=rowspan, sticky="nwes", padx=(0,2), ipadx=(3), ipady=(3))

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        heading = ttk.Label(
            self, text="Vehicle Details", justify="left", style="Main.TLabel"
        )
        heading.grid(column=0, row=0, columnspan=3, sticky="we")

        vehicle_details_frame = ttk.Frame(self, style="Plane.TFrame")
        vehicle_details_frame.grid(
            column=0, row=1, columnspan=1, rowspan=1, padx=5, pady=5, sticky="nwes"
        )
        vehicle_details_frame.columnconfigure(0, weight=1)
        vehicle_details_frame.columnconfigure(1, weight=1)

        ttk.Label(
            vehicle_details_frame, text="Vehicle Number", style="Primary.TLabel"
        ).grid(column=0, row=0, sticky="w", pady=(0, 5))
        self.vehicle_number_entry = ttk.Entry(
            vehicle_details_frame,
            textvariable=self.parent.vehicle_number_var,
            foreground="#B7950B",
            background="white",
            font=("Helvetica", 13, "bold"),
        )
        self.vehicle_number_entry.grid(
            column=1, row=0, columnspan=2, sticky="e", pady=(0, 5)
        )

        ttk.Label(
            vehicle_details_frame, text="Selected Vehicle Class", style="Primary.TLabel"
        ).grid(column=0, row=1, sticky="w", pady=(0, 5))
        ttk.Label(
            vehicle_details_frame,
            textvariable=self.parent.vehicle_class_var,
            style="Secondary.TLabel",
        ).grid(column=1, row=1, columnspan=2, sticky="e", pady=(0, 5))

        ttk.Label(
            vehicle_details_frame, text="Journey Class", style="Primary.TLabel"
        ).grid(column=0, row=2, sticky="w", pady=(0, 5))
        ttk.Label(
            vehicle_details_frame,
            textvariable=self.parent.journey_class_var,
            style="Secondary.TLabel",
        ).grid(column=1, row=2, columnspan=2, sticky="e", pady=(0, 5))

        ttk.Label(
            vehicle_details_frame, text="Exemption Class", style="Primary.TLabel"
        ).grid(column=0, row=3, sticky="w", pady=(0, 5))
        ttk.Label(
            vehicle_details_frame,
            textvariable=self.parent.exempt_class_var,
            style="Secondary.TLabel",
        ).grid(column=1, row=3, columnspan=2, sticky="e", pady=(0, 5))

        ttk.Label(
            vehicle_details_frame, text="FastTag TID", style="Primary.TLabel"
        ).grid(column=0, row=4, sticky="w", pady=(0, 5))
        ttk.Label(
            vehicle_details_frame,
            textvariable=self.parent.fast_tag_var,
            style="Secondary.TLabel",
        ).grid(column=1, row=4, columnspan=2, sticky="e", pady=(0, 5))

        ttk.Label(vehicle_details_frame, text="Toll Fees", style="Primary.TLabel").grid(
            column=0, row=5, sticky="w", pady=(0, 5)
        )
        ttk.Label(
            vehicle_details_frame,
            textvariable=self.parent.toll_fee_var,
            style="Secondary.TLabel",
        ).grid(column=1, row=5, columnspan=2, sticky="e", pady=(0, 5))

        # vehicle class slection frame
        self.vehicle_selection_frame = ttk.Frame(self, style="Plane.TFrame")
        self.vehicle_selection_frame.grid(column=0, row=2, columnspan=2, sticky="wens")
        self.vehicle_selection_frame.columnconfigure(0, weight=1)
        self.vehicle_selection_frame.columnconfigure(1, weight=1)
        self.vehicle_selection_frame.columnconfigure(2, weight=1)
        self.vehicle_selection_frame.grid_remove()

        self.exempt_classes_label = ttk.Label(
            self.vehicle_selection_frame,
            text="Select Vehicle Class",
            style="Main.TLabel",
        )
        self.exempt_classes_label.grid(column=0, row=0, columnspan=3, pady=(0, 2), sticky="wne")

        raw_vehicle_classes = self.parent.vehicle_classes
        self.vehicle_classes = [ValueSetter(raw_vehicle_classes.columns,entry) for entry in raw_vehicle_classes.values]

        self.create_class_buttons(
            self.vehicle_selection_frame,
            self.vehicle_classes,
            self.select_vehicle_class,
        )
        # journey class slection frame
        self.journey_selection_frame = ttk.Frame(self, style="Plane.TFrame")
        self.journey_selection_frame.grid(column=0, row=2, columnspan=2, sticky="wesn")
        self.journey_selection_frame.grid_remove()

        self.exempt_classes_label = ttk.Label(
            self.journey_selection_frame,
            text="Select Journey Class",
            style="Main.TLabel",
        )
        self.exempt_classes_label.grid(
            column=0, row=0, columnspan=3, sticky="wen", pady=(0, 5)
        )
        raw_journey_classes = self.parent.journey_classes
        self.journey_classes = [ValueSetter(raw_journey_classes.columns,entry) for entry in raw_journey_classes.values]

        self.create_class_buttons(
            self.journey_selection_frame,
            self.journey_classes,
            self.select_journey_class,
        )

        # exempt class slection frame
        self.exempt_selection_frame = ttk.Frame(self, style="Plane.TFrame")
        self.exempt_selection_frame.grid(column=0, row=2, columnspan=2, sticky="wens")
        self.exempt_selection_frame.grid_remove()

        self.exempt_classes_label = ttk.Label(
            self.exempt_selection_frame, text="Select Exempt Class", style="Main.TLabel"
        )
        self.exempt_classes_label.grid(
            column=0, row=0, columnspan=3, sticky="wne", pady=(0, 5)
        )
        raw_exempt_classes = self.parent.exempt_classes
        self.exempt_classes = [ValueSetter(raw_exempt_classes.columns,entry) for entry in raw_exempt_classes.values]

        self.create_class_buttons(
            self.exempt_selection_frame,
            self.exempt_classes,
            self.select_exempt_class,
        )

        self.vehicle_number_entry.focus()
        self.show_vehicle_class_selection()
        self.parent.parent.bind("<Escape>", self.reset_selection_classes)

    def show_vehicle_class_selection(self, warning=False):
        self.parent.toll_fee_var.set("")
        self.vehicle_selection_frame.grid()

    def show_journey_class_selection(self, warning=False):
        self.vehicle_selection_frame.grid_remove()
        self.exempt_selection_frame.grid_remove()
        self.journey_selection_frame.grid()

    def show_exempt_class_selection(self, warning=False):
        self.vehicle_selection_frame.grid_remove()
        self.journey_selection_frame.grid_remove()
        if self.parent.selected_journey_class.Exempt:
            self.exempt_selection_frame.grid()
        else:
            self.exempt_selection_frame.grid_remove()

    def select_vehicle_class(self, vehicle_class):
        self.parent.selected_vehicle_class = vehicle_class
        self.parent.vehicle_class_var.set(vehicle_class.Name)
        self.show_journey_class_selection()
        self.parent.logger.info("Vehicle Class Selected Manually")
        print('vehicle class selected successfully')

    def select_journey_class(self, journey_class):
        if not self.parent.selected_vehicle_class:
            return
        self.parent.selected_journey_class = journey_class
        self.parent.journey_class_var.set(journey_class.Name)
        self.parent.calculate_toll_fare()
        self.show_exempt_class_selection()
        self.parent.logger.info("Journey Class Selected Manually")

    def select_exempt_class(self, exempt_class):
        if not self.parent.selected_journey_class or not self.parent.selected_vehicle_class:
            return False
        if not self.parent.selected_journey_class.Exempt:
            return False
        self.parent.selected_exempt_class = exempt_class
        self.parent.exempt_class_var.set(exempt_class.Name)
        self.exempt_selection_frame.grid_remove()
        self.parent.logger.info("Exempt Class Selected Manually")

    def create_class_buttons( self, frame, vehicle_objects, function):
        for index, vehicle in enumerate(vehicle_objects):
            column = index % 3
            row = index // 3 + 1

            ttk.Button( frame,
                style="Custom.TButton",
                text=f"{vehicle.Name} \n {vehicle.Key_Binding}",
                command=lambda v=vehicle: function(v),
            ).grid(column=column, row=row, padx=2, pady=2, sticky="we")

            self.parent.parent.bind(vehicle.Key_Binding, lambda event=None, v=vehicle: function(v))

    def reset_selection_classes(self, event=None):
        self.journey_selection_frame.grid_remove()
        self.exempt_selection_frame.grid_remove()
        self.show_vehicle_class_selection()
        self.parent.reset_selection_classes()

class TransactionPanel(ttk.Frame):
    def __init__(self, parent, frame, column, row, colspan, rowspan):
        super().__init__(frame, style="Primary.TFrame")
        self.grid( column=column, row=row, columnspan=colspan, rowspan=rowspan, sticky="wens", pady=(0,0))

        self.parent = parent

        ttk.Label(
            self,
            text="Transaction Details",
            justify="left",
            style="Main.TLabel",
        ).pack(anchor="center", fill="both")

        headings = ['Transaction ID', 'Vehicle Class', 'Paid Amount', 'Transaction_Date', 'Vehicle_Number']
        self.tree = ttk.Treeview(
            self,
            columns=headings,
            show="headings",
        )
        
        for heading in headings:
            self.tree.heading(heading, text=heading)
            self.tree.column(heading, width=120, anchor="center")

        self.tree.pack(fill="both", expand=True)

        transaction_data = self.parent.transaction_data.values
        for row in transaction_data:
            row = list(row)
            print(row)
            self.tree.insert("", "end", values=row)
        warning_label = ttk.Label( self, textvariable=self.parent.warning_var, style="Warning.TLabel")
        warning_label.pack(fill="both", padx=5)

    def update_treeview(self, new_row_data):
        items = self.tree.get_children()

        if len(items)>=10:
            self.tree.delete(items[-1])

        self.tree.insert("", 0, values=new_row_data)


class ComponentStyle(ttk.Style):
    def __init__(self, root):
        super().__init__(root)

        # Frame Styles 
        #--------------
        self.configure( "Primary.TFrame", background="white")
        self.configure("Border.TFrame", background="white", borderwidth=1, relief='ridge')
        self.configure("Back.TFrame", background="#05B2DC")
        
        # Button Styles
        #--------------
        self.configure(
            "Custom.TButton",
            width=15,
            font=("Helvetica", 10, "bold"),
            padding=3,
        )

        # Entry Styles
        #-------------
        self.configure(
            "Primary.TEntry",
            foreground="#08158c",
            background="white",
            font=("Helvetica", 20, "bold"),
            width=26,
            highlightthickness=1,
            highlightbackground="#08158c",
        )

        # Treeview Styles
        #----------------
        self.configure(
            "Treeview.Heading",
            background="white",
            foreground="#08158c",
        )
        self.configure("Treeview", rowheight=23)

        # Label Styles
        #-------------
        self.configure(
            "Primary.TLabel",
            foreground="#2268c7",
            background="white",
            font=("Helvetica", 12, "bold"),
        )
        self.configure(
            "Warning.TLabel",
            foreground="#2268c7",
            relief="flat",
            background="white",
            font=("Helvetica", 12, "bold"),
        )
        self.configure(
            "Secondary.TLabel",
            foreground="#08158c",
            background="white",
            font=("Helvetica", 11, "bold"),
        )
        self.configure(
            "Main.TLabel",
            foreground="black",
            background="white",
            font=("Helvetica", 10, 'bold'),
            padding=2,
        )
        self.configure(
            "Black.TLabel",
            foreground="white",
            background="black",
            font=("Helvetica", 10, 'bold'),
            padding=2,
        )       
        # Seperator Styles
        #-----------------
        self.configure("Primary.TSeparator", background="#08158c")

