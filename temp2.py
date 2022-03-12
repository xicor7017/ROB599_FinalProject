import time
import rossros

class Sender:

    def __init__(self):
        self.count = 0

    def start_sending_data(self):
        self.count += 1
        return self.count

class Reciever:

    def __init__(self):
        self.rev = 0

    def get(self, data):
        print(data)

if __name__ == "__main__":
    dt = 0.01

    sender = Sender()
    reciever = Reciever()

    bus = rossros.Bus(name='trackbus')
    threads = []
    threads += [rossros.Producer(sender.start_sending_data, bus, delay=dt, name='tracker')]
    threads += [rossros.Consumer(reciever.get, bus, delay=dt, name='grabber')]
    rossros.runConcurrently(threads)