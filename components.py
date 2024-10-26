import os
import json
import re
import uuid
import binascii
from datetime import datetime, time, date
from PIL import Image
from tkinter import ttk, filedialog
from tkcalendar import DateEntry
import tkinter as tk
import xml.etree.ElementTree as ET
from models import TkImages
from settings import center_window, full_path


class Header:
    def __init__(self, frame, column, row, colspan, rowspan, plaza_details):
        header_frame = ttk.Frame(frame, padding=2, style="Primary.TFrame")
        header_frame.grid(
            column=column,
            row=row,
            columnspan=colspan,
            rowspan=rowspan,
            sticky="ewn",
            pady=(0, 2),
        )
        header_frame.columnconfigure(0, weight=3)
        header_frame.columnconfigure(1, weight=3)
        header_frame.columnconfigure(2, weight=3)
        header_frame.columnconfigure(3, weight=0)

        logo_label = ttk.Label(header_frame, background="white")
        logo_label.image = TkImages(active_image="apl_techno.png").active_image
        logo_label.config(image=logo_label.image)
        logo_label.grid(column=0, row=0, rowspan=1, sticky="w")

        name_frame = ttk.Frame(header_frame, style="Primary.TFrame")
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
            column=column,
            row=row,
            columnspan=colspan,
            rowspan=rowspan,
            sticky="nwe",
            pady=(0, 0),
        )
        user_frame.columnconfigure(0, weight=0)
        user_frame.columnconfigure(1, weight=1)
        user_frame.columnconfigure(2, weight=0)
        user_frame.columnconfigure(3, weight=1)
        user_frame.columnconfigure(4, weight=0)
        user_frame.columnconfigure(5, weight=1)
        user_frame.columnconfigure(6, weight=0)
        user_frame.columnconfigure(7, weight=1)

        ttk.Label(
            user_frame,
            text="User : ",
            justify="left",
            font=("Helvetica", 10),
            background="white",
        ).grid(row=0, column=0, sticky="ew")

        ttk.Label(
            user_frame,
            text="Lane : ",
            justify="left",
            font=("Helvetica", 10),
            background="white",
        ).grid(row=0, column=2, sticky="ew")

        ttk.Label(
            user_frame,
            text="Shift : ",
            justify="left",
            font=("Helvetica", 10),
            background="white",
        ).grid(row=0, column=4, sticky="ew")

        ttk.Label(
            user_frame,
            text="Date-Time : ",
            justify="left",
            font=("Helvetica", 10),
            background="white",
        ).grid(row=0, column=6, sticky="ew")

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
        self.parent.bind("<Escape>", lambda x: self.parent.destroy())

        frame = ttk.Frame(self, padding=20, style="Border.TFrame")
        frame.columnconfigure(0, weight=1)
        frame.grid(column=1, row=0, sticky="wne", pady=(50), padx=20, ipadx=20)

        self.heading = ("Helvetica", 14, "bold")
        self.normal_font = ("Helvetica", 12)
        self.small_font = ("Helvetica", 10)
        self.small_bold_font = ("Helvetica", 10, "bold")

        self.host_name_var = tk.StringVar(value="")
        self.port_var = tk.StringVar(value="")
        self.user_name_var = tk.StringVar(value="")
        self.password_var = tk.StringVar(value="")
        self.db_name_var = tk.StringVar(value="")

        _label = ttk.Label(
            frame,
            text="Please Login",
            font=self.heading,
            background="white",
        )
        _label.grid(column=0, row=1, pady=(0, 20))

        label = ttk.Label(
            frame,
            text="Host Name/IP : ",
            font=self.small_bold_font,
            background="white",
        )
        label.grid(column=0, row=2, sticky="w")

        with open("config.json", "r") as f:
            self.config = json.load(f)
        host_combobox = ttk.Combobox(
            frame,
            textvariable=self.host_name_var,
            values=[users for users in self.config.get("hosts", [])],
        )
        host_combobox.bind("<<ComboboxSelected>>", self.select_host)
        host_combobox.grid(column=0, row=3, sticky="we", pady=(0, 10))

        host_combobox.focus_set()

        label = ttk.Label(
            frame,
            text="Port : ",
            font=self.small_bold_font,
            background="white",
        )
        label.grid(column=0, row=4, sticky="w")
        entry = ttk.Entry(
            frame,
            width=26,
            textvariable=self.port_var,
            font=("Helvetica", 9),
            background="white",
        )
        entry.grid(column=0, row=5, sticky="we", pady=(0, 10))

        label = ttk.Label(
            frame,
            text="User Name : ",
            font=self.small_bold_font,
            background="white",
        )
        label.grid(column=0, row=6, sticky="w")
        self.user_combobox = ttk.Combobox(
            frame, textvariable=self.user_name_var, values=[]
        )
        self.user_combobox.bind("<<ComboboxSelected>>", self.select_user)
        self.user_combobox.grid(column=0, row=7, sticky="we", pady=(0, 10))

        label = ttk.Label(
            frame,
            text="Password : ",
            font=self.small_bold_font,
            background="white",
        )
        label.grid(column=0, row=8, sticky="w")
        entry = ttk.Entry(
            frame,
            width=26,
            show="*",
            textvariable=self.password_var,
            font=("Helvetica", 9),
            background="white",
        )
        entry.grid(column=0, row=9, sticky="we", pady=(0, 10))

        label = ttk.Label(
            frame,
            text="DataBase Name :",
            font=self.small_bold_font,
            background="white",
        )
        label.grid(column=0, row=10, sticky="w")
        self.db_combobox = ttk.Combobox(
            frame,
            textvariable=self.db_name_var,
            values=[],
        )
        self.db_combobox.bind("<<ComboboxSelected>>", self.select_user)
        self.db_combobox.grid(column=0, row=11, sticky="we", pady=(0, 10))

        self.login_button = ttk.Button(
            frame,
            style="Custom.TButton",
            text="Login",
            compound="left",
            command=self.login,
        )
        self.login_button.grid(column=0, row=12, pady=(0, 20))

        self.info_label = ttk.Label(
            frame,
            text="",
            font=self.small_bold_font,
            background="white",
        )
        self.info_label.grid(column=0, row=13, sticky="w", pady=(0, 10))

    def select_host(self, event=None):
        hosts = self.config.get("hosts")
        if hosts:
            host = hosts.get(self.host_name_var.get())
            self.port_var.set(host.get("port", ""))
            users = [user for user in host.get("details", [])]
            self.user_combobox.config(value=users)
            self.user_combobox.focus_set()

    def select_user(self, event=None):
        if self.config.get("hosts"):
            for user, details in (
                self.config.get("hosts")
                .get(self.host_name_var.get())
                .get("details")
                .items()
            ):
                if user == self.user_name_var.get():
                    self.password_var.set(details.get("password", ""))
                    self.db_combobox.config(value=details.get("databases", []))
                    self.db_combobox.focus_set()

    def login(self, event=None):
        host_name = self.host_name_var.get()
        port = self.port_var.get()
        user_name = self.user_name_var.get()
        password = self.password_var.get()
        db_name = self.db_name_var.get()
        if all((host_name, port, user_name, password, db_name)):
            self.save_connection_details(host_name, port, user_name, password, db_name)
            self.login_button.config(state="disabled")
            value = self.on_login_success(host_name, port, user_name, password, db_name)
            self.login_button.config(state="Normal")
            self.info_label.config(text=value)
        else:
            self.info_label.config(text="Enter All the Details")

    def save_connection_details(self, host_name, port, user_name, password, db_name):
        self.config = {
            **self.config,
            "hosts": {
                **self.config.get("hosts", {}),
                host_name: {
                    "port": port,
                    "details": {
                        **self.config.get("hosts", {})
                        .get(host_name, {})
                        .get("details", {}),
                        user_name: {
                            **self.config.get("hosts", {})
                            .get(host_name, {})
                            .get("details", {})
                            .get(user_name, {}),
                            "password": password,
                            "databases": list(
                                {
                                    *self.config.get("hosts", {})
                                    .get(host_name, {})
                                    .get("details", {})
                                    .get(user_name, {})
                                    .get("databases", []),
                                    db_name,
                                }
                            ),
                        },
                    },
                },
            },
        }
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=2)


