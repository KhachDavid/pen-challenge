import math
from interbotix_xs_modules.xs_robot.arm import InterbotixManipulatorXS
from interbotix_common_modules.common_robot.robot import robot_shutdown, robot_startup
# The robot object is what you use to control the robot

class Robot:
    def __init__(self):
        self.robot = InterbotixManipulatorXS("px100", "arm", "gripper")
        
        robot_startup()

        current_states = self.robot.core.robot_get_joint_states()
        self.positions = {
            'waist': math.degrees(current_states.position[0]),
            'shoulder': math.degrees(current_states.position[1]),
            'elbow': math.degrees(current_states.position[2]),
            'wrist_angle': math.degrees(current_states.position[3])
        }

    def get_joint_position(self, joint):
        return self.positions[joint]
    
    def set_joint_position(self, joint, angle):
        if joint == 'waist':
            if angle > 180 or angle < -180:
                print('Invalid Waist Angle')
                return

        elif joint == 'shoulder':
            if angle > 107 or angle < -111:
                print('Invalid shoulder Angle')
                return
            
        elif joint == 'elbow':
            if angle > 92 or angle < -121:
                print('Invalid elbow Angle')
                return
            
        elif joint == 'wrist_angle':
            if angle > 123 or angle < -100:
                print('Invalid Wrist Angle')
                return

        else:
            print('Invalid parameters. Cannot move')
            return

        self.robot.arm.set_single_joint_position(joint, math.radians(angle))
        self.positions[joint] = angle
    
    def set_xyz(self, xyz):
        self.robot.arm.set_ee_pose_components(x=xyz[0], y=xyz[1], z=xyz[2])

    def get_xyz(self):
        arm_positions = self.robot.arm.get_ee_pose()

        return arm_positions[0][3], arm_positions[1][3], arm_positions[2][3]
    
    def grasp(self):
        self.robot.gripper.grasp()

    def release(self):
        self.robot.gripper.release()

    def go_home(self):
        self.robot.arm.go_to_home_pose()

    def go_sleep(self):
        self.robot.arm.go_to_sleep_pose()

    def end(self):
        robot_shutdown()