import os

from model_api import AutokerasModel, YoloModel


class ModelFactory:
    _MODEL_MAP = {
        "autokeras_efficient.keras": AutokerasModel.AutokerasModel,
        "autokeras_resnet.keras": AutokerasModel.AutokerasModel,
        "autokeras_vanilla.keras": AutokerasModel.AutokerasModel,
        "autokeras_xception.keras": AutokerasModel.AutokerasModel,
        "yolo11.pt": YoloModel.YoloModel
    }

    def create_model(self, model_name):
        if model_name not in self._MODEL_MAP:
            raise ValueError(f"Неизвестная модель: {model_name}")

        model_path = f"models/{model_name}"
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Файл модели не найден: {model_path}")

        cls = self._MODEL_MAP[model_name]
        return cls(model_name)