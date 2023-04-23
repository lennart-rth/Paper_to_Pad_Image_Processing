import cv2
import numpy as np
import mouse
from scipy.spatial import distance as dist

import config

def move_mouse(warped_point):
    try:
        x_diff = warped_point[0]-config.old_pen_point[0]
        y_diff = warped_point[1]-config.old_pen_point[1]

        s = cv2.getTrackbarPos('mouse_sensitivity', 'main')
        # x_diff *= s
        # y_diff *= s

        if config.drawing:
            mouse.move(-x_diff, -y_diff, absolute=False)
    except:
         pass

def handle_perspective_change(frame_vis):
    print(config.corners)
    try:
        warped,warped_point = four_point_transform(frame_vis, np.asarray(config.corners, dtype="float32")) 
        warped_point = warped_point[0][0] 

        # Create a new 4-channel image with transparency values
        hwa = int(warped.shape[0])
        wwa = int(warped.shape[1])

        transparent_img = np.zeros((hwa, wwa, 4), dtype=np.uint8)
        cv2.circle(transparent_img, (int(warped_point[0]),int(warped_point[1])), 3, (0, 0, 255), -1)

        alpha = np.ones((hwa, wwa, 1), dtype=np.uint8) * 255
        rgba = np.concatenate((warped, alpha), axis=2)
        warped = cv2.addWeighted(rgba,1,transparent_img,1,0)
        
        w = frame_vis.shape[1]
        h = frame_vis.shape[0]
        # print(frame_vis.shape)

        # warped = cv2.resize(warped,(int((700/h)*w),700))
        warped = cv2.flip(warped, -1)
        cv2.imshow('DinA4', warped) 
        # print(warped_point) 

        move_mouse(warped_point)

    except:
        pass

    return warped_point

# def order_points(pts):
# 	rect = np.zeros((4, 2), dtype = "float32")

# 	s = pts.sum(axis = 1)
# 	rect[0] = pts[np.argmin(s)]
# 	rect[2] = pts[np.argmax(s)]

# 	diff = np.diff(pts, axis = 1)
# 	rect[1] = pts[np.argmin(diff)]
# 	rect[3] = pts[np.argmax(diff)]

# 	return rect
def order_points(pts):
	xSorted = pts[np.argsort(pts[:, 0]), :]

	leftMost = xSorted[:2, :]
	rightMost = xSorted[2:, :]

	leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
	(tl, bl) = leftMost

	D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
	(br, tr) = rightMost[np.argsort(D)[::-1], :]

	return np.array([tl, tr, br, bl], dtype="float32")


def four_point_transform(image, pts):
    rect = order_points(pts)      #we dont need to order the points because the user is instrucetd to add the points in the right order
    (tl, tr, br, bl) = rect

    # (tl, tr, br, bl) = pts
    # rect = np.assary(pts)

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
        
    maxHeight = int((maxWidth/5)*7)     # this is the format of DINA4

    dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")

	# compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)

    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    track_point = np.array([config.filtered_position], dtype='float32')
    track_point = np.array([track_point])

    new_point = cv2.perspectiveTransform(track_point, M)
    
	# return the warped image and point
    return warped, new_point