class ColumnSelectionWindow(tk.Toplevel):
    def __init__(self, parent, notification_type="warning", title="APL Techno"):
        super().__init__(parent)
        self.parent = parent
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        center_window(self, 400, 250, top=False)

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

        self.listbox.pack(padx=5, pady=(5), expand=True, fill="both")

        select_button = ttk.Button(
            main_frame, text="Select", command=self.get_selection
        )
        select_button.pack(padx=5, fill="x")

        self.wait_visibility()
        self.grab_set()
        self.wait_window()

    def get_selection(self):
        selected_indices = self.listbox.curselection()
        selected_columns = [self.listbox.get(i) for i in selected_indices]
        self.parent.get_selected_columns(selected_columns)
        self.grab_release()
        self.destroy()


class ErrorWindow(tk.Toplevel):
    def __init__(
        self, parent, errors=[], notification_type="warning", title="Input Field Error"
    ):
        super().__init__(parent)
        self.parent = parent
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        center_window(self, 600, 400, top=False)

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

        text_widget = tk.Text(main_frame, wrap=tk.WORD, font=("Helvetica", 9))
        text_widget.grid(row=0, column=0, sticky="ewns")

        scrollbar = tk.Scrollbar(main_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")

        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_widget.yview)

        self.insert_bulleted_list(text_widget, errors)

        self.wait_visibility()
        self.grab_set()
        self.wait_window()

    def insert_bulleted_list(self, text_widget, items):
        text_widget.delete(1.0, tk.END)
        for index, item in enumerate(items, 1):
            text_widget.insert(tk.END, f" {index}. {item}\n")


