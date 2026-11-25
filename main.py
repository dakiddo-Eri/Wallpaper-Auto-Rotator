import PIL
import ctypes
import os 
import random 

WIDTH, HEIGHT = 1920, 1080
OUTPUT_FILE = "daily_wallpaper.png"

def lerp_color(c1, c2, t):
    return (
        int(c1[0] * (1 - t) + c2[0] * t),
        int(c1[1] * (1 - t) + c2[1] * t),
        int(c1[2] * (1 - t) + c2[2] * t),
    )