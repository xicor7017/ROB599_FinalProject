import cv2
import socket, pickle
import numpy as np
import mediapipe as mp

class Run_gesture_recognition_server:

    def __init__(self):
        # initialize mediapipe
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.mpDraw = mp.solutions.drawing_utils

        # Load the gesture recognizer model
        f = open("Model", 'rb')
        self.model = pickle.load(f)
        
        self.classNames = ['okay', 'peace', 'thumbs up', 'thumbs down',
                    'call me', 'stop', 'rock', 'live long', 'fist', 'smile']

        # Initialize the webcam
        self.cap = cv2.VideoCapture("/dev/video2")

        #Initialize belief array for discrete bayes filter
        self.belief = np.array((1/len(self.classNames) * np.ones(len(self.classNames))))

        #Initialize connection
        host = '10.1.10.7'
        port = 7788
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Waiting for connection from Gesture client")
        s.bind((host, port))
        s.listen(1) #Allow only 1 connection
        self.c, addr = s.accept()
        print("Connection successfull")

        self.current_gesture = ""
        self.startServer()

    def normalize_belief(self, distribution):
        distribution /= sum(distribution.astype(float))
        distribution = np.clip(distribution, 1e-5, 0.99)
        return distribution

    def update_belief(self, belief, gestureReading, prob_correct): 
        gestureReading_beliefIndex = self.classNames.index(gestureReading)#belief.index(gestureReading)
        scale = prob_correct / (1 - prob_correct)
        
        for i, gestureProb in enumerate(belief):
            if gestureReading_beliefIndex == i:
                gestureProb *= scale 
                belief[i] = gestureProb


        updatedBelief = self.normalize_belief(belief)
        self.belief = updatedBelief

    def startServer(self, n=10):
        last_n = ['stop' for _ in range(n)]
        while True:
            # Read each frame from the webcam
            _, frame = self.cap.read()

            x, y, c = frame.shape

            # Flip the frame vertically
            frame = cv2.flip(frame, 1)
            framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Get hand landmark prediction
            result = self.hands.process(framergb)

            # post process the result
            post_processed = False
            if result.multi_hand_landmarks:
                landmarks = []
                for handslms in result.multi_hand_landmarks:
                    for lm in handslms.landmark:
                        lmx = int(lm.x * x)
                        lmy = int(lm.y * y)

                        landmarks.append([lmx, lmy])

                    rect = cv2.minAreaRect(np.array([landmarks]))
                    
                    gestureAngle = rect[2]
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)

                    # Drawing landmarks on frames
                    self.mpDraw.draw_landmarks(
                        frame, handslms, self.mpHands.HAND_CONNECTIONS)

                    # Predict gesture
                    prediction = self.model.predict([landmarks])
                    classID = np.argmax(prediction)
                    post_processed = True

                    last_n = last_n[1:] + [self.classNames[classID]]
                    className = max(last_n, key=last_n.count)

                    self.update_belief(self.belief, className, 0.9)

                    most_likely_current_gesture_index = np.argmax(self.belief)
                    className = self.classNames[most_likely_current_gesture_index]
                    self.current_gesture = self.classNames[most_likely_current_gesture_index]
                    #print(f"probability of {self.current_gesture} is {np.amax(self.belief)}")

                cv2.putText(frame, className, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 2, cv2.LINE_AA)

            # Show the final output
            cv2.imshow("Output", frame)

            if post_processed:

                msg = [className, gestureAngle]
                msg = pickle.dumps(msg)
                print(className, gestureAngle)
                self.c.send(msg)

            if cv2.waitKey(1) == ord('q'):
                break

        # release the webcam and destroy all active windows
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    Run_gesture_recognition_server()