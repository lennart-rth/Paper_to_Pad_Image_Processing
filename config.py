from collections import deque
import numpy as np

###Settings#####
DEBUG = True               #Use predefined Pen_color_calibration. Show a image of the Masking of the Pen 
point_smoothing = 1        #smoothe the tracked point movement (0-inf) the lower the less smoothing
lower = np.array([61.94,60.01,-15.5])       # hardset calibration for pen - lower color bound !!only used when DEBUG=True!!
upper = np.array([117.94,116.01,40.5])        # hardset calibration for pen - lower color bound !!only used when DEBUG=True!!
debug_corners = np.array([(221, 394), (754, 665), (946, 130), (575, 39)])

gaussian_blur = 37          # ksize for the gaussion The higher the more blur and the smoother are the edges of the colormask. Increase if pen tracking jiitters - decrease if tracking is unprecise
mask_threshold = 63         # defines the threshold to build a Bit-mask containing the pen. Higher values decrease the with of the recognized pen.

tip_detection = "slope"     # values are ["slope","shape"]. Use shape if slope if pen is not recognized reliable and you have a pen which chape of the tip is visually different from the top. eg. tip is shapened and top is rectangle with clip on the side.

calibration_window = 10  #size in pixel of your the area which is averaged to find calibrate the pen color

####Other variables! Dont touch!#####
drawing = False     #if the pen is tracked and the computer mouse is moved accordingly
mouse_pressed = False   #if the mouse is is pessed down

calibration_pen = [0,0,0]  #first init of the pen color

mouse_pos = None    # bosition of the mouse on the opencv_Frame (Gui interal)
filtered_position = [0,0]
old_pen_point = [0,0]
rolling_window = deque(maxlen=point_smoothing)    # smoothening the Movement of the mouse

corners = []        #list of corners calibrated by the user to Trasnform the Image to Birds View

if DEBUG:
    corners = debug_corners

