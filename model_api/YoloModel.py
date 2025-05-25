import os

import cv2
import numpy as np
from ultralytics import YOLO

from app_utils import resource_path


class YoloModel:
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = YOLO(resource_path(os.path.join("models", model_name)))
        self.classes = [
            'call', 'dislike', 'fist', 'four', 'like', 'mute', 'no_gesture', 'ok', 'one', 'palm',
            'peace', 'peace_inverted', 'rock', 'stop', 'stop_inverted', 'three',
            'three2', 'two_up', 'two_up_inverted'
        ]
        self.last_prediction = None
        self.last_center = None
        self.cache_threshold = 0

    def predict(self, image, hand_center=None):
        if hand_center is not None and self.last_center is not None:
            if np.linalg.norm(np.array(hand_center) - np.array(self.last_center)) < self.cache_threshold:
                return self.last_prediction

        # Предобработка
        image = cv2.resize(image, (64, 64), interpolation=cv2.INTER_AREA)

        # Предсказание
        results = self.model.predict(image, verbose=False)[0]
        prediction = self.classes[results.probs.top1]

        # Кэширование
        self.last_prediction = prediction
        self.last_center = hand_center

        return prediction