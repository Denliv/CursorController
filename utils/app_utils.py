import cv2
import mediapipe as mp
import numpy as np
import json
import os
import threading
import time
from PIL import Image, ImageTk
from hand_detectors import mediapipe_hand_detector as mp_detector
from video_handlers.cv_video_handler import VideoHandler

class AppCameraHandler:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.detector = mp_detector.MediapipeHandDetector(0.5, 0.5)
        self.video_handler = VideoHandler(width=640, height=480)
        self.frame_counter = 0
        self.skip_frames = 1

    def get_camera_image(self, is_running, config_vars):
        _, frame = self.video_handler.get_screen()
        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self._show_hand_bb(frame, is_running, config_vars)

        img = Image.fromarray(frame)
        return ImageTk.PhotoImage(img)

    def _show_hand_bb(self, frame, is_running, config_vars):
        if not is_running:
            return

        # self.frame_counter += 1
        # if self.frame_counter % self.skip_frames != 0:
        #     return

        hand_boxes, hand_landmarks_list, hand_types = self.detector.detect_hands(frame)
        for (box, landmark, hand_type) in zip(hand_boxes, hand_landmarks_list, hand_types):
            min_x, min_y, max_x, max_y = box
            # Отрисовка
            if config_vars["show_bbox"]:
                cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
            if config_vars["show_skeleton"]:
                self.mp_drawing.draw_landmarks(frame,
                                               landmark,
                                               self.mp_hands.HAND_CONNECTIONS,
                                               self.mp_drawing_styles.get_default_hand_landmarks_style(),
                                               self.mp_drawing_styles.get_default_hand_connections_style())

            # Выделение области руки
            hand_roi = frame[min_y:max_y, min_x:max_x]
            if hand_roi.size == 0:
                continue

            # Подготовка изображения для модели
            hand_roi = cv2.resize(hand_roi, (64, 64), interpolation=cv2.INTER_AREA)
            hand_roi = np.expand_dims(hand_roi, axis=0)

            # Предсказание жеста
            # prediction = model.predict(hand_roi)
            # gesture = class_names[prediction[0]]
            gesture = hand_type + ": " + "prediction"

            # Отображение результата
            cv2.putText(frame, gesture, (min_x, min_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    def get_camera_parameters(self):
        video_captor = self.video_handler.video_captor
        width = int(video_captor.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_captor.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return width, height

    def __del__(self):
        if hasattr(self.video_handler, 'video_captor'):
            self.video_handler.video_captor.release()
        del self.video_handler

class ConfigHandler:
    def __init__(self, config_path=None):
        self.config_path = config_path
        self.default_config = {
            "show_fps": False,
            "show_bbox": False,
            "show_skeleton": False,
            "multiple_gestures": False,
            "model_name": [os.path.splitext(f)[0] for f in os.listdir("models")][0],
            "fps": 33
        }

    def load_config(self):
        if not os.path.exists(self.config_path):
            self.save_config(self.default_config)
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self.default_config

    def save_config(self, config = None):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)