class ForeignKeyComboBoxWidget:
    def __init__(self, frame, column_details, foreign_key_values):
        self.column_details = column_details
        self.variable = tk.StringVar()
        self.entry = ttk.Combobox(
            frame,
            textvariable=self.variable,
            values=foreign_key_values,
            width=3,
            state="readonly",
        )
        # self.objects_dict = {str(getattr(obj, obj._id)): obj for obj in kwargs.get('values')}

    def get_value(self):
        return self.variable.get()

    def grid(self, *args, **kwargs):
        self.entry.grid(*args, **kwargs)

    def get_object(self):
        return self.objects_dict.get(str(self.get()))

    def get_value1(self):
        obj = self.get_object()
        if obj:
            return getattr(obj, self.primary_key)
        else:
            return obj

    def validate(self):
        return True, "Valid."

    def reset(self):
        self.variable.set("")


class DateWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details
        self.variable = tk.StringVar()
        self.entry = DateEntry(
            frame,
            textvariable=self.variable,
            date_pattern="y-mm-dd",
            width=12,
            borderwidth=2,
        )

    def get_value(self):
        return self.entry.get_date().strftime("%Y-%m-%d")

    def grid(self, *args, **kwargs):
        self.entry.grid(*args, **kwargs)

    def validate(self):
        value = self.entry.get_date()
        try:
            min_date = date(1753, 1, 1)
            max_date = date(9999, 12, 31)

            if not (min_date <= value <= max_date):
                return (
                    False,
                    f"Date must be between {min_date.date()} and {max_date.date()}.",
                )
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD."
        return True, "Valid."

    def reset(self):
        self.variable.set("")


class TimeWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details

        self.frame = ttk.Frame(frame, style="Primary.TFrame")

        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(4, weight=1)

        self.start_hour_var = tk.StringVar(value="00")
        self.start_minute_var = tk.StringVar(value="00")

        label = ttk.Label(self.frame, style="Small_Bold.TLabel", text="Hours: ")
        label.grid(row=0, column=0, padx=(2), sticky="we")
        start_hour = ttk.Combobox(
            self.frame,
            textvariable=self.start_hour_var,
            values=[f"{i:02}" for i in range(24)],
            width=3,
            state="readonly",
        )
        start_hour.grid(row=0, column=1, padx=(2), sticky="we")
        start_hour.set("00")

        label = ttk.Label(self.frame, style="Small_Bold.TLabel", text=":")
        label.grid(row=0, column=2, padx=(2), sticky="we")

        label = ttk.Label(self.frame, style="Small_Bold.TLabel", text="Minutes: ")
        label.grid(row=0, column=3, padx=(2), sticky="we")
        start_minute = ttk.Combobox(
            self.frame,
            textvariable=self.start_minute_var,
            values=[f"{i:02}" for i in range(60)],
            width=3,
            state="readonly",
        )
        start_minute.grid(row=0, column=4, padx=(2), sticky="we")
        start_minute.set("00")

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def get_value(self):
        selected_hour = int(self.start_hour_var.get())
        selected_minute = int(self.start_minute_var.get())

        selected_time = time(hour=selected_hour, minute=selected_minute)
        return selected_time.strftime("%H:%M:%S")

    def validate(self):
        value = self.get_value()
        try:
            datetime.strptime(value, "%H:%M:%S.%f")
            return True, "Valid."
        except ValueError:
            try:
                datetime.strptime(value, "%H:%M:%S")
                return True, "Valid."
            except ValueError:
                return False, "Invalid time format. Use HH:MM:SS[.nnnnnnn]"

    def reset(self):
        self.start_hour_var.set("00")
        self.start_minute_var.set("00")


class DateTimeWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details

        self.frame = ttk.Frame(frame, style="Primary.TFrame")

        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(3, weight=1)

        self.start_date_var = tk.StringVar()
        self.start_minute_var = tk.StringVar(value="00")
        self.start_hour_var = tk.StringVar(value="00")

        self.start_date = DateEntry(
            self.frame,
            textvariable=self.start_date_var,
            date_pattern="y-mm-dd",
            width=12,
            borderwidth=2,
        )
        self.start_date.grid(row=0, column=0, padx=(2), sticky="we")

        self.start_hour = ttk.Combobox(
            self.frame,
            textvariable=self.start_hour_var,
            values=[f"{i:02}" for i in range(24)],
            width=3,
            state="readonly",
        )
        self.start_hour.grid(row=0, column=1, padx=(2), sticky="we")
        self.start_hour.set("00")

        label = ttk.Label(self.frame, style="Small_Bold.TLabel", text=":")
        label.grid(row=0, column=2, padx=(2), sticky="we")

        self.start_minute = ttk.Combobox(
            self.frame,
            textvariable=self.start_minute_var,
            values=[f"{i:02}" for i in range(60)],
            width=3,
        )
        self.start_minute.set("00")
        self.start_minute.grid(row=0, column=3, padx=(2), sticky="we")

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def reset(self):
        self.start_date_var.set("")
        self.start_hour_var.set("00")
        self.start_minute_var.set("00")

    def get_value(self):
        selected_date = self.start_date.get_date()
        selected_hour = int(self.start_hour_var.get())
        selected_minute = int(self.start_minute_var.get())

        selected_datetime = datetime(
            year=selected_date.year,
            month=selected_date.month,
            day=selected_date.day,
            hour=selected_hour,
            minute=selected_minute,
        )
        return selected_datetime.strftime("%Y-%m-%d %H:%M:%S")

    def validate(self):
        selected_date = self.start_date.get_date()
        selected_hour = int(self.start_hour.get())
        selected_minute = int(self.start_minute.get())

        try:
            selected_datetime = datetime(
                year=selected_date.year,
                month=selected_date.month,
                day=selected_date.day,
                hour=selected_hour,
                minute=selected_minute,
            )
        except ValueError as e:
            return False, str(e)

        if self.column_details.DATA_TYPE in ["datetime", "datetime2"]:
            if selected_datetime < datetime(1753, 1, 1) or selected_datetime > datetime(
                9999, 12, 31
            ):
                return False, "DATETIME must be between 1753-01-01 and 9999-12-31."

        elif self.column_details.DATA_TYPE == "smalldatetime":
            if selected_datetime < datetime(1900, 1, 1) or selected_datetime > datetime(
                2079, 6, 6
            ):
                return False, "SMALLDATETIME must be between 1900-01-01 and 2079-06-06."

        elif self.column_details.DATA_TYPE == "datetimeoffset":
            if selected_datetime < datetime(1753, 1, 1) or selected_datetime > datetime(
                9999, 12, 31
            ):
                return (
                    False,
                    "DATETIMEOFFSET must be between 1753-01-01 and 9999-12-31.",
                )

        return True, "Valid."


class StringWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details
        self.default_value = (
            self.column_details.COLUMN_DEFAULT[2:-2]
            if self.column_details.COLUMN_DEFAULT
            else ""
        )
        self.variable = tk.StringVar(value=self.default_value)
        self.entry = ttk.Entry(frame, textvariable=self.variable)

    def get_widget(self):
        return self.entry

    def grid(self, *args, **kwargs):
        self.entry.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.entry.pack(*args, **kwargs)

    def reset(self):
        self.variable.set(self.default_value)

    def get_value(self):
        return self.variable.get().strip()

    def validate(self):
        value = self.get_value()
        max_length = self.column_details.CHARACTER_MAXIMUM_LENGTH
        is_nullable = self.column_details.IS_NULLABLE == "YES"

        if not isinstance(value, str):
            return False, "Value must be a string."

        if value == "":
            if not is_nullable:
                return False, "This field cannot be empty."
            else:
                return True, "Valid."

        if max_length is not None and max_length != -1 and len(value) > max_length:
            return False, f"Length must not exceed {max_length} characters."

        return True, "Valid."


class SQLWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details
        self.default_value = (
            self.column_details.COLUMN_DEFAULT[2:-2]
            if self.column_details.COLUMN_DEFAULT
            else ""
        )
        self.variable = tk.StringVar(value=self.default_value)
        self.entry = ttk.Entry(frame, textvariable=self.variable)

    def get_widget(self):
        return self.entry

    def grid(self, *args, **kwargs):
        self.entry.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.entry.pack(*args, **kwargs)

    def reset(self):
        self.variable.set(self.default_value)

    def get_value(self):
        return self.variable.get().strip()

    def validate(self):
        value = self.get_value()
        is_nullable = self.column_details.IS_NULLABLE == "YES"

        if not is_nullable and (value == "" or value is None):
            return False, "This field cannot be empty."

        if value == "":
            return True, "Valid."

        return True, "Valid."


class IntegerWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details
        self.default_value = (
            self.column_details.COLUMN_DEFAULT[2:-2]
            if self.column_details.COLUMN_DEFAULT
            else ""
        )
        self.variable = tk.StringVar(value=self.default_value)
        self.entry = ttk.Entry(frame, textvariable=self.variable)

    def get_widget(self):
        return self.entry

    def grid(self, *args, **kwargs):
        self.entry.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.entry.pack(*args, **kwargs)

    def reset(self):
        self.variable.set(self.default_value)

    def get_value(self):
        value = self.variable.get().strip()
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def validate(self):
        value = self.get_value()
        if value is None:
            if self.column_details.IS_NULLABLE == "YES":
                return True, "Valid."
            else:
                return False, "This field accepts only integer values."

        if self.column_details.DATA_TYPE == "smallint":
            return self.validate_smallint(value)
        elif self.column_details.DATA_TYPE == "int":
            return self.validate_int(value)
        elif self.column_details.DATA_TYPE == "bigint":
            return self.validate_bigint(value)
        elif self.column_details.DATA_TYPE == "tinyint":
            return self.validate_tinyint(value)
        else:
            return self.validate_int(value)

    def validate_int(self, value, min_val=-2147483648, max_val=2147483647):
        if not isinstance(value, int):
            return False, "Value must be an integer."
        if value < min_val or value > max_val:
            return False, f"Value must be between {min_val} and {max_val}."
        return True, "Valid."

    def validate_tinyint(self, value):
        return self.validate_int(value, 0, 255)

    def validate_smallint(self, value):
        return self.validate_int(value, -32768, 32767)

    def validate_bigint(self, value):
        return self.validate_int(value, -9223372036854775808, 9223372036854775807)


class BinaryEntryWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details
        self.default_value = (
            self.column_details.COLUMN_DEFAULT[2:-2]
            if self.column_details.COLUMN_DEFAULT
            else ""
        )
        self.variable = tk.StringVar(value=self.default_value)
        self.entry = ttk.Entry(frame, textvariable=self.variable)

    def get_widget(self):
        return self.entry

    def grid(self, *args, **kwargs):
        self.entry.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.entry.pack(*args, **kwargs)

    def reset(self):
        self.variable.set(self.default_value)

    def get_user_input(self):
        return self.variable.get().strip()

    def get_value(self):
        is_valid, message = self.validate()
        if is_valid:
            return message
        else:
            return None

    def validate(self):
        value = self.get_user_input()
        max_length = self.column_details.CHARACTER_MAXIMUM_LENGTH
        data_type = self.column_details.DATA_TYPE
        is_nullable = self.column_details.IS_NULLABLE == "YES"

        if not value:
            if is_nullable:
                return True, "Valid."
            else:
                return False, "This field cannot be empty."

        if data_type in ["binary", "varbinary"]:
            return self.validate_binary_data(value, max_length)
        else:
            return False, "Unsupported data type."

    def validate_binary_data(self, value, max_length):
        try:
            binary_data = None

            if all(c in "0123456789abcdefABCDEF" for c in value):
                binary_data = self.hex_to_binary(value)
            elif all(c in "01" for c in value):
                binary_data = self.binary_string_to_binary(value)
            else:
                return (
                    False,
                    "Input is neither a valid hexadecimal nor a binary string.",
                )

            if (
                max_length is not None
                and max_length != -1
                and len(binary_data) > max_length
            ):
                return (
                    False,
                    f"Binary data exceeds maximum length of {max_length} bytes.",
                )

            return True, binary_data

        except Exception as e:
            return False, str(e)

    def hex_to_binary(self, value):
        try:
            binary_data = binascii.unhexlify(value)
            return binary_data
        except binascii.Error:
            return False, "Error converting hexadecimal to binary."

    def binary_string_to_binary(self, value):
        try:
            binary_data = int(value, 2).to_bytes((len(value) + 7) // 8, byteorder="big")
            return binary_data
        except ValueError:
            return False, "Invalid binary string."


class BooleanWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details
        self.default_value = (
            ("YES" if self.column_details.COLUMN_DEFAULT[2:-2] == "1" else "NO")
            if self.column_details.COLUMN_DEFAULT
            else ""
        )
        self.variable = tk.StringVar(value=self.default_value)
        self.entry = ttk.Combobox(
            frame, textvariable=self.variable, values=["YES", "NO"], state="readonly"
        )

    def get_widget(self):
        return self.entry

    def grid(self, *args, **kwargs):
        self.entry.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.entry.pack(*args, **kwargs)

    def reset(self):
        self.variable.set(self.default_value)

    def get_value(self):
        value = self.variable.get().strip()
        if value == "YES":
            return 1
        elif value == "NO":
            return 0
        return None

    def validate(self):
        value = self.variable.get().strip()

        if self.column_details.IS_NULLABLE == "YES" and value == "":
            return True, "Valid."

        if value not in ["YES", "NO"]:
            return False, "Please select 'YES' or 'NO'."

        return True, "Valid."


class FloatWidget:
    def __init__(self, frame, column_details):
        self.frame = frame
        self.column_details = column_details
        self.default_value = (
            self.column_details.COLUMN_DEFAULT[2:-2]
            if self.column_details.COLUMN_DEFAULT
            else ""
        )
        self.variable = tk.StringVar(value=self.default_value)
        self.entry = ttk.Entry(self.frame, textvariable=self.variable)

    def get_widget(self):
        return self.entry

    def grid(self, *args, **kwargs):
        self.entry.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.entry.pack(*args, **kwargs)

    def reset(self):
        self.variable.set(self.default_value)

    def get_value(self):
        return self.variable.get().strip()

    def validate(self):
        data_type = self.column_details.DATA_TYPE.lower()
        precision = self.column_details.NUMERIC_PRECISION
        scale = self.column_details.NUMERIC_SCALE
        value = self.get_value()

        if data_type in ["decimal", "numeric"]:
            return self.validate_decimal(value, precision, scale)
        elif data_type == "money":
            return self.validate_money(value)
        elif data_type == "smallmoney":
            return self.validate_smallmoney(value)
        elif data_type == "float":
            return self.validate_float(value)
        elif data_type == "real":
            return self.validate_real(value)
        else:
            return False, f"Unsupported data type: {data_type}"

    def validate_decimal(self, value, precision, scale):
        if not self.is_number(value):
            return False, "Value must be a number."

        str_value = str(value)
        if "." in str_value:
            integer_part, decimal_part = str_value.split(".")
        else:
            integer_part, decimal_part = str_value, ""

        if len(integer_part + decimal_part) > precision:
            return False, f"Total number of digits must not exceed {precision}."

        if len(decimal_part) > scale:
            return False, f"Decimal places must not exceed {scale}."

        return True, "Valid."

    def validate_money(self, value):
        try:
            val = float(value)
            print(val)
        except ValueError:
            return False, "Value must be a valid monetary amount."

        return self.validate_decimal(value, precision=19, scale=4)

    def validate_smallmoney(self, value):
        try:
            val = float(value)
            print(val)
        except ValueError:
            return False, "Value must be a valid monetary amount."

        return self.validate_decimal(value, precision=10, scale=4)

    def validate_float(self, value, precision=53):
        try:
            val = float(value)
            print(val)
        except ValueError:
            return False, "Value must be a valid float."

        return True, "Valid."

    def validate_real(self, value):
        return self.validate_float(value, precision=24)

    @staticmethod
    def is_number(value):
        try:
            float(value)
            return True
        except ValueError:
            return False


class JsonWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details
        self.default_value = (
            self.column_details.COLUMN_DEFAULT[2:-2]
            if self.column_details.COLUMN_DEFAULT
            else ""
        )
        self.variable = tk.StringVar(value=self.default_value)
        self.entry = ttk.Entry(frame, textvariable=self.variable)

    def get_widget(self):
        return self.entry

    def grid(self, *args, **kwargs):
        self.entry.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.entry.pack(*args, **kwargs)

    def reset(self):
        self.variable.set(self.default_value)

    def get_value(self):
        return self.variable.get().strip()

    def validate(self):
        allow_null = self.column_details.IS_NULLABLE
        value = self.get_value()

        if not allow_null and (value is None or value == ""):
            return False, "Value cannot be NULL or empty."

        max_length = self.column_details.CHARACTER_MAXIMUM_LENGTH
        if max_length is not None and max_length != -1 and len(value) > max_length:
            return False, f"Value exceeds maximum length of {max_length} characters."

        if value:
            try:
                json.loads(value)
            except ValueError as e:
                return False, f"Invalid JSON format: {e}"

        return True, "Valid."


class XmlWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details
        self.default_value = (
            self.column_details.COLUMN_DEFAULT[2:-2]
            if self.column_details.COLUMN_DEFAULT
            else ""
        )
        self.variable = tk.StringVar(value=self.default_value)
        self.entry = ttk.Entry(frame, textvariable=self.variable)

    def get_widget(self):
        return self.entry

    def grid(self, *args, **kwargs):
        self.entry.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.entry.pack(*args, **kwargs)

    def reset(self):
        self.variable.set(self.default_value)

    def get_value(self):
        return self.variable.get().strip()

    def validate(self):
        allow_null = self.column_details.IS_NULLABLE
        value = self.get_value()

        if not allow_null and (value is None or value == ""):
            return False, "Value cannot be NULL or empty."

        max_length = self.column_details.CHARACTER_MAXIMUM_LENGTH
        if max_length is not None and max_length != -1 and len(value) > max_length:
            return False, f"Value exceeds maximum length of {max_length} characters."

        if value:
            try:
                ET.fromstring(value)
            except ET.ParseError as e:
                return False, f"Invalid XML format: {e}"

        return True, "Valid."


class UUIDWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details
        self.default_value = (
            self.column_details.COLUMN_DEFAULT[2:-2]
            if self.column_details.COLUMN_DEFAULT
            else ""
        )
        self.variable = tk.StringVar(value=self.default_value)
        self.entry = ttk.Entry(frame, textvariable=self.variable)

    def get_widget(self):
        return self.entry

    def grid(self, *args, **kwargs):
        self.entry.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.entry.pack(*args, **kwargs)

    def reset(self):
        self.variable.set(self.default_value)

    def get_value(self):
        return self.variable.get().strip()

    def validate(self):
        allow_null = self.column_details.IS_NULLABLE
        value = self.get_value()

        if not allow_null and (value is None or value == ""):
            return False, "Value cannot be NULL or empty."

        max_length = self.column_details.CHARACTER_MAXIMUM_LENGTH
        if max_length is not None and len(value) > max_length:
            return False, f"Value exceeds maximum length of {max_length} characters."

        if value:
            try:
                uuid.UUID(str(value))
                return True, "Valid."
            except ValueError:
                return False, "Value must be a valid UUID."

        return True, "Valid."


class GeometryWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details
        default_value = (
            self.column_details.COLUMN_DEFAULT[2:-2]
            if self.column_details.COLUMN_DEFAULT
            else ""
        )
        pattern = r"STGeomFromText\('POINT\((\-?\d+ \-?\d+)\)', (\d+)\)"

        geometry_match = re.search(pattern, default_value)
        if geometry_match:
            self.coordinates = geometry_match.group(1).split()
        else:
            self.coordinates = (0, 0)

        self.frame = ttk.Frame(frame, style="Primary.TFrame")
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(3, weight=1)

        self.x_var = tk.StringVar(value=self.coordinates[0])
        self.y_var = tk.StringVar(value=self.coordinates[1])

        label = ttk.Label(self.frame, style="Small_Bold.TLabel", text="X : ")
        label.grid(row=0, column=0, padx=(2), sticky="we")

        x = ttk.Entry(self.frame, textvariable=self.x_var)
        x.grid(row=0, column=1, padx=(2), sticky="we")

        label = ttk.Label(self.frame, style="Small_Bold.TLabel", text="Y : ")
        label.grid(row=0, column=2, padx=(2), sticky="we")

        y = ttk.Entry(self.frame, textvariable=self.y_var)
        y.grid(row=0, column=3, padx=(2), sticky="we")

    def get_widget(self):
        return self.frame

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def reset(self):
        self.x_var.set(self.coordinates[0])
        self.y_var.set(self.coordinates[1])

    def get_value(self):
        x_value = self.x_var.get().strip()
        y_value = self.y_var.get().strip()

        if x_value == "" or y_value == "":
            return ""

        return f"geometry::STGeomFromText('POINT({x_value} {y_value})', 0)"

    def validate(self):
        allow_null = self.column_details.IS_NULLABLE
        value = self.get_value()

        if not allow_null and (value is None or value == ""):
            return False, "Value cannot be NULL or empty."

        max_length = self.column_details.CHARACTER_MAXIMUM_LENGTH
        if max_length is not None and max_length != -1 and len(value) > max_length:
            return False, f"Value exceeds maximum length of {max_length} characters."

        if value:
            pattern = r"^geometry::STGeomFromText\('POINT\((-?\d+(\.\d+)? -?\d+(\.\d+)?)\)', 0\)$"
            if not re.match(pattern, value):
                return False, "Invalid Geometry format. Expected format: POINT(x y)"

        return True, "Valid."


class GeographyWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details

        self.frame = ttk.Frame(frame, style="Primary.TFrame")
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(3, weight=1)

        self.longitude_var = tk.StringVar()
        self.latitude_var = tk.StringVar()

        label = ttk.Label(self.frame, style="Small_Bold.TLabel", text="Longitude: ")
        label.grid(row=0, column=0, padx=(2), sticky="we")
        longitude = ttk.Entry(self.frame, textvariable=self.longitude_var)
        longitude.grid(row=0, column=1, padx=(2), sticky="we")

        label = ttk.Label(self.frame, style="Small_Bold.TLabel", text="Latitude: ")
        label.grid(row=0, column=2, padx=(2), sticky="we")
        latitude = ttk.Entry(self.frame, textvariable=self.latitude_var)
        latitude.grid(row=0, column=3, padx=(2), sticky="we")

    def get_widget(self):
        return self.frame

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def reset(self):
        self.longitude_var.set(0)
        self.latitude_var.set(0)

    def get_value(self):
        longitude_value = self.longitude_var.get().strip()
        latitude_value = self.latitude_var.get().strip()

        if longitude_value == "" or latitude_value == "":
            return ""

        return f"geography::Point({longitude_value}, {latitude_value}, 4326)"

    def validate(self):
        allow_null = self.column_details.IS_NULLABLE
        value = self.get_value()

        if not allow_null and (value is None or value == ""):
            return False, "Value cannot be NULL or empty."

        max_length = self.column_details.CHARACTER_MAXIMUM_LENGTH
        if max_length is not None and max_length != -1 and len(value) > max_length:
            return False, f"Value exceeds maximum length of {max_length} characters."

        if value:
            pattern = (
                r"^geography::Point\((-?\d+(\.\d+)?) ?, ?(-?\d+(\.\d+)?) ?, ?(4326)\)$"
            )
            if not re.match(pattern, value):
                return (
                    False,
                    "Invalid Geography format. Expected format: Point(longitude, latitude)",
                )

        return True, "Valid."


class ImageWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details
        self.variable = None
        self.file_path = None
        self.button = ttk.Button(
            frame, text="Select an Image", command=self.open_file_dialog
        )

    def get_widget(self):
        return self.button

    def grid(self, *args, **kwargs):
        self.button.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.button.pack(*args, **kwargs)

    def reset(self):
        self.variable = None
        self.button.config(text="Select an Image")

    def open_file_dialog(self):
        self.file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.tiff")],
        )
        if self.file_path:
            if self.validate():
                self.load_image()

    def validate(self):
        allow_null = self.column_details.IS_NULLABLE == "YES"
        value = self.get_value()

        if not allow_null and (value is None or value == ""):
            return False, "Value cannot be NULL or empty."
        if value:
            try:
                img = Image.open(self.file_path)
                img.verify()
                return True, "Image Verified"
            except (IOError, SyntaxError) as e:
                return False, f"Invalid Image, Selected file is not a valid image: {e}"

        return True, "Valid."

    def load_image(self):
        with open(self.file_path, "rb") as img_file:
            self.variable = f"0x{img_file.read().hex()}"

        self.button.config(text=self.file_path.split("/")[-1])

    def get_value(self):
        return self.variable


class BinaryFileWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details
        self.variable = None
        self.file_path = None
        self.button = ttk.Button(
            frame, text="Select a File", command=self.open_file_dialog
        )

    def get_widget(self):
        return self.button

    def grid(self, *args, **kwargs):
        self.button.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.button.pack(*args, **kwargs)

    def reset(self):
        self.variable = None
        self.file_path = None
        self.button.config(text="Select a File")

    def open_file_dialog(self):
        self.file_path = filedialog.askopenfilename(title="Select a File")
        if self.file_path:
            self.load_binary()
        else:
            self.button.config(text="Invalid File Selected")

    def validate(self):
        allow_null = self.column_details.IS_NULLABLE == "YES"
        max_length = self.column_details.CHARACTER_MAXIMUM_LENGTH or -1
        value = self.get_value() or ""

        if not allow_null and not self.file_path:
            return False, "Value cannot be NULL or empty."

        if max_length is not None and max_length != -1 and len(value) > max_length:
            return False, f"Value exceeds maximum length of {max_length} characters."

        try:
            file_size = os.path.getsize(self.file_path)
            if file_size == 0:
                return False, "Selected file is empty."
            return True, "Valid file selected."
        except (OSError, IOError) as e:
            return False, f"File error: {e}"

        return True, "No file path specified."

    def load_binary(self):
        with open(self.file_path, "rb") as file:
            self.variable = f"0x{file.read().hex()}"
        self.button.config(text=os.path.basename(self.file_path))

    def get_value(self):
        return self.variable


