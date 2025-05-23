import os

from model_api import AutokerasModel, YoloModel


class ModelFactory:
    _AUTOKERAS_MODELS = {
        "autokeras_efficient.keras",
        "autokeras_resnet.keras",
        "autokeras_vanilla.keras",
        "autokeras_xception.keras"
    }
    _YOLO_MODELS = {
        "yolo11.pt"
    }
    _MODEL_CLASSES = {
        "autokeras": AutokerasModel.AutokerasModel,
        "yolo": YoloModel.YoloModel
    }

    def create_model(self, model_name):
        if model_name in self._AUTOKERAS_MODELS:
            cls = self._MODEL_CLASSES.get("autokeras")
        elif model_name in self._YOLO_MODELS:
            cls = self._MODEL_CLASSES.get("yolo")
        else:
            raise ValueError(f"Неизвестная модель: {model_name}")

        # Проверяем, что класс найден
        if cls is None:
            raise ValueError(f"Класс для модели '{model_name}' не найден в MODEL_CLASSES")

        # Проверяем существование файла
        if not os.path.exists(f"models/{model_name}"):
            raise FileNotFoundError(f"Файл модели не найден: {model_name}")

        return cls(model_name)