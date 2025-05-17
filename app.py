import tkinter as tk
import mediapipe as mp
import cv2
import numpy as np
import os

from tkinter import ttk
from PIL import Image, ImageTk
from utils.app_utils import AppCameraHandler

# TODO Julia lang | AutoML | Flux.jl

def configure_app_window():
    ff_width, ff_height = camera_handler.get_camera_parameters()
    sf_width = 300
    window = tk.Tk()
    window.title("Cursor Controller")
    window.geometry(f"{ff_width + sf_width}x600")
    window.bind('<Escape>', lambda e: window.quit())
    return window, ff_width, ff_height, sf_width

def configure_main_frame():
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)
    return frame

def configure_camera_frame(side, time=20):
    left_frame = tk.Frame(main_frame, width=cam_width, bg="gray")
    left_frame.pack(side=side, fill="both", expand=True)
    label_cam = tk.Label(left_frame)
    label_cam.pack(fill="both", expand=True)
    show_camera_image(label=label_cam, time=time)

def show_camera_image(label, time=20):
    photo_image = camera_handler.get_camera_image()
    label.photo_image = photo_image
    label.configure(image=photo_image)
    label.after(time, show_camera_image, label, time)

def configure_scrolling_frame(side, width):
    right_frame = tk.Frame(main_frame, width=width)
    right_frame.pack(side=side, fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(right_frame, width=list_width - 45)
    scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    canvas.bind("<Enter>", lambda e: _bind_mousewheel(canvas))
    canvas.bind("<Leave>", lambda e: _unbind_mousewheel(canvas))

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    fill_scrolling_frame(scrollable_frame)

def fill_scrolling_frame(scrolling_frame):
    for index, gesture in enumerate(hand_gestures):
        frame = tk.Frame(scrolling_frame)
        frame.pack(fill="x", pady=5)

        image_path = os.path.join("images", f"{gesture}.png")
        if not os.path.exists(image_path):
            image_path = os.path.join("images", "no_image.png")
        try:
            photo = ImageTk.PhotoImage(Image.open(image_path).resize((IMG_SIZE, IMG_SIZE), Image.Resampling.BOX))
            gesture_images[gesture] = photo
            img_label = tk.Label(frame, image=photo)
            img_label.pack(side="left", padx=5)
        except Exception as e:
            img_label = tk.Label(frame, text="[нет изображения]")
            img_label.pack(side="left", padx=5)

        selected_option = tk.StringVar(value=options[0])
        dropdown = ttk.OptionMenu(frame, selected_option, options[0], *options)
        dropdown.pack(side="left")

        actions[gesture] = selected_option
        option_menu[gesture] = dropdown

def _bind_mousewheel(widget):
    # Windows и MacOS
    widget.bind_all("<MouseWheel>", lambda e: _on_mousewheel(e, widget))
    # Linux
    widget.bind_all("<Button-4>", lambda e: _on_mousewheel(e, widget))
    widget.bind_all("<Button-5>", lambda e: _on_mousewheel(e, widget))

def _unbind_mousewheel(widget):
    widget.unbind_all("<MouseWheel>")
    widget.unbind_all("<Button-4>")
    widget.unbind_all("<Button-5>")

def _on_mousewheel(event, widget):
    widget.yview_scroll(int(-1 * (event.delta / 120)), "units")

def update_gestures_option_menu():
    used = set(val.get() for val in actions.values() if val.get() != 'не выбрано')
    for gesture_name, action in actions.items():
        current_action = action.get()
        gesture_menu = option_menu[gesture_name]["menu"]
        gesture_menu.delete(0, "end")

        for option in options:
            if option == current_action or option == 'не выбрано' or (option not in used and option != 'не выбрано'):
                gesture_menu.add_command(label=option, command=lambda v=action, o=option: on_select(v, o))

def on_select(action, value):
    action.set(value)
    update_gestures_option_menu()

def configure_settings_panel(parent):
    settings_frame = tk.Frame(parent, bg="#ddd", pady=5)
    settings_frame.pack(side="top", fill="x")

    # Пример: Поле ввода FPS
    tk.Label(settings_frame, text="FPS:", bg="#ddd").pack(side="left", padx=(10, 2))
    fps_entry = tk.Entry(settings_frame, width=5)
    fps_entry.insert(0, "20")
    fps_entry.pack(side="left", padx=(0, 10))

    # Пример: Чекбокс для отладки
    debug_var = tk.BooleanVar(value=False)
    debug_check = tk.Checkbutton(settings_frame, text="Debug", variable=debug_var, bg="#ddd")
    debug_check.pack(side="left")

    # Пример: Кнопка применения
    def apply_settings():
        try:
            fps = int(fps_entry.get())
            if fps <= 0:
                raise ValueError
            print(f"FPS set to: {fps}")
            # Можно передать значение fps в show_camera_image или другую функцию
        except ValueError:
            print("Некорректное значение FPS")

        print("Debug mode:", debug_var.get())

    apply_button = tk.Button(settings_frame, text="Применить", command=apply_settings)
    apply_button.pack(side="left", padx=10)

options = ['не выбрано', 'а', 'б', 'в', 'г', 'д']

hand_gestures = [
    'call', 'dislike', 'fist', 'four', 'like', 'mute', 'ok', 'one', 'palm',
    'peace', 'peace_inverted', 'rock', 'stop', 'stop_inverted', 'three',
    'three2', 'two_up', 'two_up_inverted'
]

gesture_images = {}
actions = {}
option_menu = {}
IMG_SIZE = 100

# Настройка камеры и детектора
camera_handler = AppCameraHandler()

# Настройки окна
root, cam_width, cam_height, list_width = configure_app_window()

# Панель настроек
configure_settings_panel(root)

# Основной фрейм
main_frame = configure_main_frame()

# Левая часть — видео
configure_camera_frame("left", 20)

# Правая часть — список
configure_scrolling_frame("right", list_width)

update_gestures_option_menu()

root.mainloop()