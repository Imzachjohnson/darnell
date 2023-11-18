import io
import os
import base64
import requests
from PIL import Image
from pyexiv2 import Image as MetaImage
import typer
import pygetwindow as gw
import pyautogui
from PIL import Image

import pyautogui
from PIL import Image
import base64

def capture_active_window(output_path):
    """
    Captures a screenshot of the active window and saves it to the specified output path.

    Parameters:
    - output_path (str): The path where the screenshot will be saved.

    Returns:
    - str: The base64 representation of the captured image.
    """

    # Get the current active window
    window = gw.getActiveWindow()

    # Get the coordinates of the window
    left, top = window.topleft
    right, bottom = window.bottomright

    # Take a screenshot of the current active window only
    pyautogui.screenshot(output_path)

    # Crop the image to the coordinates of the window
    image = Image.open(output_path)
    image = image.crop((left, top, right, bottom))
    image.save(output_path)

    # Convert the image to base64
    with open(output_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    return base64_image



def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