class HierarchyWidget:
    def __init__(self, frame, column_details):
        self.column_details = column_details
        self.default_value = (
            self.column_details.COLUMN_DEFAULT[2:-2]
            if self.column_details.COLUMN_DEFAULT
            else ""
        )
        self.variable = tk.StringVar(value=self.default_value)
        self.entry = ttk.Entry(frame, textvariable=self.variable)

    def get_widget(self):
        return self.entry

    def grid(self, *args, **kwargs):
        self.entry.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.entry.pack(*args, **kwargs)

    def reset(self):
        self.variable.set(self.default_value)

    def get_value(self):
        return self.variable.get().strip()

    def validate(self):
        value = self.get_value()
        max_length = self.column_details.CHARACTER_MAXIMUM_LENGTH
        is_nullable = self.column_details.IS_NULLABLE == "YES"

        if not isinstance(value, str):
            return False, "Value must be a string."

        if value == "":
            if not is_nullable:
                return False, "This field cannot be empty."
            else:
                return True, "Valid."

        if max_length is not None and max_length != -1 and len(value) > max_length:
            return False, f"Length must not exceed {max_length} characters."

        if not (value.startswith("/") and value.endswith("/")):
            return False, "Input string must start and end with '/'."

        trimmed_string = value.strip("/")
        parts = trimmed_string.split("/")
        for part in parts:
            if part == "":
                return False, "Input string cannot have empty segments."

        if not all(part.isdigit() for part in parts):
            return False, "All segments must be numeric."

        return True, "Valid SqlHierarchyId."


