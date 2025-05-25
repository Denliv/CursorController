import cv2

class VideoHandler:
    def __init__(self, camera_num = None, width = 640, height = 480, max_cameras=10):
        if camera_num is not None:
            self.video_captor = cv2.VideoCapture(camera_num)
            if self.video_captor.isOpened():
                self.set_screen(width, height)
                return
        self.video_captor = None
        for camera_num in range(max_cameras):
            cap = cv2.VideoCapture(camera_num)
            if cap.isOpened():
                self.video_captor = cap
                self.set_screen(width, height)
                break
            cap.release()

        if self.video_captor is None or not self.video_captor.isOpened():
            raise RuntimeError("No available camera found")

    def set_screen(self, width, height):
        self.video_captor.set(3, width)
        self.video_captor.set(4, height)

    def get_screen(self):
        return self.video_captor.read()

    def __del__(self):
        self.video_captor.release()