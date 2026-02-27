from handlers.__pycache__.camera_handler_2 import Camera
from examples.utils.UR_Functions import URfunctions as URControl
from examples.utils.robotiq.robotiq_gripper import RobotiqGripper
import math

HOST = "192.168.0.2"
PORT = 30003

def main():
    robot = URControl(ip=HOST, port=PORT)
    gripper = RobotiqGripper()
    gripper.connect(HOST, 63352)

    cam = Camera(0, 'robot_vial_recording')

    print(gripper.get_current_position())
    gripper.move(255, 125, 125)

    # === START RECORDING ===
    cam.start_recording()

    try:
        # Position 1 - start position, open gripper
        joint_state = [1.680945634841919, -1.9105240307249964, 2.3388877550708216,
                       -1.9763552151122035, -1.6369965712176722, 0.12794356048107147]
        robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
        gripper.move(gripper.get_open_position(), 125, 125)
        cam.capture_image('/home/robot/Code/groupc/images/position_1_start.jpg')

        # Position 2 - pick position, close gripper
        joint_state = [1.6805652379989624, -1.7611729107298792, 2.4781621138202112,
                       -2.2649728260436, -1.638026539479391, 0.12882831692695618]
        robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
        gripper.move(140, 255, 255)
        cam.capture_image('/home/robot/Code/groupc/images/position_2_pick.jpg')

        # Position 3 - move directly up
        joint_state = [1.680945634841919, -1.9105240307249964, 2.3388877550708216,
                       -1.9763552151122035, -1.6369965712176722, 0.12794356048107147]
        robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
        cam.capture_image('/home/robot/Code/groupc/images/position_3_up.jpg')

        # Position 4 - move vial above stirrer plate
        joint_state = [1.5243818759918213, -1.3093386751464386, 1.5124495665179651,
                       -1.816165109673971, -1.6351736227618616, 0.12748508155345917]
        robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
        gripper.move(140, 255, 255)
        cam.capture_image('/home/robot/Code/groupc/images/position_4_above_stirrer.jpg')

        # Position 5 - hover vial above stirrer plate
        joint_state = [1.5242940187454224, -1.248557524090149, 1.6598289648639124,
                       -2.0242706737914027, -1.6358855406390589, 0.12835928797721863]
        robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
        cam.capture_image('/home/robot/Code/groupc/images/position_5_hover.jpg')

    finally:
        # === STOP RECORDING ===
        cam.stop_recording()

def degreestorad(lst):
    return [x * (math.pi / 180) for x in lst]

if __name__ == "__main__":
    main()