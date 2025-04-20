from re import error

import mediapipe as mp
import cv2
import numpy as np

from hand_detectors import mediapipe_hand_detector as mp_detector
from video_handlers.cv_video_handler import VideoHandler

# библиотеки для контроля мыши: pynput, pyautogui, autopy


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
detector = mp_detector.MediapipeHandDetector(0.7, 0.7)
video_handler = VideoHandler()

#TODO захватывать не только камеру, но и экран пользователя
while True:
    ret, frame = video_handler.get_screen()

    if not ret:
        break

    # Инвертирование кадра
    frame = cv2.flip(frame, 1)

    # Обнаружение рук
    hand_boxes, hand_landmarks_list, hand_types = detector.detect_hands(frame)

    for (box, landmark, hand_type) in zip(hand_boxes, hand_landmarks_list, hand_types):
        min_x, min_y, max_x, max_y = box

        # Отрисовка
        cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
        mp_drawing.draw_landmarks(frame,
                                  landmark,
                                  mp_hands.HAND_CONNECTIONS,
                                  mp_drawing_styles.get_default_hand_landmarks_style(),
                                  mp_drawing_styles.get_default_hand_connections_style())

        # Выделение области руки
        hand_roi = frame[min_y:max_y, min_x:max_x]
        if hand_roi.size == 0:
            continue

        # Подготовка изображения для модели
        hand_roi = cv2.resize(hand_roi, (64, 64))
        hand_roi = np.expand_dims(hand_roi, axis=0)

        # Предсказание жеста
        # prediction = model.predict(hand_roi)
        # gesture = class_names[prediction[0]]
        gesture = hand_type + ": " + "prediction"

        # Отображение результата
        cv2.putText(frame, gesture, (min_x, min_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.namedWindow("Hand Gesture Recognition", cv2.WINDOW_AUTOSIZE)
    cv2.imshow('Hand Gesture Recognition', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
