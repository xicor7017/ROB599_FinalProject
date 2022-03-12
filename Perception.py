#!/usr/bin/python3
import cv2
import Camera
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

range_rgb = {
    'red':   (0, 0, 255),
    'blue':  (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

class ColorTracker:
    def __init__(self, color = 'red', tracker_num = 1):
        self.target_color = color
        self.tracker_num = tracker_num
        self.size = (640, 480)
        self.last_x = 0
        self.last_y = 0

    def get_area_max_contour(self, contours):
        contour_area = 0
        contour_area_estimate = 0
        area_contour = None

        for c in contours :
            contour_area_estimate = math.fabs(cv2.contourArea(c))
            if contour_area_estimate > contour_area:
                contour_area = contour_area_estimate
                if contour_area > 300:
                    area_contour = c

        return area_contour, contour_area

    def track(self, frame: np.ndarray):
        img = frame.copy()
        img_height, img_width = img.shape[:2]

        # Draw a line on the center of the screen for calibration
        cv2.line(img, (0, int(img_height / 2)), (img_width, int(img_height / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_width / 2), 0), (int(img_width / 2), img_height), (0, 0, 200), 1)

        # Add Blur and convert format
        frame_resize = cv2.resize(img, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)

        # Find contours that match the color range
        c_min, c_max = color_range[self.target_color]
        frame_mask = cv2.inRange(frame_lab, c_min, c_max)
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6,6),np.uint8))
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6,6),np.uint8))
        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
        area_contour, area = self.get_area_max_contour(contours)

        if area_contour is not None and area > 2500:
            # Bounding box
            rect = cv2.minAreaRect(area_contour)
            box = np.int0(cv2.boxPoints(rect))

            # Drawing the bounding box
            roi = getROI(box)
            get_roi = True
            img_centerx, img_centery = getCenter(rect, roi, self.size, square_length)
            world_x, world_y = convertCoordinate(img_centerx, img_centery, self.size)
            cv2.drawContours(img, [box], -1, range_rgb[self.target_color], 2)
            cv2.putText(img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, range_rgb[self.target_color], 1)

            #Labeling the  color
            cv2.putText(img, "Color: " + self.target_color, (250*self.tracker_num, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, range_rgb[self.target_color], 2)
            cube_pos = [round(world_x,2), round(world_y,2), round(rect[2],2)]

        else:
            cube_pos = None
        
        return img, cube_pos

class Tracker:
    def __init__(self):
        #Initializing camera
        self.camera = Camera.Camera()
        self.camera.camera_open()

        #Trackers for RGB colors
        self.tracker_red = ColorTracker("red", 0)
        self.tracker_green = ColorTracker("green", 1)
        self.tracker_blue = ColorTracker("blue", 2)

        #self.startTracking()
    
    def track(self):
        img = self.camera.frame

        if img is not None:
            frame = img.copy()
            frame, red_cube_pos = self.tracker_red.track(frame)
            frame, green_cube_pos = self.tracker_green.track(frame)
            frame, blue_cube_pos = self.tracker_blue.track(frame)
            cv2.imshow('Frame', frame)   
            key = cv2.waitKey(1)
        else:
            red_cube_pos, green_cube_pos, blue_cube_pos = None, None, None

        return red_cube_pos, green_cube_pos, blue_cube_pos

if __name__ == '__main__':
    Tracker()