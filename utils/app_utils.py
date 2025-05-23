﻿import cv2
import mediapipe as mp
import numpy as np
import json
import os
import time
from PIL import Image, ImageTk
from hand_detectors import mediapipe_hand_detector as mp_detector
from model_api import YoloModel, AutokerasModel
from video_handlers.cv_video_handler import VideoHandler
from system_action_handlers.mouse_action_handler import MouseActionHandler


class AppCameraHandler:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.detector = mp_detector.MediapipeHandDetector(0.5, 0.5)
        self.video_handler = VideoHandler(width=640, height=480)
        self.frame_counter = 0
        self.skip_frames = 1
        self.fps = 0
        self.last_frame_time = time.time()
        self.mouseController = MouseActionHandler(10)

    def get_camera_image(self, is_running, config_vars, model):
        _, frame = self.video_handler.get_screen()
        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self._process_hand(frame, is_running, config_vars, model)

        img = Image.fromarray(frame)
        return ImageTk.PhotoImage(img)

    def _process_hand(self, frame, is_running, config_vars, model):
        if not is_running:
            return

        current_time = time.time()
        if current_time - self.last_frame_time > 0:
            self.fps = 1.0 / (current_time - self.last_frame_time)
        self.last_frame_time = current_time


        # if self.frame_counter == self.skip_frames:
        #     self.frame_counter = 0
        #     return
        # self.frame_counter += 1
        frame_height, frame_width = frame.shape[:2]

        s1_x = frame_width // 5
        s1_y = frame_height // 5
        s2_x = 4 * frame_width // 5
        s2_y = 4 * frame_height // 5
        x1 = 2 * frame_width // 5
        x2 = 3 * frame_width // 5
        y1 = 2 * frame_height // 5
        y2 = 3 * frame_height // 5

        hand_boxes, hand_landmarks_list, hand_types = self.detector.detect_hands(frame)
        for (box, landmark, hand_type) in zip(hand_boxes, hand_landmarks_list, hand_types):
            min_x, min_y, max_x, max_y = box
            # Отрисовка
            if config_vars.get("show_bbox", False):
                cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
            if config_vars.get("show_skeleton", False):
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
            hand_roi = cv2.resize(hand_roi, (50, 50), interpolation=cv2.INTER_AREA)

            # Предсказание жеста
            prediction = model.predict(hand_roi)
            gesture = f"{hand_type}: {prediction}"

            # Отображение результата
            cv2.putText(frame, gesture, (min_x, min_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            self._show_cursor_point(hand_types, hand_type, landmark, frame, frame_width, frame_height, x1, x2, y1, y2,
                                    s1_x, s1_y, s2_x, s2_y)

        self._show_fps(config_vars, frame, frame_width)
        self._show_grid(config_vars, frame, frame_width, frame_height, x1, x2, y1, y2, s1_x, s1_y, s2_x, s2_y)

    def _show_cursor_point(self, hand_types, hand_type, landmark, frame, frame_width, frame_height, x1, x2, y1, y2,
                           s1_x, s1_y, s2_x, s2_y):
        if len(hand_types) == 1 or hand_type == "Right":
            palm_points = [0, 5, 17]

            coords = np.array([
                [landmark.landmark[i].x * frame_width, landmark.landmark[i].y * frame_height]
                for i in palm_points
            ])

            center = coords.mean(axis=0).astype(int)
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
            "model_name": os.listdir("models")[0],
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