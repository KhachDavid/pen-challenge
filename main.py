import argparse
import cv2
import pickle
import numpy as np
import math

from camera import Camera
from arm import Robot
from Realsense import DepthAndColorAligner 
from calibration import Calibration
from scipy.spatial.transform import Rotation as R

def main():
    args = get_args()
    cam = Camera(args)
    r = Robot()

    # Calibration case
    if args.c:
        with DepthAndColorAligner(args, clipping_distance_in_meters=1) as aligner:
            #while camera_coordinates == None or 0.0 in camera_coordinates or -0.0 in camera_coordinates:
            cam.setup()
            calibrate = Calibration()
            robot_points = calibrate.xyz_points()
            camera_points = []
            #while True:
            for point in robot_points:
                r.set_xyz(point)
                camera_coordinates = None
                while camera_coordinates == None or 0.0 in camera_coordinates or -0.0 in camera_coordinates:
                    camera_coordinates = cam.get_points(aligner)
                    cam.display()
                    # Wait to remove
                    key = cv2.waitKey(1)
                    ## Press esc or 'q' to close the image window
                    if key & 0xFF == ord('q') or key == 27:
                        cam.destroy()

                camera_points.append(camera_coordinates)

            ########## Begin_citation [3] ##########
            x = [p[0] for p in robot_points]
            y = [p[1] for p in robot_points]
            z = [p[2] for p in robot_points]
            robot_centroid = (sum(x) / len(robot_points), sum(y) / len(robot_points), sum(z) / len(robot_points))

            x = [p[0] for p in camera_points]
            y = [p[1] for p in camera_points]
            z = [p[2] for p in camera_points]
            camera_centroid = (sum(x) / len(camera_points), sum(y) / len(camera_points), sum(z) / len(robot_points))
            ########## End_citation [3] ########## 

            robot_normal = []
            camera_normal = []

            # normalize
            for point in robot_points:
                normal_point = np.subtract(point, robot_centroid)
                robot_normal.append(normal_point)

            for point in camera_points:
                normal_point = np.subtract(point, camera_centroid)
                camera_normal.append(normal_point)

            robot_normal = np.array(robot_normal)
            camera_normal = np.array(camera_normal)

            # Find the rotation matrix using align_vectors function
            rot, rssd, sens = R.align_vectors(robot_normal, camera_normal, return_sensitivity=True)

            # Compute the translation vector t using the formula t = P_centroid - R * Q_centroid
            translation = np.subtract(robot_centroid, rot.apply(camera_centroid))

            print("Rotation Matrix (R):", rot.as_matrix())
            print("Translation Vector (t):", translation)

            # Save the rotation and translation to a pickle file
            with open('transformation_data.pkl', 'wb') as f:
                pickle.dump({
                    'rotation_matrix': rot.as_matrix(),
                    'translation_vector': translation
                }, f)

            print("Rotation matrix and translation vector saved to transformation_data.pkl")

    # Actual program     
    else:

        STATE = "GRIPPERS_OPEN"
        with open('transformation_data.pkl', 'rb') as f:
            data = pickle.load(f)

        rotation_matrix = data['rotation_matrix']
        translation_vector = data['translation_vector']

        r.go_home()
        r.release()
        with DepthAndColorAligner(args, clipping_distance_in_meters=1.8) as aligner:
            camera_coordinates = None
            #while camera_coordinates == None or 0.0 in camera_coordinates or -0.0 in camera_coordinates:
            cam.setup()
            r.release()
            while True:
                # list of x, y, z. element one is x, element two is y, element 3 is z
                camera_coordinates = cam.get_points(aligner)
                print(camera_coordinates)

                if camera_coordinates is not None:
                    robot_coords = transform_camera_to_robot(camera_coordinates, rotation_matrix, translation_vector)

                    # move the robot here using the x y z
                    x, y, z = robot_coords

                    # Move the waist first based on the x and y coordinates
                    waist_angle = math.degrees(math.atan2(y, x))  # Calculate waist angle from x and y
                    r.release()
                    print(f"Setting Waist Angle to: {waist_angle}")
                    r.set_joint_position('waist', waist_angle)

                    # Move the robot to the new x, y, z coordinates
                    print(f"Moving to x: {x}, y: {y}, z: {z}")
                    if STATE == "GRIPPERS_OPEN":
                        STATE == "GRIPPERS_CLOSED"
                        r.set_xyz([x, y, z])
                        r.grasp()
                        break
                    else:
                        STATE == "GRIPPERS_OPEN"
                        r.release()

                cam.display()
                # Wait to remove
                key = cv2.waitKey(1)
                ## Press esc or 'q' to close the image window
                if key & 0xFF == ord('q') or key == 27:
                    cam.destroy()

    r.go_sleep()
    r.end()

# Function to transform camera coordinates to robot coordinates
def transform_camera_to_robot(camera_coords, rotation_matrix, translation_vector):
    # Convert to np.array if it's not already
    camera_coords = np.array(camera_coords)

    # Apply the formula: Q = R * P + T
    robot_coords = np.dot(rotation_matrix, camera_coords) + translation_vector
    return robot_coords

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