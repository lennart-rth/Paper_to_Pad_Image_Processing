import cv2
import numpy as np
from pynput import keyboard

from imageProccessing import *
from gui import *
from perspective import *

import config


def nothing(e):
    pass

listener = keyboard.Listener(on_press=on_press)
listener.start()

cv2.namedWindow('main')
cv2.setMouseCallback('main',mouse_update)
cv2.createTrackbar('pen_color_min', 'main', 0, 100, nothing)
cv2.createTrackbar('pen_color_max', 'main', 0, 100, nothing)
cv2.createTrackbar('mouse_sensitivity', 'main', 1, 100, nothing)


# capture = cv2.VideoCapture("http://192.168.178.54:4747/video")
capture = cv2.VideoCapture("test.MOV")

if not capture.isOpened():
    print("Cannot open camera")
    exit()

while(True):
    ret, frame = capture.read()

    w = frame.shape[1]
    h = frame.shape[0]
    frame = cv2.resize(frame, (int((700/h)*w),700))
    # mask = cv2.resize(mask, (int((700/h)*w),700))

    frame_vis = frame.copy()    # a visual frame to draw all contours to

    # Image Processing and Pen-tip Tracking.
    mask = colormasking_pen(frame)
    smoothed_edges = smoothing_edges(mask)
    contour = find_convex_hull(smoothed_edges)

    if contour is not None:
        update_tracked_point(contour, frame_vis, mask, frame)

    # Perspective Warping to archiev Birseye View onto Paper
    if len(config.corners) == 4:
        try:
            cv2.destroyWindow("mask")
        except:
            pass
        
        warped_point = handle_perspective_change(frame_vis)
        config.old_pen_point = config.old_pen_point
        config.old_pen_point = warped_point
    else:
        try:
            cv2.destroyWindow("DinA4")
        except:
            pass
        
        # w = frame_vis.shape[1]
        # h = frame_vis.shape[0]
        # frame_vis = cv2.resize(frame_vis, (int((700/h)*w),700))
        # mask = cv2.resize(mask, (int((700/h)*w),700))
        
        cv2.imshow('main', frame_vis)

        if config.DEBUG:
            cv2.imshow('mask', mask)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    if key == ord('p'):
        cv2.waitKey(-1) #wait until any key is pressed
    if key == ord('a'):     #add a calibration for the pen
        calibrate(frame)
    if key == ord('c'):  #add a corner to transform to virtual birdview
        config.corners.append(config.mouse_pos)
    if key == ord('r'): #reset warping
        config.corners = []


capture.release()
cv2.destroyAllWindows()