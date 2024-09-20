import argparse
import cv2

from camera import Camera
from arm import Robot
from Realsense import DepthAndColorAligner 
from calibration import Calibration

def main():
    args = get_args()
    cam = Camera(args)
    r = Robot()

    if args.c:
        while True:
            calibrate = Calibration()
            points = calibrate.xyz_points()
            for point in points:
                r.set_xyz(point)

    else:    
        with DepthAndColorAligner(args, clipping_distance_in_meters=0.8) as aligner:
            camera_coordinates = None
            #while camera_coordinates == None or 0.0 in camera_coordinates or -0.0 in camera_coordinates:
            cam.setup()
            while True:
                camera_coordinates = cam.get_points(aligner)
                print(camera_coordinates)
                cam.display()
                # Wait to remove
                key = cv2.waitKey(1)
                ## Press esc or 'q' to close the image window
                if key & 0xFF == ord('q') or key == 27:
                    cam.destroy()

    r.end()

def get_args():
    parser = argparse.ArgumentParser(
                    prog='Realsense',
                    description='Optional args to this program will let you read or save video streams',
                    epilog='This program accepts a -f filename followed by -a <r|read|w|write>')
    
    parser.add_argument('-f', '--file', required=False)
    parser.add_argument('-a', '--action', required=False)
    parser.add_argument('-c', action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    main()