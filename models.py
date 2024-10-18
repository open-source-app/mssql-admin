from tkinter import PhotoImage
from settings import full_path
import hashlib
import os
import logging
from datetime import datetime
import socket
from ping3 import ping
from typing import Any
import serial
from tkinter import PhotoImage
from pymodbus.client import ModbusTcpClient
from settings import full_path


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

class PlazaDetails:
    def __init__(self, plaza_details):
        _attributes = ['id', 'name', 'authority', 'ip', 'sub_type', 'type', 'address', 'from_district', 'to_district', 'agency_code']
        for index, _attr in enumerate(_attributes):
            setattr(self, _attr, plaza_details[index] if len(plaza_details) > index else '')

class LaneDetails:
    def __init__(self, plaza_details):
        _attributes = ['id', 'name', 'authority', 'ip', 'sub_type', 'type', 'address', 'from_district', 'to_district', 'agency_code']
        for index, _attr in enumerate(_attributes):
            setattr(self, _attr, plaza_details[index] if len(plaza_details) > index else '')

class Objectify:
    def __init__(self, object_data: dict = {}):
        if not isinstance(object_data, dict):
            raise Exception("Dictionary expected")
        else:
            for key, value in object_data.items():
                setattr(self, key, value)

class ValueSetter:
    def __init__(self, columns, values):
        for index,column in enumerate(columns):
            setattr(self, column, values[index] if len(values)>index else '')

    def __getattribute__(self, attr):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            try:
                keys = {i.lower():i for i in self.__dict__}
                return super().__getattribute__(keys.get(attr))
            except AttributeError:
                return ""

class TkImages:
    def __init__( self, active_image="setup.png", inactive_image="setup.png", disconnected_image="setup.png", subsample=10,):
        self.subsample = subsample
        self.active_image = PhotoImage(file=full_path(active_image)).subsample(self.subsample)
        self.inactive_image = PhotoImage(file=full_path(inactive_image)).subsample(self.subsample)
        self.disconnected_image = PhotoImage(file=full_path(disconnected_image)).subsample(self.subsample)

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

