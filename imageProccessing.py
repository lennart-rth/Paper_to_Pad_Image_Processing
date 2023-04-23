import cv2
import numpy as np

import config

def smoothing_edges(mask):
    closing = cv2.GaussianBlur(mask, (config.gaussian_blur, config.gaussian_blur), 0)
    threshold_value = config.mask_threshold
    max_value = 255
    _, thresh = cv2.threshold(closing, threshold_value, max_value, cv2.THRESH_BINARY)

    kernel = np.ones((5,5),np.uint8)
    # closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    # cv2.imshow('closing1', closing

    closing = cv2.erode(thresh,kernel,iterations = 1)
    return closing

def find_convex_hull(smoothed_edges):
    contours, hierarchy = cv2.findContours(smoothed_edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

    points = [pt[0] for ctr in contours for pt in ctr]
    points = np.array(points).reshape((-1,1,2)).astype(np.int32)

    hull = cv2.convexHull(points)
    return hull

def get_points(frame, intersect,frame_vis):
    '''gets the intersection build by bitwise and and returns a list of points containg the center of every intercption'''
    intersect_contours, intersect_hierarchy = cv2.findContours(intersect,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(intersect,intersect_contours,-1,(0,255,0),1)
    points = []
    for intersetc in intersect_contours:
        moments = cv2.moments(intersetc)

        point = (round(moments['m10'] / moments['m00']), round(moments['m01'] / moments['m00']))

        cv2.circle(frame_vis, point, 3, (255, 0, 0), -1)        #draw intersection points aka pen tips
        points.append(point)

    if len(points) > 2:
        return None         # something went wrong if a pen has more than two ends
    
    return points

def find_pen_ends(frame,uni_hull,start_point,end_point,frame_vis):
    '''Takes the outline of the pen and the centerline and calcs a bitwise and to find areas where the contours overlap. Thus finding the positions where the Pen ends and starts
    Then calc the point of these areas and return them.'''
    try:
        kernel = np.ones((5,5),np.uint8)
        blank1 = np.zeros( frame.shape[0:2] , dtype="uint8")
        blank2 = np.zeros( frame.shape[0:2] , dtype="uint8")

        cv2.drawContours(blank1,uni_hull,-1,(255,255,255),1)
        cv2.line(blank2, start_point, end_point, (255, 255, 255), 1)

        intersect = cv2.bitwise_and(blank1,blank2)
        intersect = cv2.dilate(intersect,kernel,iterations = 1)

        points = get_points(frame,intersect,frame_vis)
        return points
    except:
        return None

def find_right_tip(frame,pen_tips,mask,start_point,end_point):
    """'Takes the area of the two tip candidates and processes them further. on a smaller area of the image the colorspace is more narrow, so it can be used to further define the tip.
     Also decide which tip is the one touching the paper. Either based on the slope of the Pen on the image, or the shape of the tip contour. 3 corners = right tipp more than 3 = wrong side """
    
    p1 = pen_tips[0]
    p2 = pen_tips[1]

    size = 30

    x10 = int(p1[0]-size)
    x11 = int(p1[0]+size)
    y10 = int(p1[1]-size)
    y11 = int(p1[1]+size)

    x20 = int(p2[0]-size)
    x21 = int(p2[0]+size)
    y20 = int(p2[1]-size)
    y21 = int(p2[1]+size)

    h = frame.shape[0]
    w = frame.shape[1]

    tip1_img = frame[in_b(y10,h):in_b(y11,h),in_b(x10,w):in_b(x11,w)]
    tip1_img = cv2.resize(tip1_img, (size*3, size*3))
    

    tip2_img = frame[in_b(y20,h):in_b(y21,h),in_b(x20,w):in_b(x21,w)]
    tip2_img = cv2.resize(tip2_img, (size*3, size*3))
    
    # min_val = cv2.getTrackbarPos('min', 'main')
    # max_val = cv2.getTrackbarPos('max', 'main')

    upper1 = config.upper+39
    tip1_mask = cv2.inRange(tip1_img, config.lower, upper1)
    tip1_mask = smoothing_edges(tip1_mask)

    tip2_mask = cv2.inRange(tip2_img, config.lower, upper1)
    tip2_mask = smoothing_edges(tip2_mask)

    kernel = np.ones((5,5),np.uint8)
    # tip1_mask = cv2.erode(tip1_mask,kernel,iterations = 1)
    # tip2_mask = cv2.erode(tip2_mask,kernel,iterations = 1)
    # cv2.imshow('tip1_mask1', tip1_mask)
    tip1_mask = cv2.morphologyEx(tip1_mask, cv2.MORPH_CLOSE, kernel)
    tip2_mask = cv2.morphologyEx(tip2_mask, cv2.MORPH_CLOSE, kernel)
    # cv2.imshow('tip1_mask2', tip1_mask)
    tip1_mask = cv2.morphologyEx(tip1_mask, cv2.MORPH_CLOSE, kernel)
    tip2_mask = cv2.morphologyEx(tip2_mask, cv2.MORPH_CLOSE, kernel)
    # cv2.imshow('tip1_mask3', tip1_mask)

    closing = cv2.GaussianBlur(mask, (37, 37), 0)
    threshold_value = 63
    max_value = 255
    _, tip1_mask = cv2.threshold(tip1_mask, threshold_value, max_value, cv2.THRESH_BINARY)
    # cv2.imshow('tip1_mask4', tip1_mask)

    tip1_mask = cv2.erode(tip1_mask,kernel,iterations = 2)
    tip2_mask = cv2.erode(tip2_mask,kernel,iterations = 2)

    # cv2.imshow('tip1_mask5', tip1_mask)
    # cv2.imshow('tip2_mask', tip2_mask)

    cnts1,_ = cv2.findContours(tip1_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts2,_ = cv2.findContours(tip2_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    tip_index = 1       # Method 1 to decide which tip is the one that writes
    try:
        # cv2.approxPloyDP() function to approximate the shape
        e = cv2.getTrackbarPos('a', 'main')
        approx1 = cv2.approxPolyDP(
            cnts1[0], 0.045 * cv2.arcLength(cnts1[0], True), True)
        
        # using drawContours() function
        # cv2.drawContours(tip1_img, [approx1], 0, (0, 0, 255), 2)

        # cv2.approxPloyDP() function to approximate the shape
        approx2 = cv2.approxPolyDP(
            cnts2[0], 0.045* cv2.arcLength(cnts2[0], True), True)
        
        # using drawContours() function
        # cv2.drawContours(tip2_img, [approx2], 0, (0, 0, 255), 2)

        tip_index = 1 if len(approx1)<= len(approx2) else -1        # 1 if the last found (search from top to bottom, so the lowest) point is used and -1 otherwise
    except:
        pass
    
    # Method 2 to decide which tip is the one that writes
    slope = 0
    try:
        slope = (start_point[0]-end_point[0]) / (start_point[1]-end_point[1])       # positive if the last found point (lowest) is the tip
    except:
        pass
    if config.tip_detection == "slope":
        if  slope >= 0:
            # cv2.imshow('tip', tip1_img)
            return 0
        else:
            # cv2.imshow('tip', tip2_img)
            return 1
    elif config.tip_detection == "shape":
        if  tip_index >= 0:
            # cv2.imshow('tip', tip1_img)
            return 1
        else:
            # cv2.imshow('tip', tip2_img)
            return 0
    
def rolling_avg(p):
    config.rolling_window.append(p)
    avg= np.mean(config.rolling_window, axis=0)
    return avg


def get_center_line(contour, mask, frame_vis):
    # Find center Line of Pen
    [vx, vy, x, y] = cv2.fitLine(contour, cv2.DIST_L2, 0, 0.01, 0.01)

    # Calculate the starting and ending points of the line
    lefty = int((-x*vy/vx) + y)
    righty = int(((mask.shape[1]-x)*vy/vx)+y)
    start_point = (0, lefty)
    end_point = (mask.shape[1]-1, righty)
    try:
        cv2.line(frame_vis, start_point, end_point, (0, 255, 0), 1)
    except:
        pass

    return start_point, end_point

def in_b(v,m):
            """Takes a value and returns the value if it is in boound of 0 <= value  <= maximu. If not it rentusn o or the maximum."""
            if v >= 0 and v <= m:
                return v
            elif v <= 0:
                return 0
            elif v >= m:
                return m
            
def update_tracked_point(contour, frame_vis, mask, frame):
    uni_hull = []
    uni_hull.append(contour)

    cv2.drawContours(frame_vis,uni_hull,-1,(255,255,255),1)

    start_point, end_point = get_center_line(contour, mask, frame_vis)

    pen_tips = find_pen_ends(frame,uni_hull,start_point,end_point,frame_vis)
    # pen_tips Format: [[x1,y1],[x2,y2]]

    if pen_tips is not None:
        if len(pen_tips) == 2:
            right_tip = find_right_tip(frame,pen_tips,mask,start_point,end_point)
            tracked_point = pen_tips[right_tip]
            config.filtered_position = rolling_avg(tracked_point)
    