import torch
import torchvision.models as models
from torchvision import transforms
from torchvision.models import ResNet152_Weights

def load_model(model_path, num_classes=34, device='cuda' if torch.cuda.is_available() else 'cpu'):
    # Загружаем ResNet152 без предобученных весов
    model = models.resnet152(weights=None)

    # Модифицируем последний слой под наше количество классов
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)

    # Загружаем веса модели (с учетом безопасной загрузки)
    checkpoint = torch.load(model_path, map_location=device, weights_only=True)

    # Извлекаем веса модели
    state_dict = checkpoint.get('MODEL_STATE', checkpoint)

    # Удаляем num_batches_tracked (если есть)
    state_dict = {k: v for k, v in state_dict.items() if 'num_batches_tracked' not in k}

    # Загружаем веса
    model.load_state_dict(state_dict, strict=False)

    model = model.to(device)
    model.eval()

    return model


def initial():
    MODEL_PATH = 'gesture_classifiers/models/ResNet152.pth'
    GESTURE_CLASSES = [
        'grabbing', 'grip', 'holy', 'point', 'call', 'three3', 'timeout', 'xsign', 'hand_heart', 'hand_heart2',
        'little_finger', 'middle_finger', 'take_picture', 'dislike', 'fist', 'four', 'like', 'mute', 'ok', 'one',
        'palm', 'peace', 'peace_inverted', 'rock', 'stop', 'stop_inverted', 'three', 'three2', 'two_up',
        'two_up_inverted', 'three_gun', 'thumb_index', 'thumb_index2'
    ]
    NUM_CLASSES = 34

    # Загрузка модели
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = load_model(MODEL_PATH, NUM_CLASSES, device)
    # Преобразования для входного изображения (должны соответствовать тем, что использовались при обучении)
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),  # ResNet ожидает 224x224
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    return model, transform, device


def predict_gesture(image, model, transform, device):
    # Применение преобразований и добавление размерности batch
    image = transform(image).unsqueeze(0).to(device)

    # Предсказание
    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs.data, 1)

    return predicted.item()  # Возвращаем индекс класса
