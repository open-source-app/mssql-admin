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

class Objectifier:
    def __init__(self, data):
        if not type(data) == dict:
            print('dictionary data type required')
        else:
            for key, val in data.items():
                if type(val) == dict:
                    setattr(self, key, Objectifier(val))
                else:
                    setattr(self, key, val)

    def get(self, attr):
        return f'{getattr(self, attr)}'

    def __repr__(self):
        return f'{self.__dict__}'

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

