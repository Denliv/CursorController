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

    def predict(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        image = np.array(image).astype("float32") / 255.0
        image = np.expand_dims(image, axis=0)

        predictions = self.model.predict(image)
        class_idx = np.argmax(predictions, axis=1)[0]

        return self.classes[class_idx]