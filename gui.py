import cv2
import numpy as np
from pynput import keyboard
from pynput.mouse import Button, Controller

import config

mouseController = Controller()

def mouse_update(event,x,y,flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        config.mouse_pos = (x,y)

def toogle_mouse_press():

    if not config.mouse_pressed:
        mouseController.press(Button.left)
        config.mouse_pressed = True
    else:
        mouseController.release(Button.left)
        config.mouse_pressed = False

def on_press(key):
    try:
        print(key.char)
    except AttributeError:
        if key == keyboard.Key.space:
            toogle_mouse_press()
        elif key == keyboard.Key.alt:
            config.drawing = not config.drawing

def calibrate(frame):
    ''' get the avg color on the mouseposition of a n*n square'''
    win_size = config.calibration_window

    x = config.mouse_pos[0]
    y = config.mouse_pos[1]

    win_x = max(x - win_size // 2, 0)
    win_y = max(y - win_size // 2, 0)
    win_width = min(win_size, frame.shape[1] - win_x)
    win_height = min(win_size, frame.shape[0] - win_y)
    win = frame[win_y:win_y + win_height, win_x:win_x + win_width]
    avg_pixel_values = cv2.mean(win)
    #colors = frame[y,x]

    config.calibration_pen = avg_pixel_values

def colormasking_pen(frame):
    min_val = cv2.getTrackbarPos('pen_color_min', 'main')
    max_val = cv2.getTrackbarPos('pen_color_max', 'main')

    if not config.DEBUG:
        color = config.calibration_pen
        config.lower = np.array(color)-min_val
        config.upper = np.array(color)+max_val

    # print(config.lower,config.upper)
    mask = cv2.inRange(frame, config.lower, config.upper )
    return mask

