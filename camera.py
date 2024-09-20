import cv2
import numpy as np
import pyrealsense2 as rs
from Realsense import DepthAndColorAligner 

title_window = 'Pen Challenge'



class Camera:
    def __init__(self, args):
        self.args = args

    def get_points(self, aligner):

        #with DepthAndColorAligner(self.args, clipping_distance_in_meters=0.8) as aligner:
            #cv2.createTrackbar('minH',title_window,0,179,self.nothing)
            #cv2.createTrackbar('minS',title_window,0,255,self.nothing)
            #cv2.createTrackbar('minV',title_window,0,255,self.nothing)
            #cv2.createTrackbar('maxH',title_window,0,179,self.nothing)
            #cv2.createTrackbar('maxS',title_window,0,255,self.nothing)
            #cv2.createTrackbar('maxV',title_window,0,255,self.nothing)

            #cv2.setTrackbarPos('minH', title_window, 115)
            #cv2.setTrackbarPos('minS', title_window, 75)
            #cv2.setTrackbarPos('minV', title_window, 58)
            #cv2.setTrackbarPos('maxH', title_window, 149)
            #cv2.setTrackbarPos('maxS', title_window, 255)
            #cv2.setTrackbarPos('maxV', title_window, 255)
        
            #while True:
        depth_image, color_image = aligner.process_frames()
        
        self.color_image = color_image
        if depth_image is None or color_image is None:
            # Try again
            return None

        self.smooth_color_image = cv2.bilateralFilter(self.color_image, 15, 15, 75)
        self.smooth_color_image = aligner.remove_background(depth_image, self.smooth_color_image)
        #min_h = cv2.getTrackbarPos('minH',title_window)
        #min_s = cv2.getTrackbarPos('minS',title_window)
        #min_v = cv2.getTrackbarPos('minV',title_window)
        #max_h = cv2.getTrackbarPos('maxH',title_window)
        #max_s = cv2.getTrackbarPos('maxS',title_window)
        #max_v = cv2.getTrackbarPos('maxV',title_window)

        lower_bound = np.array(self.get_purple_lower())
        upper_bound = np.array(self.get_purple_higher())
        hsv = cv2.cvtColor(self.smooth_color_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest_contour)
            # avoid div by zero
            if M["m00"] != 0: 
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                #cv2.drawContours(result_colored, [largest_contour], -1, (0, 255, 0), 2)
                #cv2.drawContours(mask_grayscale, [largest_contour], -1, (255, 255, 255), 2)
                cv2.drawContours(self.color_image, [largest_contour], -1, (0, 255, 0), 2)  # Green contour on color image
                cv2.drawContours(self.smooth_color_image, [largest_contour], -1, (0, 255, 0), 2)  # Green contour on color image
                #cv2.circle(result_colored, (cX, cY), 5, (255, 0, 0), -1) 
                #cv2.circle(mask_grayscale, (cX, cY), 5, (255, 255, 255), -1) 
                cv2.circle(self.color_image, (cX, cY), 5, (255, 255, 255), -1) 
                cv2.circle(self.smooth_color_image, (cX, cY), 5, (255, 255, 255), -1) 

                intrinsics = aligner.intrinsics

                ## CITE
                depth = aligner.aligned_depth_frame.get_distance(cX, cY)
                #depth = depth_image[cY, cX]
                point_3D = rs.rs2_deproject_pixel_to_point(intrinsics, [cX, cY], depth)

                #cv2.imshow("Smooth", smooth_color_image)  # Show the original color image with contour
                #key = cv2.waitKey(1)
                #if key & 0xFF == ord('q') or key == 27:
                #    break
                return point_3D

    def setup(self):
        cv2.namedWindow("Smooth", cv2.WINDOW_NORMAL)

    def display(self):
        #cv2.namedWindow(title_window, cv2.WINDOW_NORMAL)
        cv2.imshow("Smooth", self.color_image)
        #cv2.imshow("Smooth", self.color_image)

    def trackbars(self):
        pass

    def destroy(self):
        cv2.destroyAllWindows()

    def get_purple_lower(self):
        return [115, 75, 58], 

    def get_purple_higher(self):
        return [149, 255, 255], 

    def nothing(x):
        pass

