import tkinter as tk
import mediapipe as mp
import cv2
import numpy as np
import os

from tkinter import ttk
from PIL import Image, ImageTk
from utils.app_utils import AppCameraHandler, ConfigHandler


# TODO Julia lang | AutoML | Flux.jl

def configure_app_window():
    # ff_width, ff_height = camera_handler.get_camera_parameters()
    # sf_width = 300
    window = tk.Tk()
    window.title("Cursor Controller")
    window.resizable(True, True)
    # window.minsize(ff_width + sf_width, 400)
    window.bind('<Escape>', lambda e: window.quit())
    window.protocol("WM_DELETE_WINDOW", on_closing)
    return window


def on_closing():
    global camera_handler
    del camera_handler
    root.destroy()


def configure_main_frame():
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)
    return frame


def configure_camera_frame(side, time=33):
    left_frame = tk.Frame(main_frame, bg="gray")
    left_frame.pack(side=side, fill="both", expand=True)
    label_cam = tk.Label(left_frame)
    label_cam.pack(fill="both", expand=True)
    show_camera_image(label=label_cam, time=time)


def show_camera_image(label, time):
    global is_running, config_vars
    photo_image = camera_handler.get_camera_image(is_running, config_vars)
    label.photo_image = photo_image
    label.configure(image=photo_image)
    label.after(time, show_camera_image, label, time)


def configure_scrolling_frame(side):
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=side, fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(right_frame)
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
    for index, gesture in enumerate(hand_gestures, start=1):
        frame = tk.Frame(scrolling_frame)
        frame.pack(fill="x", pady=5)

        number_label = tk.Label(frame, text=f"{index}.", anchor="w")
        number_label.pack(side="left")
        number_label.configure(font=("Arial", 12))

        image_path = os.path.join("images", f"{gesture}.png")
        if not os.path.exists(image_path):
            image_path = os.path.join("images", "no_image.png")
        try:
            photo = ImageTk.PhotoImage(Image.open(image_path).resize((IMG_SIZE, IMG_SIZE), Image.Resampling.BOX))
            gesture_images[gesture] = photo
            img_label = tk.Label(frame, image=photo)
            img_label.pack(side="left", padx=5)
        except Exception:
            img_label = tk.Label(frame, text=f"[{gesture}]")
            img_label.pack(side="left", padx=5)

        selected_option = tk.StringVar(value=default_option)
        dropdown = ttk.OptionMenu(frame, selected_option, default_option, *options, style='my.TMenubutton')
        dropdown["menu"].configure(font=("Arial", 12), activebackground="#000")
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
    global config
    if config.get("multiple_gestures", False):
        return
    used = set(val.get() for val in actions.values() if val.get() != default_option)
    for gesture_name, action in actions.items():
        current_action = action.get()
        gesture_menu = option_menu[gesture_name]["menu"]
        gesture_menu.delete(0, "end")

        for option in options:
            if option == current_action or option == default_option or (
                    option not in used and option != default_option):
                gesture_menu.add_command(label=option, command=lambda v=action, o=option: on_select(v, o))


def on_select(action, value):
    action.set(value)
    update_gestures_option_menu()


def configure_menu_panel():
    global main_menu
    main_menu = tk.Menu(tearoff=0)
    settings_menu = tk.Menu(tearoff=0, title="Settings")

    # Загружаем config
    global config

    # Переменные Settings меню
    show_fps_var = tk.BooleanVar(value=config.get("show_fps", False))
    show_bbox_var = tk.BooleanVar(value=config.get("show_bbox", False))
    show_skeleton_var = tk.BooleanVar(value=config.get("show_skeleton", False))
    multiple_gestures_var = tk.BooleanVar(value=config.get("multiple_gestures", False))
    global model_var
    model_var = tk.StringVar(value=config.get("model_name", models[0]))

    def save_config_callback(*args):
        new_config = {
            "show_fps": show_fps_var.get(),
            "show_bbox": show_bbox_var.get(),
            "show_skeleton": show_skeleton_var.get(),
            "multiple_gestures": multiple_gestures_var.get(),
            "model_name": model_var.get()
        }
        config_handler.save_config(new_config)

    show_fps_var.trace("w", save_config_callback)
    show_bbox_var.trace("w", save_config_callback)
    show_skeleton_var.trace("w", save_config_callback)
    multiple_gestures_var.trace("w", save_config_callback)
    model_var.trace("w", save_config_callback)

    # Настройка Settings
    settings_menu.add_checkbutton(label="Show FPS", variable=show_fps_var)
    settings_menu.add_checkbutton(label="Show Hand bounding box", variable=show_bbox_var)
    settings_menu.add_checkbutton(label="Show hand skeleton", variable=show_skeleton_var)
    settings_menu.add_checkbutton(label="Multiple gestures for action", variable=multiple_gestures_var)

    models_menu = tk.Menu(settings_menu, tearoff=0)
    for model_name in models:
        models_menu.add_radiobutton(label=f"{model_name}", variable=model_var, value=model_name)

    settings_menu.add_cascade(label="Model", menu=models_menu)

    main_menu.add_cascade(label="Settings", menu=settings_menu)
    root.config(menu=main_menu)


def configure_bottom_panel():
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(side="bottom", fill="x")

    def toggle():
        global is_running, config_vars
        if is_running:
            button.config(text="Start", bg="green", activebackground="green")
            is_running = False
            main_menu.entryconfig("Settings", state="normal")
            for dropdown in option_menu.values():
                dropdown.config(state="normal")
        else:
            button.config(text="Stop", bg="red", activebackground="red")
            is_running = True
            config_vars = config_handler.load_config()
            main_menu.entryconfig("Settings", state="disabled")
            for dropdown in option_menu.values():
                dropdown.config(state="disabled")

    button = tk.Button(bottom_frame, text="Start", command=toggle, font=global_font, bg="green",
                       activebackground="green")
    button.pack(fill="x", expand=True, padx=10, pady=10)


# Определяем вспомогательные массивы
default_option = "not selected"
options = [default_option, 'right click', 'left click', 'middle click', 'double click', 'scroll up', 'scroll down',
           'step back', 'step forward', 'custom action']

hand_gestures = [
    'call', 'dislike', 'fist', 'four', 'like', 'mute', 'ok', 'one', 'palm',
    'peace', 'peace_inverted', 'rock', 'stop', 'stop_inverted', 'three',
    'three2', 'two_up', 'two_up_inverted'
]

models = [os.path.splitext(f)[0] for f in os.listdir("models")]

gesture_images = {}
actions = {}
option_menu = {}
IMG_SIZE = 100

# Определяем переменные меню
model_var = None
main_menu = None
is_running = False
config_vars = None

# Настройка хэндлеров
camera_handler = AppCameraHandler()
config_handler = ConfigHandler("config.json")
config = config_handler.load_config()

# Настройки окна
root = configure_app_window()

# Определяем стиль шрифта
global_font = ('Arial', 12)
style = ttk.Style()
style.configure('my.TMenubutton', font=global_font)

# Панель настроек
configure_menu_panel()

configure_bottom_panel()

# Основной фрейм
main_frame = configure_main_frame()

# Левая часть — видео
configure_camera_frame(side="left", time=33)

# Правая часть — список
configure_scrolling_frame("right")

update_gestures_option_menu()

root.mainloop()
