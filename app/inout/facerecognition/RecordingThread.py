import threading

class RecordingThread (threading.Thread):
    def __init__(self, name, camera):
        threading.Thread.__init__(self)
        self.name = name
        self.isRunning = True
 
        self.cap = camera
 
    def run(self):
        while self.isRunning:
            ret, frame = self.cap.read()
 
    def stop(self):
        self.isRunning = False
 
    def __del__(self):
        pass