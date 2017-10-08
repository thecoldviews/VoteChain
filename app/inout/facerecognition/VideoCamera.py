# camera.py

import cv2
from RecordingThread import RecordingThread

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.is_record = False
        self.out = None
        self.recordingThread = None
    
    def __del__(self):
        self.video.release()

    def start_record(self):
        self.is_record = True
        self.recordingThread = RecordingThread("Video Recording Thread", self.video)
        self.recordingThread.start()

    def stop_record(self):
        self.is_record = False

        if self.recordingThread != None:
            self.recordingThread.stop()
    
    def get_frame(self):
        success, image = self.video.read()
        # ret, jpeg = cv2.imencode('.jpg', image)
        return image