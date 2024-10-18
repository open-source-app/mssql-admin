import os
import env_file
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # If not running as a PyInstaller executable, use the directory of the script
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def center_window(window, width, height, top=False):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_coordinate = (screen_width - width) // 2 - 8
    if top:
        y_coordinate = 10
    else:
        y_coordinate = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

DEBUG = env_file.DEBUG
API = env_file.API

CAMERA = env_file.CAMERA
FRAME_RATE = 30

STATIC = resource_path("resources/")

#print(f"location - {STATIC}\n{os.listdir(STATIC)}")

BACKGROUND_COLOR = "#FFFFFF"
FOREGROUND_COLOR = "#0089CF"
WHITE = "#ffffff"
BLACK = "#000000"
BLUE = "#0089CF"
D_BLUE = "#015784"
APL_BLUE = "#0089CF"
RED = "#C0392B"
GREEN = "#08A53C"
GREY = "#CCD1D1"
YELLOW = "#60C209"
LIGHT_YELLOW = "#F9E79F"

ALERT1 = "#2E86C1"
ALERT2 = "#F1C40F"

if not CAMERA:
    FIRST_CAMERA = 0
    SECOND_CAMERA = 0
else:
    FIRST_CAMERA = env_file.FIRST_CAMERA
    SECOND_CAMERA = env_file.SECOND_CAMERA


def full_path(file_name):
    return f"{STATIC}{file_name}"

