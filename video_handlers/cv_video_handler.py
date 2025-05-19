import cv2

class VideoHandler:
    def __init__(self, camera_num = 0, width = 640, height = 480):
        self.video_captor = cv2.VideoCapture(camera_num)
        self.set_screen(width, height)
        if not self.video_captor.isOpened():
            raise RuntimeError("Cannot open camera")

    def set_screen(self, width, height):
        self.video_captor.set(3, width)
        self.video_captor.set(4, height)

    def get_screen(self):
        return self.video_captor.read()

    def __del__(self):
        self.video_captor.release()