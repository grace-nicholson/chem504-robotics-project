from PIL import ImageTk, Image
import numpy as np
import math
import os
import sys
import cv2
import numpy as np
import time
from handlers import camera_handler

current_dir = os.path.dirname(os.path.abspath(__file__))
from examples.utils.UR_Functions import URfunctions as URControl
# sys.path.append(os.path.join(current_dir, 'robotiq'))
# current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(f"current_dir : {current_dir}")
# sys.path.append(current_dir)

from examples.utils.robotiq.robotiq_gripper import RobotiqGripper



HOST = "192.168.0.2"
PORT = 30003
# from robotiq.robotiq_gripper import RobotiqGripper
def main():
    robot = URControl(ip="192.168.0.2", port=30003)
    HOST = "192.168.0.2"
    PORT = 30003
    gripper=RobotiqGripper()
    gripper.connect("192.168.0.2", 63352)
    print(gripper.get_current_position())
    gripper.move(255,125,125)
    #joint_state=degreestorad([93.77,-89.07,89.97,-90.01,-90.04,0.0])
    #robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
    #gripper.move(gripper.get_open_position(), 255, 0)
    
    # start position - open gripper
    joint_state=[1.680945634841919, -1.9105240307249964, 2.3388877550708216, -1.9763552151122035, -1.6369965712176722, 0.12794356048107147]
    robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
    gripper.move(gripper.get_open_position(),125,125)
    
    # move to pick position and close gripper
    joint_state=[1.6805652379989624, -1.7611729107298792, 2.4781621138202112, -2.2649728260436, -1.638026539479391, 0.12882831692695618]
    robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
    gripper.move(140,255,255)

    # move directly up
    joint_state=[1.680945634841919, -1.9105240307249964, 2.3388877550708216, -1.9763552151122035, -1.6369965712176722, 0.12794356048107147]
    robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
    
    #NOT USED
#     joint_state=[1.0959500074386597, -1.2733981174281617, 1.5358312765704554, -1.837823053399557, -1.6253846327411097, 0.12656208872795105]
#     robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
    #NOT USED
#     joint_state=[1.0957462787628174, -1.1416998666575928, 1.7283881346331995, -2.161959787408346, -1.6265938917743128, 0.12783384323120117]
#     robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
# #     gripper.move(gripper.get_open_position(),125,125)
    
    #move vial above stirrer plate
    joint_state=[1.5243818759918213, -1.3093386751464386, 1.5124495665179651, -1.816165109673971, -1.6351736227618616, 0.12748508155345917]
    robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
    gripper.move(140,255,255)
    
    #hovers vial above stirrer plate
    joint_state=[1.5242940187454224, -1.248557524090149, 1.6598289648639124, -2.0242706737914027, -1.6358855406390589, 0.12835928797721863]
    robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
    #gripper.move(gripper.get_open_position(),125,125)
    
    # move arm above vial
    #joint_state=[1.5243818759918213, -1.3093386751464386, 1.5124495665179651, -1.816165109673971, -1.6351736227618616, 0.12748508155345917]
    #robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
    
    # move back to start position
    #joint_state=[1.680945634841919, -1.9105240307249964, 2.3388877550708216, -1.9763552151122035, -1.6369965712176722, 0.12794356048107147]
    #robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
    
#     joint_state=[1.0959500074386597, -1.2733981174281617, 1.5358312765704554, -1.837823053399557, -1.6253846327411097, 0.12656208872795105]
#     robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
    
#     joint_state=degreestorad([93.77,-89.07,89.97,-90.01,-90.04,0.0])
#     robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
#     gripper.move(gripper.get_open_position(), 255, 0)
    

#     joint_state=[1.6807823181152344, -1.8428417644896449, 2.4167338053332728, -2.1217719517149867, -1.6374414602862757, 0.12840861082077026]
#     robot.move_joint_list(joint_state, 0.5, 0.5, 0.02)
    
    
    
def degreestorad(list):
     for i in range(6):
          list[i]=list[i]*(math.pi/180)


if __name__=="__main__":
     main()