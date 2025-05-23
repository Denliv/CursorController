from ultralytics import YOLO

class YoloModel:
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = YOLO(f"models/{model_name}")
        self.classes = [
            'call', 'dislike', 'fist', 'four', 'like', 'mute', 'no_gesture', 'ok', 'one', 'palm',
            'peace', 'peace_inverted', 'rock', 'stop', 'stop_inverted', 'three',
            'three2', 'two_up', 'two_up_inverted'
        ]

    def predict(self, image):
        return self.classes[self.model.predict(image)[0].probs.top1]