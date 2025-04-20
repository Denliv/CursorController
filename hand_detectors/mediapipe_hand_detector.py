import cv2
import mediapipe as mp
import numpy as np


class MediapipeHandDetector:
    def __init__(self, detection_confidence=0.5, tracking_confidence=0.5):
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

    def detect_hands(self, frame):
        results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if not results.multi_hand_landmarks:
            return [], [], []

        hand_bounding_boxes = []
        hand_landmarks = results.multi_hand_landmarks
        hand_types = [x.classification[0].label for x in results.multi_handedness]
        height, width = frame.shape[:2]

        for hand_landmark in hand_landmarks:
            # Получение координат bounding box
            coords = np.array([(landmark.x * width, landmark.y * height) for landmark in hand_landmark.landmark])
            min_x, min_y = np.min(coords, axis=0)
            max_x, max_y = np.max(coords, axis=0)

            # Добавление отступа
            padding = round(max(max_x - min_x, max_y - min_y) / 7)
            min_x = max(0, int(min_x) - padding)
            min_y = max(0, int(min_y) - padding)
            max_x = min(width, int(max_x) + padding)
            max_y = min(height, int(max_y) + padding)

            hand_bounding_boxes.append((min_x, min_y, max_x, max_y))

        return hand_bounding_boxes, hand_landmarks, hand_types