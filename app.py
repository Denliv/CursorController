import tkinter as tk
from doctest import master

import mediapipe as mp
import cv2
import numpy as np
import os

from tkinter import ttk
from PIL import Image, ImageTk
from hand_detectors import mediapipe_hand_detector as mp_detector
from utils.app_utils import AppCameraHandler
from video_handlers.cv_video_handler import VideoHandler

# TODO Julia lang | AutoML | Flux.jl

def show_camera_image(label, time=20):
    photo_image = camera_handler.get_camera_image()
    label.photo_image = photo_image
    label.configure(image=photo_image)
    label.after(time, show_camera_image, label, time)

def configure_camera_frame(side):
    left_frame = tk.Frame(main_frame, width=cam_width, bg="gray")
    left_frame.pack(side=side, fill="both", expand=True)
    label_cam = tk.Label(left_frame)
    label_cam.pack(fill="both", expand=True)
    show_camera_image(label=label_cam, time=20)

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def update_all_optionmenus():
    used = set(val.get() for val in variables.values() if val.get() != 'не выбрано')
    for i, var in variables.items():
        current = var.get()
        menu = option_menus[i]["menu"]
        menu.delete(0, "end")
        for option in options:
            if option == current or (option not in used and option != 'не выбрано'):
                menu.add_command(label=option, command=lambda v=var, o=option: on_select(v, o))
        # Добавим "не выбрано" всегда
        if 'не выбрано' not in [menu.entrycget(j, "label") for j in range(menu.index("end")+1)]:
            menu.add_command(label='не выбрано', command=lambda v=var: on_select(v, 'не выбрано'))

def on_select(var, value):
    var.set(value)
    update_all_optionmenus()

# Настройка камеры и детектора
camera_handler = AppCameraHandler()

# Настройки окна
cam_width, cam_height = camera_handler.get_camera_parameters()
list_width = 300
root = tk.Tk()
root.title("Cursor Controller")
root.geometry(f"{cam_width+list_width}x600")

# Основной фрейм
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# Левая часть — видео
configure_camera_frame("left")

# Правая часть — список
right_frame = tk.Frame(main_frame, width=list_width)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

options = ['не выбрано', 'а', 'б', 'в', 'г', 'д']

hand_gestures = [
    'call', 'dislike', 'fist', 'four', 'like', 'mute', 'ok', 'one', 'palm',
    'peace', 'peace_inverted', 'rock', 'stop', 'stop_inverted', 'three',
    'three2', 'two_up', 'two_up_inverted'
]

# Прокручиваемая область
canvas = tk.Canvas(right_frame, width=list_width-45)
scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Словарь для хранения изображений (чтобы избежать удаления сборщиком мусора)
gesture_images = {}
variables = {}
option_menus = {}

for index, gesture in enumerate(hand_gestures):
    frame = tk.Frame(scrollable_frame)
    frame.pack(fill="x", pady=5)

    image_path = os.path.join("images", f"{gesture}.png")
    try:
        img = Image.open(image_path).resize((100, 100), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        gesture_images[gesture] = photo  # сохранить ссылку
        img_label = tk.Label(frame, image=photo)
        img_label.pack(side="left", padx=5)
    except Exception as e:
        img_label = tk.Label(frame, text="[нет изображения]")
        img_label.pack(side="left", padx=5)
        print(f"Ошибка при загрузке {image_path}: {e}")

    var = tk.StringVar(value=options[0])
    dropdown = ttk.OptionMenu(frame, var, options[0], *options)
    dropdown.pack(side="left")

    variables[gesture] = var
    option_menus[gesture] = dropdown

update_all_optionmenus()

root.bind('<Escape>', lambda e: root.quit())
root.mainloop()