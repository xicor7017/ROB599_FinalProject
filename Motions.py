import sys
sys.path.append('/home/pi/ArmPi/')

import time
from enum import Enum
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as b
from CameraCalibration.CalibrationConfig import *

class State(Enum):
    WHERE_IS_BLOCK_I_DO_NOT_KNOW = 0
    FOUND_BLOCK_GETTING_READY = 1
    FOUND_BLOCK_MOVING_TO_POSITION = 2
    NEAR_BLOCK_MATCHING_ORIENTATION = 3
    NEAR_BLOCK_LOWERING= 4
    NEAR_BLOCK_GRABBING= 5
    HAVE_BLOCK_RAISING= 6
    HAVE_BLOCK_RETURNING_TO_DROPOFF= 7
    READY = 8

class Motions:

    def __init__(self):
        self.closed_gripper_angle = 450
        self.ik = ArmIK()

    def execute_motion(self, command_data):
        print("Received ", command_data)
        if command_data[0] is not None and command_data[1] is not None:
            command = command_data[0]

            if command == "ReturnBase":
                self.returnBase()

            elif command == "GripperControl":
                angle = float(command_data[1])
                self.GripperControl(angle)

            elif command == "StoreRed":
                block_pos = command_data[2][0]
                self.storeblock("red", block_pos)

            elif command == "StoreGreen":
                block_pos = command_data[2][1]
                self.storeblock("green", block_pos)

            elif command == "StoreBlue":
                block_pos = command_data[2][2]
                self.storeblock("blue", block_pos)

            elif command == "Rise":
                self.rise()

            else:
                pass

    def returnBase(self):
        print("Returning to base")
        b.setBusServoPulse(1, self.closed_gripper_angle, 300)
        b.setBusServoPulse(2, 500, 500)
        self.ik.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        time.sleep(1.2)

    def rise(self):
        print("Rising")
        _ = self.ik.setPitchRangeMoving((-0.0, 20.0, 25), -90, -90, 0)
        time.sleep(1.2)

    def storeblock(self, color, pos):
        self.dropoff = {
            'red':   np.array([-15 + 0.5, 12 - 0.5, 1.2]),
            'green': np.array([-15 + 0.5, 6 - 0.5,  1.2]),
            'blue':  np.array([-15 + 0.5, 0 - 0.5,  1.2]),
        }

        if pos is not None:
            cube_position, cube_rotation = pos[:2], pos[2]

            #Return to base:
            print("Returning to base")
            b.setBusServoPulse(1, self.closed_gripper_angle, 300)
            b.setBusServoPulse(2, 500, 500)
            self.ik.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
            time.sleep(1.2)

            #Reaching close to the block:
            print("Reaching block")
            b.setBusServoPulse(1, self.closed_gripper_angle-280, 300)
            block_reachable = self.ik.setPitchRangeMoving((*cube_position, 5), -90, -90, 0)
            if not block_reachable:
                print("Block not reachable")
                return 0
            time.sleep(1.2)

            #Setting grabbing orientation
            print("Setting grabbing orientation")
            servo2_angle = getAngle(*cube_position, cube_rotation)
            b.setBusServoPulse(2, servo2_angle, 500)
            time.sleep(1.2)

            #Reaching grabbing position
            print("Setting grabbing position")
            _ = self.ik.setPitchRangeMoving((*cube_position, 2), -90, -90, 0)
            time.sleep(1.2)

            #Grabbing block
            print("Closing gripper")
            b.setBusServoPulse(1, self.closed_gripper_angle, 300)
            time.sleep(1.2)

            #Pick up block
            print("Picking up block")
            _ = self.ik.setPitchRangeMoving((*cube_position, 15), -90, -90, 0)
            servo2_angle = getAngle(*cube_position, 0.0)
            b.setBusServoPulse(2, servo2_angle, 500)
            time.sleep(1.2)

            #Moving to drop location
            print("Moving to drop location")
            _ = self.ik.setPitchRangeMoving((*self.dropoff[color][:2], 12), -90, -90, 0)
            time.sleep(1.2)

            #Orientation droping off angle
            print("Orienting drop")
            servo2_angle = getAngle(*self.dropoff[color][:2], -90)
            b.setBusServoPulse(2, servo2_angle, 500)
            time.sleep(1.2)

            #Reach the drop off location
            print("Reach the drop location")
            _ = self.ik.setPitchRangeMoving((*self.dropoff[color][:2], 2), -90, -90, 0)
            time.sleep(1.2)

            #Open gripper
            print("Releasing cube")
            b.setBusServoPulse(1,  self.closed_gripper_angle - 200, 500)
            time.sleep(1.2)

            #Return to base
            print("Returning to base")
            b.setBusServoPulse(1, self.closed_gripper_angle, 300)
            b.setBusServoPulse(2, 500, 500)
            self.ik.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
            time.sleep(1.2)

    def GripperControl(self, angle):
        if angle < -75 or angle > -10:
            b.setBusServoPulse(1, self.closed_gripper_angle, 500)
        else:
            b.setBusServoPulse(1, self.closed_gripper_angle - 200, 500)

if __name__ == "__main__":
    motions = Motions()
    motions.storeblock("red", [-6.0, 15.6, 0.0])
    #motions.returnBase()
        
        