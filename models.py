import os
import ast
import magic
import struct
import logging
import tkinter as tk
from datetime import datetime, time, date
from tkinter import ttk, filedialog, messagebox, PhotoImage
from tkcalendar import DateEntry
from settings import center_window, full_path


class CustomLogger:
    def __init__(self, file_name=__name__, log_dir="data"):
        self.log_dir = log_dir
        self._logger = self._setup_logger(file_name)

    def _setup_logger(self, file_name):
        logger = logging.getLogger(file_name)
        logger.setLevel(logging.DEBUG)

        current_date = datetime.now()
        log_date = current_date.strftime("%Y/%B/%d")
        # log_date = current_date.strftime("%H/%M/%S")

        log_subdir = os.path.join(self.log_dir, log_date)
        os.makedirs(log_subdir, exist_ok=True)

        info_handler = logging.FileHandler(os.path.join(log_subdir, "info.log"))
        error_handler = logging.FileHandler(os.path.join(log_subdir, "error.log"))

        formatter = logging.Formatter(
            "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%d-%b-%y %H:%M:%S",
        )

        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)

        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(info_handler)
        logger.addHandler(error_handler)

        return logger

    def debug(self, message):
        self._logger.debug(message)

    def info(self, message):
        self._logger.info(message)

    def error(self, message):
        self._logger.error(message)


class Objectifier:
    def __init__(self, data):
        if not isinstance(data, dict):
            print("dictionary data type required")
        else:
            for key, val in data.items():
                if isinstance(val, dict):
                    setattr(self, key, Objectifier(val))
                else:
                    setattr(self, key, val)

    def get(self, attr):
        return f"{getattr(self, attr)}"

    def __repr__(self):
        return f"{self.__dict__}"


class ValueSetter:
    def __init__(self, columns, values):
        for index, column in enumerate(columns):
            setattr(self, column, values[index] if len(values) > index else "")

    def __getattribute__(self, attr):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            try:
                keys = {i.lower(): i for i in self.__dict__}
                return super().__getattribute__(keys.get(attr))
            except AttributeError:
                return ""

class TkImages:
    def __init__(
        self,
        active_image="setup.png",
        inactive_image="setup.png",
        disconnected_image="setup.png",
        subsample=10,
    ):
        self.subsample = subsample
        self.active_image = PhotoImage(file=full_path(active_image)).subsample(
            self.subsample
        )
        self.inactive_image = PhotoImage(file=full_path(inactive_image)).subsample(
            self.subsample
        )
        self.disconnected_image = PhotoImage(
            file=full_path(disconnected_image)
        ).subsample(self.subsample)


class CustomImages:
    def __init__(
        self,
        active_image="setup.png",
        inactive_image="setup.png",
        disconnected_image="setup.png",
        subsample=10,
        x_axis=45,
        y_axis=10,
        show_image=True,
    ):
        self.active_image = full_path(active_image)
        self.inactive_image = full_path(inactive_image)
        self.disconnected_image = full_path(disconnected_image)
        self.subsample = subsample
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.show_image = show_image

    @property
    def get_active_image(self):
        image = PhotoImage(file=self.active_image)
        return image.subsample(self.subsample)

    @property
    def get_inactive_image(self):
        image = PhotoImage(file=self.inactive_image)
        return image.subsample(self.subsample)

    @property
    def get_disconnected_image(self):
        image = PhotoImage(file=self.disconnected_image)
        return image.subsample(self.subsample)

class OriginalData:
    def __init__(self, column_details):
        self.column_details = column_details
        self.default_value =  column_details.initial_value

    def get_value(self):
        return self.default_value

class BooleanData:
    def __init__(self, column_details):
        self.column_details = column_details
        self.default_value =  column_details.initial_value

    def get_value(self):
        value = self.default_value
        if value == "True":
            return 1
        elif value == "False":
            return 0