class Device(CustomImages):
    def __init__(self, name="Server", ip="192.168.1.10", **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.device = self
        self.ip = ip
        self.read = False
        self.connected = False

    def is_online(self):
        result = ping(self.ip)
        if isinstance(result, float):
            self.connected = True
            self.read = True
        else:
            self.connected = False
            self.read = False

class PLC(ModbusTcpClient):
    def __init__(self, ip, retries=1, timeout=2):
        super().__init__(
            ip,
            timeout=timeout,
            retry_on_empty=False,
            close_comm_on_error=False,
            retries=retries,
        )

    def try_connecting(self):
        try:
            print("**Attempting to connect PLC in a thread**")
            if self.connected:
                print("**Connected to PLC successfully**")
            else:
                self.connect()
                print("**Failed to connect to PLC**")
        except Exception as e:
            print(f"Connection failed due to {e}")

        connection_thread = threading.Thread(target=self._connect_in_thread)
        connection_thread.start()

    def disconnect(self):
        if self.connected:
            self.close()
            print("**Disconnected from PLC**")

class ModbusDevice(CustomImages):
    logger: CustomLogger = CustomLogger

    def __init__(
        self,
        device: PLC = PLC,
        name: str = "Device",
        address: str = "0.0.0.0",
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.name = name
        self.address = address
        self._read = None
        self.device = device

    @property
    def read(self):
        # print(self.device.client, self.device.is_connected, self.device.is_plc_online)
        if (self.device.connected and self.device.is_online):
            try:
                # print(self.device.client.read_coils(self.address, 1))
                return self.device.client.read_coils(self.address, 1).bits[0]
            except Exception as e:
                print("\n ModbusDevice read error : ", self.name, e)
                return False
        else:
            return False

    def write(self, value=0, logger: CustomLogger = None):
        if self.device and self.device.is_connected:
            self.device.client.write_coil(self.address, value)
            if logger:
                if value:
                    logger.info(f"Activating - {self.name}")
                else:
                    logger.info(f"Deactivating - {self.name}")
        else:
            if logger:
                logger.info(f"Trying to modify {self.name} - PLC not Connected")


class COMPortDevice(CustomImages):
    def __init__(self, name: str = "Device", port="COM2", baudrate=9600, **kwargs: Any):
        super().__init__(**kwargs)
        self.name = name
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.read = False
        self.is_connected = False

    def connect(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate)
            print(f"\n\nConnected to {self.port}")
            self.is_connected = True
            return True
        except serial.SerialException:
            print(f"Failed to connect to {self.port}")
            self.is_connected = False
            return False

    def disconnect(self):
        if self.serial:
            self.serial.close()

    def log_data(self, logger, msg=None):
        logger.info(f"Writing On UFD - {msg}")

    def write_full_still(self, data, logger: CustomLogger = None):
        if self.serial:
            self.serial.write(f"|C|4|1|{data}|1|7|\n".encode())
            self.log_data(logger, data)

    def write_full_moving(self, data, logger: CustomLogger = None):
        if self.serial:
            self.serial.write(f"|C|4|2|{data}|1|7| \n".encode())
            self.log_data(logger, data)

    def write_top_still(self, data, logger: CustomLogger = None):
        if self.serial:
            self.serial.write(f"|C|4|1|{data}|1|8| \n".encode())
            self.log_data(logger, data)

    def write_top_moving(self, data, logger: CustomLogger = None):
        if self.serial:
            self.serial.write(f"|C|4|2|{data}|1|8| \n".encode())
            self.log_data(logger, data)

    def write_below_still(self, data, logger: CustomLogger = None):
        if self.serial:
            self.serial.write(f"|C|4|1|0-8-{data}|1|8| \n".encode())
            self.log_data(logger, data)

    def write_below_moving(self, data, logger: CustomLogger = None):
        if self.serial:
            self.serial.write(f"|C|4|2|0-8-{data}|1|8| \n".encode())
            self.log_data(logger, data)

    def clear_screen(self, logger: CustomLogger = None):
        if self.serial:
            self.serial.write("|C|6| \n".encode())
            self.log_data(logger)

    def delete_messages(self, logger: CustomLogger = None):
        if self.serial:
            self.serial.write("|C|7| \n".encode())
            self.log_data(logger)

    def receive_data(self):
        if self.serial:
            return self.serial.read_all()
        return None


class VehicleClass:
    def __init__(
        self,
        vehicle_id,
        vehicle_desc,
        is_active,
        passing_weight,
        over_weight_amount,
        vehicle_image,
    ):
        self.VehicleID = vehicle_id
        self.VehicleDescription = vehicle_desc
        self.IsActive = is_active
        self.PassingWeight = passing_weight
        self.OverWeightAmount = over_weight_amount
        self.VehicleImage = vehicle_image


class Vehicle:
    def __init__(self):
        self.vehicle_classs = None
        self.journey_type = None
        self.licence_plate_number = None
        self.exempt_category = None
        self.axel_count = None
        self.rfid_tag = None
        self.weight = None
        self.toll_fee = None
        self.payment_method = None


class HardwareDevice:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.connection = None
        self.data_buffer = b""
        self.timeout = 10  # Default timeout

    def connect(self):
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.settimeout(self.timeout)
            self.connection.connect((self.ip_address, self.port))
        except (socket.error, socket.timeout) as e:
            print(f"Connection error: {e}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    @property
    def is_connected(self):
        return self.connection is not None

    def send_data(self, data):
        try:
            self.connection.send(data)
        except (socket.error, socket.timeout) as e:
            print(f"Send data error: {e}")

    def receive_data(self, buffer_size):
        try:
            data = self.connection.recv(buffer_size)
            self.data_buffer += data
            return data
        except (socket.error, socket.timeout) as e:
            print(f"Receive data error: {e}")

    def clear_data_buffer(self):
        self.data_buffer = b""

    def set_timeout(self, timeout):
        self.timeout = timeout
        if self.connection:
            self.connection.settimeout(self.timeout)


class VehicleClass:
    def __init__(
        self, name, identifier, status, toll_fare, passing_weight, current_weight
    ):
        self.name = name
        self.identifier = identifier
        self.status = status
        self.toll_fare = toll_fare
        self.passing_weight = passing_weight
        self.current_weight = current_weight

    def __repr__(self):
        return f"VehicleClass(name={self.name}, identifier={self.identifier}, status={self.status}, passing_weight={self.passing_weight}, current_weight={self.current_weight})"


class JourneyClass:
    def __init__(self, name, deactivated, exempt):
        self.name = name
        self.deactivated = deactivated
        self.exempt = exempt

    def __repr__(self):
        return f"JourneyClass = {self.name}"


class ExemptClass:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"ExemptClass = {self.name}"


class TransactionData:
    def __init__(self, row):
        self.trans_id = row[0]
        self.avc_class = row[1]
        self.fast_tag_id = row[2]
        self.plate_number = row[3]
        self.amount = str(row[4])  # Convert Decimal to string
        self.datetime = row[5].strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # Convert datetime to formatted string

    def get_data_list(self):
        return [
            self.trans_id,
            self.avc_class,
            self.fast_tag_id,
            self.plate_number,
            self.amount,
            self.datetime,
        ]


class LaneConfiguration:
    def __init__(
        self,
        toll_name,
        contractor,
        static_ip_one,
        static_ip_two,
        bank_name,
        lane_id,
        lane_number,
        lane_side,
        server_ip,
        lpic_ip,
        ic_ip,
        rfid_ip,
        wim_port,
        ufd_port,
        plc_ip,
        plc_ports,
        avc_port,
        ohls_status,
        traffic_light_status,
        barrier_status,
        violation_status,
    ):
        self.toll_name = toll_name
        self.contractor = contractor
        self.static_ip_one = static_ip_one
        self.static_ip_two = static_ip_two
        self.bank_name = bank_name
        self.lane_id = lane_id
        self.lane_number = lane_number
        self.lane_side = lane_side
        self.server_ip = server_ip
        self.lpic_ip = lpic_ip
        self.ic_ip = ic_ip
        self.rfid_ip = rfid_ip
        self.wim_port = wim_port
        self.ufd_port = ufd_port
        self.plc_ip = plc_ip
        self.plc_ports = plc_ports
        self.avc_port = avc_port
        self.ohls_status = ohls_status
        self.traffic_light_status = traffic_light_status
        self.barrier_status = barrier_status
        self.violation_status = violation_status


class TransactionProcess:
    in_progress = False
    is_completed = False
    is_paid = False

    image_captured = False
    video_captured = False

    vehicle_detected_on_present_loop = False
    vehicle_passed_present_loop = False

    vehicle_detected_on_exit_loop = False
    vehicle_passed_exit_loop = False

    vehicle_image_taken = False
    vehicle_video_taken = False

    is_fleet = False
    is_convoy = False
    vehicle_count = 0

    @classmethod
    def add_vehicle(cls):
        cls.vehicle_count += 1

    @classmethod
    def reset_transaction(cls):
        cls.in_progress = False
        cls.is_completed = False
        cls.is_paid = False

        cls.image_captured = False
        cls.video_captured = False

        cls.vehicle_detected_on_present_loop = False
        cls.vehicle_passed_present_loop = False

        cls.vehicle_detected_on_exit_loop = False
        cls.vehicle_passed_exit_loop = False

        cls.vehicle_image_taken = False
        cls.vehicle_video_taken = False

        cls.is_fleet = False
        cls.is_convoy = False
        cls.vehicle_count = 0


class User(ValueSetter):
    def __init__(self, user):
        super().__init__(user.columns, user.values)

    def hash_password(self, password_to_hash):
        salted_password = self.GID + password_to_hash
        hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
        return hashed_password

    def verify_password(self, password_to_verify):
        expected_hashed_password = self.hash_password(password_to_verify)
        return self.Password == expected_hashed_password

    def __repr__(self):
        return f'{self.First_Name} - {self.Last_Name}'

"""
if vehicle_detected_on_present_loop:
    transaction.vehicle_detected_on_present_loop = True
    transaction.in_progress = True

if vehicle_not_on_present_loop:
    if transaction.vehicle_detected_on_present_loop:
        if not transaction.is_paid:
            transaction.reset_transaction()
            return
        transaction.vehicle_detected_on_present_loop = False
        transaction.vehicle_passed_present_loop = True

if vehicle_detected_on_exit_loop:
    if transaction.vehicle_passed_present_loop:
        if not transaction.is_paid:
            self.run_violation()

        transaction.vehicle_detected_on_exit_loop = True

if vehicle_passed_exit_loop:
    if transaction.vehicle_detected_on_exit_loop:
        transaction.vehicle_detected_on_exit_loop = False
        transaction.vehicle_passed_exit_loop = True
        self.reset_transaction()
"""

