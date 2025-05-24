import autokeras as ak
import cv2
import keras
import numpy as np


class AutokerasModel:
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = keras.models.load_model(f"models/{model_name}", custom_objects=ak.CUSTOM_OBJECTS)
        self.classes = [
            'call', 'dislike', 'fist', 'four', 'like', 'mute', 'no_gesture', 'ok', 'one', 'palm',
            'peace', 'peace_inverted', 'rock', 'stop', 'stop_inverted', 'three',
            'three2', 'two_up', 'two_up_inverted'
        ]
        self.last_prediction = None
        self.last_center = None
        self.cache_threshold = 5

    def predict(self, image, hand_center=None):
        if hand_center is not None and self.last_center is not None:
            if np.linalg.norm(np.array(hand_center) - np.array(self.last_center)) < self.cache_threshold:
                return self.last_prediction

        image = cv2.resize(image, (50, 50), interpolation=cv2.INTER_AREA)
        image = np.array(image).astype("float32") / 255.0
        image = np.expand_dims(image, axis=0)

        # Предсказание
        predictions = self.model.predict(image, verbose=0)
        class_idx = np.argmax(predictions, axis=1)[0]
        prediction = self.classes[class_idx]

        # Кэширование
        self.last_prediction = prediction
        self.last_center = hand_center

        return prediction