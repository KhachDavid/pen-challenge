import cv2
import argparse
import numpy as np

from Realsense import DepthAndColorAligner 

title_window = 'Pen Challenge'

def main():
    args = get_args()

    with DepthAndColorAligner(args, clipping_distance_in_meters=0.8) as aligner:
        cv2.namedWindow(title_window, cv2.WINDOW_NORMAL)
        cv2.createTrackbar('minH',title_window,0,179,nothing)
        cv2.createTrackbar('minS',title_window,0,255,nothing)
        cv2.createTrackbar('minV',title_window,0,255,nothing)
        cv2.createTrackbar('maxH',title_window,0,179,nothing)
        cv2.createTrackbar('maxS',title_window,0,255,nothing)
        cv2.createTrackbar('maxV',title_window,0,255,nothing)

        cv2.setTrackbarPos('minH', title_window, 115)
        cv2.setTrackbarPos('minS', title_window, 75)
        cv2.setTrackbarPos('minV', title_window, 58)
        cv2.setTrackbarPos('maxH', title_window, 149)
        cv2.setTrackbarPos('maxS', title_window, 255)
        cv2.setTrackbarPos('maxV', title_window, 255)
        

        while True:
            depth_image, color_image = aligner.process_frames()

            if depth_image is None or color_image is None:
                continue

            bg_removed = aligner.remove_background(depth_image, color_image)
            #aligner.render_images(bg_removed, depth_image)
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            images = np.hstack((bg_removed, depth_colormap))
            min_h = cv2.getTrackbarPos('minH',title_window)
            min_s = cv2.getTrackbarPos('minS',title_window)
            min_v = cv2.getTrackbarPos('minV',title_window)
            max_h = cv2.getTrackbarPos('maxH',title_window)
            max_s = cv2.getTrackbarPos('maxS',title_window)
            max_v = cv2.getTrackbarPos('maxV',title_window)

            lower_bound = np.array([min_h, min_s, min_v])
            upper_bound = np.array([max_h, max_s, max_v])

            hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
            #result = mask
            #cv2.imshow(title_window, result)

            # Colored version below
            # Show the colored mask result
            result_colored = cv2.bitwise_and(color_image, color_image, mask=mask)
            # Convert the mask to grayscale
            mask_grayscale = cv2.cvtColor(result_colored, cv2.COLOR_BGR2GRAY)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # drawing all contours...we don't need it here
            #for contour in contours:
            #    # Calculate the moments of the contour
            #    M = cv2.moments(contour)
            #    if M["m00"] != 0:  # To avoid division by zero
            #        # Calculate the x and y coordinates of the centroid
            #        cX = int(M["m10"] / M["m00"])
            #        cY = int(M["m01"] / M["m00"])
            #
            #        # Draw the contour
            #        cv2.drawContours(result_colored, [contour], -1, (0, 255, 0), 2)  # Green contours on color
            #        cv2.drawContours(mask_grayscale, [contour], -1, (255, 255, 255), 2)  # White contours on grayscale
            #
            #        # Draw the centroid on both images
            #        cv2.circle(result_colored, (cX, cY), 5, (255, 0, 0), -1)  # Blue dot for the centroid
            #        cv2.circle(mask_grayscale, (cX, cY), 5, (255, 255, 255), -1)  # White dot for the centroid

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)

                M = cv2.moments(largest_contour)

                # avoid div by zero
                if M["m00"] != 0: 
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])

                    cv2.drawContours(result_colored, [largest_contour], -1, (0, 255, 0), 2)
                    cv2.drawContours(mask_grayscale, [largest_contour], -1, (255, 255, 255), 2)
                    cv2.drawContours(color_image, [largest_contour], -1, (0, 255, 0), 2)  # Green contour on color image

                    cv2.circle(result_colored, (cX, cY), 5, (255, 0, 0), -1) 
                    cv2.circle(mask_grayscale, (cX, cY), 5, (255, 255, 255), -1) 
                    cv2.circle(color_image, (cX, cY), 5, (255, 255, 255), -1) 


            # contours
            #cv2.drawContours(result_colored, contours, -1, (0, 255, 0), 2)
            #cv2.drawContours(mask_grayscale, contours, -1, (255, 255, 255), 2)

            cv2.imshow(title_window, result_colored)
            cv2.imshow(title_window + '_grayscale', mask_grayscale)
            cv2.imshow(title_window, color_image)  # Show the original color image with contour

            key = cv2.waitKey(1)
            if key & 0xFF == ord('q') or key == 27:
                break


def nothing(x):
    pass

def get_args():
    parser = argparse.ArgumentParser(
                    prog='Realsense',
                    description='Optional args to this program will let you read or save video streams',
                    epilog='This program accepts a -f filename followed by -a <r|read|w|write>')
    
    parser.add_argument('-f', '--file', required=False)
    parser.add_argument('-a', '--action', required=False)
    return parser.parse_args()

if __name__ == "__main__":
    main()
