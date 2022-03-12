import time
import socket
import pickle

class RecieveGestures:

    def __init__(self):
        host = "10.1.10.7"
        port = 7788
        freq = 50
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Connecting to Gesture Server on Host: {}:{}".format(host, port))
        self.s.connect((host, port))
        print("Connected to Gesture Server")

    def getData(self):
        msg = self.s.recv(1024)
        gesture, angle = pickle.loads(msg)
        return [gesture, angle]
        
if __name__ == "__main__":
    R = RecieveGestures()

    