import cv2
from re import error

class VideoHandler:
    def __init__(self, camera_num = 0):
        self.video_captor = cv2.VideoCapture(camera_num)
        if not self.video_captor.isOpened():
            error("Cannot open camera")
            exit()

    def set_screen(self, width, height):
        self.video_captor.set(3, width)
        self.video_captor.set(4, height)

    def get_screen(self):
        return self.video_captor.read()

    def __del__(self):
        self.video_captor.release()