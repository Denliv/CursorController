import cv2
import mediapipe as mp
import cv2
import numpy as np

from PIL import Image, ImageTk

from hand_detectors import mediapipe_hand_detector as mp_detector
from video_handlers.cv_video_handler import VideoHandler

class AppCameraHandler:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.detector = mp_detector.MediapipeHandDetector(0.7, 0.7)
        self.video_handler = VideoHandler()

    def get_camera_image(self):
        _, frame = self.video_handler.get_screen()
        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        return ImageTk.PhotoImage(img)

    def get_camera_parameters(self):
        video_captor = self.video_handler.video_captor
        width = int(video_captor.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_captor.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return width, height