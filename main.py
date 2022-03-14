import time
import rossros

from Motions import Motions
from Perception import Tracker
from RecieveGestures import RecieveGestures

from temp_reciver import Reciever

class Merger:

    def __init__(self):
        self.red_cube_pos = None
        self.green_cube_pos = None
        self.blue_cube_pos = None

        self.gesture = None
        self.gesture_angle = None
        self.gesture2command = {
                                "stop"          : "ReturnBase",
                                "thumbs up"     : "StoreRed",
                                "thumbs down"   : "StoreBlue",
                                "call me"       : "StoreGreen",
                                'peace'         : "GripperControl",
                                "rock"          : "Rise",
                                "fist"          : "Rise",

                                'okay'          : "pass",
                                'live long'     : "ReturnBase",
                                'smile'         : "ReturnBase"
                                }

        self.current_command = None
        self.all_poses = [self.red_cube_pos, self.green_cube_pos, self.blue_cube_pos]
        
    def update_poses(self, poses):
        self.red_cube_pos = poses[0]
        self.green_cube_pos = poses[1]
        self.blue_cube_pos = poses[2]

        self.all_poses = [self.red_cube_pos, self.green_cube_pos, self.blue_cube_pos]

    def update_gesture(self, gesture_data):
        if gesture_data != 0:
            self.gesture = gesture_data[0]
            self.gesture_angle = gesture_data[1]
            self.current_command = self.gesture2command[self.gesture]

    def commandArm(self):
        return [self.current_command, self.gesture_angle, self.all_poses]

    def print_data(self):
        print(self.red_cube_pos, self.gesture)
        time.sleep(0.5)

if __name__ == "__main__":

    #Initializing class    
    merger = Merger()
    tracker = Tracker()
    gestureReciever = RecieveGestures()
    motions = Motions()

    #Initializing busses
    cubePoseBus = rossros.Bus(name='cubePoseBus')
    gesturesBus = rossros.Bus(name='gesturesBus')
    commandsBus = rossros.Bus(name='CommandsBus')
    
    #Initializing and starting threads
    dt = 0.1
    threads = []
    
    threads += [rossros.Producer(tracker.track, cubePoseBus, delay=dt, name='cubePoseTracker')]
    threads += [rossros.Producer(gestureReciever.getData, gesturesBus, delay=dt, name='GestureReceiverClient')]
    threads += [rossros.Producer(merger.commandArm, commandsBus, delay=3*dt, name='sendCommands')]

    threads += [rossros.Consumer(merger.update_poses, cubePoseBus, delay=dt, name='mergerPoses')]
    threads += [rossros.Consumer(merger.update_gesture, gesturesBus, delay=dt, name='mergerGestures')]
    threads += [rossros.Consumer(motions.execute_motion, commandsBus, delay=3*dt, name='controlArm')]
    
    rossros.runConcurrently(threads)

    while True:
        merger.print_data()