class ComponentStyle(ttk.Style):
    def __init__(self, root):
        super().__init__(root)

        # Frame Styles
        # --------------
        self.configure("Primary.TFrame", background="white")
        self.configure(
            "Border.TFrame", background="white", borderwidth=1, relief="ridge"
        )
        self.configure("Back.TFrame", background="#05B2DC")

        # Button Styles
        # --------------
        self.configure(
            "Custom.TButton",
            width=15,
            font=("Helvetica", 10, "bold"),
            padding=3,
        )

        # Entry Styles
        # -------------
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
        # ----------------
        self.configure(
            "Treeview.Heading",
            background="white",
            foreground="#08158c",
        )
        self.configure("Treeview", rowheight=23)

        # Label Styles
        # -------------
        self.configure(
            "Normal.TLabel",
            foreground="black",
            background="white",
            font=("Helvetica", 10),
        )
        self.configure(
            "Normal_Bold.TLabel",
            foreground="black",
            background="white",
            font=("Helvetica", 10, "bold"),
        )
        self.configure(
            "Small.TLabel",
            foreground="black",
            background="white",
            font=("Helvetica", 9),
        )
        self.configure(
            "Small_Bold.TLabel",
            foreground="black",
            background="white",
            font=("Helvetica", 9, "bold"),
            padding=2,
        )
        self.configure(
            "Heading.TLabel",
            foreground="black",
            background="white",
            font=("Helvetica", 12, "bold"),
            padding=2,
        )
        # Seperator Styles
        # -----------------
        self.configure("Primary.TSeparator", background="#08158c")