class GeometryData:
    def __init__(self, column_details):
        self.column_details = column_details
        self.default_value =  column_details.initial_value

        if self.default_value:
            self.coordinates = self.decode(self.default_value)
        else:
            self.coordinates = (0, 0)

        self.x_var = tk.StringVar(value=self.coordinates[0])
        self.y_var = tk.StringVar(value=self.coordinates[1])

    def decode(self, wkb_string):
        try:
            data = ast.literal_eval(wkb_string)
            srid, version, properties = struct.unpack('<IBB', data[:6])
            single_point_flag = properties & 0x08
            if not single_point_flag:
                raise ValueError("Not a single point. Complex geometries need different handling.")
            x, y = struct.unpack('<dd', data[6:22])
            return round(x, 3), round(y, 3)
        except: return 0, 0

    def get_value(self):
        x_value = self.x_var.get().strip()
        y_value = self.y_var.get().strip()

        if x_value == "" or y_value == "":
            return ""

        return f"geometry::STGeomFromText('POINT({x_value} {y_value})', 0)"

class GeographyData:
    def __init__(self, column_details):
        self.column_details = column_details

        self.default_value =  self.column_details.initial_value

        if self.default_value:
            self.coordinates = self.decode(self.default_value)
        else:
            self.coordinates = (0, 0)

        self.longitude_var = tk.StringVar(value=self.coordinates[0])
        self.latitude_var = tk.StringVar(value=self.coordinates[1])

    def get_value(self):
        longitude_value = self.longitude_var.get().strip()
        latitude_value = self.latitude_var.get().strip()

        if longitude_value == "" or latitude_value == "":
            return ""

        return f"geography::Point({longitude_value}, {latitude_value}, 4326)"

    def decode(self, wkb_string):
        try:
            data = ast.literal_eval(wkb_string)
            srid, version, properties = struct.unpack('<IBB', data[:6])
            single_point_flag = properties & 0x08
            if not single_point_flag:
                raise ValueError("Not a single point. Complex geometries need different handling.")
            x, y = struct.unpack('<dd', data[6:22])
            return round(x, 3), round(y, 3)
        except: return 0, 0

class ImageData:
    def __init__(self, column_details):
        self.column_details = column_details

        self.file_path = None

        self.default_value =  column_details.initial_value or (
            column_details.COLUMN_DEFAULT[2:-2]
            if column_details.COLUMN_DEFAULT
            else ""
        )
 
        try:
            self.image_bytes =  ast.literal_eval(self.default_value)
            self.variable = f"0x{self.image_bytes.hex()}"
        except: 
            self.variable = None
            self.image_bytes = None

    def get_value(self):
        return self.variable

class BinaryData:
    def __init__(self, column_details):
        self.column_details = column_details
        self.variable = None
        self.file_path = None
        self.mime = magic.Magic(mime=True)

        self.default_value =  column_details.initial_value or (
            column_details.COLUMN_DEFAULT[2:-2]
            if column_details.COLUMN_DEFAULT
            else ""
        )
 
        try:
            self.file_bytes =  ast.literal_eval(self.default_value)
            self.variable = f"0x{self.file_bytes.hex()}"
        except Exception as e: 
            self.file_bytes = None
            self.variable = None
            print(f'BinaryFileData Error :- {e}')

    def get_value(self):
        return self.variable

class HierarchyData:
    def __init__(self, column_details):
        self.column_details = column_details
        self.default_value = self.decode(ast.literal_eval(column_details.initial_value)) if column_details.initial_value else ''
        self.variable = tk.StringVar(value=self.default_value)

    def get_value(self):
        return self.variable.get().strip()

    def decode(self, binary_data):
        position = 0
        path = []
        padding = ""

        while position < len(binary_data):
            # Parse Li based on possible patterns and move position
            li = binary_data[position:position+2]  # Get the first 2 bits to check Li patterns
            position += 2

            if li == '01':
                oi = binary_data[position:position+2]  # Next 2 bits for Oi
                position += 2
                value = int(oi, 2)  # Integer value of Oi
                label = value + 0  # L1 range 0 to 3, add lower limit
            elif li == '111110':
                oi = binary_data[position:position+32]  # Oi for 32/36-bit range
                position += 32
                value = int(oi, 2)  # Integer value of Oi
                label = value + 5200  # L range 5200 to 4294972495
            else:
                # Add other cases according to hierarchy rules
                break

            # Add label to path
            path.append(label)

            # Parse Fi
            fi = binary_data[position:position+1]
            position += 1
            is_real = fi == '1'

            if is_real:
                path.append("/")  # Separator for real nodes
            else:
                path.append(".")  # Separator for fake nodes

            padding = binary_data[position:]
            position += len(padding)

        return f"/{''.join(map(str, path))}"

