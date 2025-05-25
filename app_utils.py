import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageTk

from hand_detectors import mediapipe_hand_detector as mp_detector
from system_action_handlers.mouse_action_handler import MouseActionHandler
from video_handlers.cv_video_handler import VideoHandler


class AppCameraHandler:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.detector = mp_detector.MediapipeHandDetector(0.5, 0.5)
        self.video_handler = VideoHandler(width=640, height=480)
        self.frame_counter = 0
        self.fps = 0
        self.last_frame_time = time.time()
        self.mouseController = MouseActionHandler(10)
        self.last_prediction = None
        self.prediction_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.action_cooldown = 0.4
        self.last_action_time = 0
        self.last_gesture = None
        self.gesture_count = 0
        self.gesture_stability_threshold = None

    def get_camera_image(self, is_running, config_vars, model):
        ret, frame = self.video_handler.get_screen()
        if not ret:
            return None
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self._process_hand(frame_rgb, is_running, config_vars, model)

        img = Image.fromarray(frame_rgb)
        return ImageTk.PhotoImage(img)

    def _process_hand(self, frame, is_running, config_vars, model):
        if not is_running:
            return

        current_time = time.time()
        if current_time - self.last_frame_time > 0:
            self.fps = 1.0 / (current_time - self.last_frame_time)
        self.last_frame_time = current_time

        skip_frames = config_vars.get("frame_skip", 2)

        frame_height, frame_width = frame.shape[:2]
        s1_x, s1_y = frame_width // 5, frame_height // 5
        s2_x, s2_y = 4 * frame_width // 5, 4 * frame_height // 5
        x1, x2 = 2 * frame_width // 5, 3 * frame_width // 5
        y1, y2 = 2 * frame_height // 5, 3 * frame_height // 5

        # Детекция рук
        hand_boxes, hand_landmarks_list, hand_types = self.detector.detect_hands(frame)
        for (box, landmark, hand_type) in zip(hand_boxes, hand_landmarks_list, hand_types):
            min_x, min_y, max_x, max_y = box
            if config_vars.get("show_bbox", False):
                cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
            if config_vars.get("show_skeleton", False):
                self.mp_drawing.draw_landmarks(frame, landmark, self.mp_hands.HAND_CONNECTIONS,
                                               self.mp_drawing_styles.get_default_hand_landmarks_style(),
                                               self.mp_drawing_styles.get_default_hand_connections_style())

            # Выделение и предобработка области руки
            hand_roi = frame[min_y:max_y, min_x:max_x]
            if hand_roi.size == 0:
                continue

            # Вычисление центра руки
            palm_points = [0, 5, 17]
            coords = np.array([[landmark.landmark[i].x * frame_width, landmark.landmark[i].y * frame_height]
                               for i in palm_points])
            hand_center = coords.mean(axis=0).astype(int)

            # Предсказание
            if self.frame_counter == skip_frames:
                self.frame_counter = 0

                def predict_async():
                    prediction = model.predict(hand_roi, hand_center)
                    with self.prediction_lock:
                        self.last_prediction = prediction

                self.executor.submit(predict_async)
            else:
                self.frame_counter += 1

            # Используем последнее предсказание
            with self.prediction_lock:
                prediction = self.last_prediction
            if prediction is None:
                continue

            gesture = f"{hand_type}: {prediction}"
            cv2.putText(frame, gesture, (min_x, min_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            self._handle_cursor_point(hand_center, hand_types, hand_type, frame, x1, x2, y1, y2, s1_x, s1_y, s2_x, s2_y)

            action = config_vars.get(prediction, "not selected")
            if prediction == self.last_gesture:
                self.gesture_count += 1
            else:
                self.last_gesture = prediction
                self.gesture_count = 1

            if self.gesture_stability_threshold is None:
                self.gesture_stability_threshold = round(120 / config_vars.get("frame_time_period"))

            if self.gesture_count >= self.gesture_stability_threshold and action != "not selected":
                current_time = time.time()
                if current_time - self.last_action_time >= self.action_cooldown:
                    self.mouseController.perform_action(action)
                    self.last_action_time = current_time

        self._show_fps(config_vars, frame, frame_width)
        self._show_grid(config_vars, frame, frame_width, frame_height, x1, x2, y1, y2, s1_x, s1_y, s2_x, s2_y)

    def _handle_cursor_point(self, center, hand_types, hand_type, frame, x1, x2, y1, y2, s1_x, s1_y, s2_x, s2_y):
        if len(hand_types) == 1 or hand_type == "Right":
            cv2.circle(frame, tuple(center), 5, (0, 255, 0), -1)
            self.mouseController.move_mouse(center, x1, x2, y1, y2, s1_x, s1_y, s2_x, s2_y)

    def _show_fps(self, config_vars, frame, frame_width):
        if config_vars.get("show_fps", False):
            fps_text = f"FPS: {int(self.fps)}"
            cv2.putText(frame, fps_text, (frame_width - 100, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)

    def _show_grid(self, config_vars, frame, frame_width, frame_height, x1, x2, y1, y2, s1_x, s1_y, s2_x, s2_y):
        if config_vars.get("show_grid", False):
            # Квадрат
            cv2.rectangle(frame, (s1_x, s1_y), (s2_x, s2_y), (255, 0, 0), 1)

            # Горизонтальные линии
            cv2.line(frame, (0, y1), (frame_width, y1), (255, 0, 0), 1)
            cv2.line(frame, (0, y2), (frame_width, y2), (255, 0, 0), 1)

            # Вертикальные линии
            cv2.line(frame, (x1, 0), (x1, frame_height), (255, 0, 0), 1)
            cv2.line(frame, (x2, 0), (x2, frame_height), (255, 0, 0), 1)

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
    def __init__(self, config_path, hand_gestures, default_option):
        self.config_path = config_path
        self.default_config = {
            "show_fps": False,
            "show_bbox": False,
            "show_skeleton": False,
            "multiple_gestures": False,
            "show_grid": False,
            "model_name": os.listdir(resource_path("models"))[0],
            "frame_time_period": 33,
            "frame_skip": 2,
            "call": "not selected",
            "dislike": "not selected",
            "fist": "not selected",
            "four": "not selected",
            "like": "not selected",
            "mute": "not selected",
            "ok": "not selected",
            "one": "not selected",
            "palm": "not selected",
            "peace": "not selected",
            "peace_inverted": "not selected",
            "rock": "not selected",
            "stop": "not selected",
            "stop_inverted": "not selected",
            "three": "not selected",
            "three2": "not selected",
            "two_up": "not selected",
            "two_up_inverted": "not selected"
        }
        for gesture in hand_gestures:
            self.default_config[gesture] = default_option

    def load_config(self):
        if not os.path.exists(self.config_path):
            self.save_config(self.default_config)
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self.default_config

    def save_config(self, config=None):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)