import numpy as np
import random

class Calibration:
    def __init__(self, robot):
        self.robot = robot

    def random_joint_positions(self):
        # Randomly generate valid joint positions for all joints (waist, shoulder, elbow, wrist_angle)
        waist_angle = random.uniform(0, -90)           # Waist limits
        shoulder_angle = random.uniform(-55, 25)        # Shoulder limits
        elbow_angle = random.uniform(-30, 40)            # Elbow limits
        wrist_angle = random.uniform(-100, 123)           # Wrist angle limits

        return {
            'waist': waist_angle,
            'shoulder': shoulder_angle,
            'elbow': elbow_angle,
            'wrist_angle': wrist_angle
        }

    def move_and_record_xyz(self, num_positions=100):
        xyz_data = []

        for i in range(num_positions):
            # Generate random positions for all joints
            joint_positions = self.random_joint_positions()

            # Move the robot by setting each joint to its new position
            for joint, angle in joint_positions.items():
                self.robot.set_joint_position(joint, angle)
                print(f"Moving {joint} to {angle:.2f} degrees")

            # After all joints have been set, get the resulting XYZ position
            xyz = self.robot.get_xyz()
            xyz_data.append(xyz)
            print(f"Position {i+1}/{num_positions} - XYZ: {xyz}")

        return xyz_data

    def get_xyz_data(self):
        # Perform calibration and collect 100 XYZ points by adjusting multiple joints
        xyz_points = self.move_and_record_xyz(num_positions=100)
        return xyz_points
