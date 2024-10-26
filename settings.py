import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

STATIC = resource_path("resources/")

def full_path(file_name):
    return f"{STATIC}{file_name}"

def center_window(window, width, height, top=False):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_coordinate = (screen_width - width) // 2 - 8
    if top:
        y_coordinate = 10
    else:
        y_coordinate = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

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


