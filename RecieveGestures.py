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
        #s.setblocking(0)
        print("Connected to Gesture Server")

        self.startClient()

    def startClient(self):
        while True:
            msg = self.s.recv(1024)
            gesture = pickle.loads(msg)
            print(gesture)
            time.sleep(0.1)

if __name__ == "__main__":
    R = RecieveGestures()

    