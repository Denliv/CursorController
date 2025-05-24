import os
import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk

from PIL import Image, ImageTk

from model_api.ModelFactory import ModelFactory
from utils.app_utils import AppCameraHandler, ConfigHandler


def configure_app_window():
    # ff_width, ff_height = camera_handler.get_camera_parameters()
    # sf_width = 300
    window = tk.Tk()
    window.title("Cursor Controller")
    window.resizable(True, True)
    # window.minsize(ff_width + sf_width, 400)
    window.bind('<Escape>', lambda e: on_exit())
    window.protocol("WM_DELETE_WINDOW", on_closing)
    return window


def on_exit():
    root.quit()
    on_closing()


def on_closing():
    global camera_handler, config_handler, config_vars
    del camera_handler
    config_handler.save_config(config_vars)
    root.destroy()


def configure_main_frame():
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)
    return frame


def configure_camera_frame(side):
    left_frame = tk.Frame(main_frame, bg="gray")
    left_frame.pack(side=side, fill="both", expand=True)
    label_cam = tk.Label(left_frame)
    label_cam.pack(fill="both", expand=True)
    show_camera_image(label=label_cam)


def show_camera_image(label):
    global is_running, config_vars, camera_handler, model
    time_period = config_vars.get("frame_time_period", 33)
    photo_image = camera_handler.get_camera_image(is_running, config_vars, model)
    label.photo_image = photo_image
    label.configure(image=photo_image)
    label.after(time_period, show_camera_image, label)


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
    for index, gesture in enumerate(hand_gestures_active, start=1):
        frame = tk.Frame(scrolling_frame)
        frame.pack(fill="x", pady=5)

        number_label = tk.Label(frame, text=f"{index}.", anchor="w")
        number_label.pack(side="left")
        number_label.configure(font=("Arial", 12))

        image_path = os.path.join("images", f"{gesture}.png")
        if not os.path.exists(image_path):
            image_path = os.path.join("images", "no_image.png")
        try:
            photo = ImageTk.PhotoImage(Image.open(image_path).resize((hand_gesture_img_size, hand_gesture_img_size), Image.Resampling.BOX))
            gesture_images[gesture] = photo
            img_label = tk.Label(frame, image=photo)
            img_label.pack(side="left", padx=5)
        except Exception:
            img_label = tk.Label(frame, text=f"[{gesture}]")
            img_label.pack(side="left", padx=5)

        global config_vars

        selected_option = tk.StringVar(value=config_vars.get(f"{gesture}", default_option))
        dropdown = ttk.OptionMenu(frame, selected_option, selected_option.get(), *options, style='my.TMenubutton')
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
    global config_vars
    if config_vars.get("multiple_gestures", False):
        used = set()
    else:
        used = set(val.get() for val in actions.values() if val.get() != default_option)
    for gesture_name, action in actions.items():
        current_action = action.get()
        gesture_menu = option_menu[gesture_name]["menu"]
        gesture_menu.delete(0, "end")

        for option in options:
            if option == current_action or option == default_option or (
                    option not in used and option != default_option):
                gesture_menu.add_command(label=option, command=lambda v=action, o=option: on_select(v, o))

        config_vars[gesture_name] = current_action


def on_select(action, value):
    action.set(value)
    update_gestures_option_menu()


def save_config_callback(var, var_param):
    global config_vars
    config_vars[var_param] = var.get()


def clear_hand_gestures_settings():
    global hand_gestures_active
    for gesture, action in actions.items():
        action.set(default_option)
        config_vars[gesture] = default_option


def clear_model_param():
    global model
    model = None


def ask_time_period(var):
    var.set(simpledialog.askinteger("", "Set frames time period([20, 60], ms):", initialvalue=var.get(), minvalue=20, maxvalue=60))


def ask_frame_skip(var):
    var.set(simpledialog.askinteger("", "Set skip frames value([0, 5]):", initialvalue=var.get(), minvalue=0, maxvalue=5))


def configure_menu_panel():
    global main_menu
    main_menu = tk.Menu(tearoff=0)
    settings_menu = tk.Menu(tearoff=0, title="Settings")

    global config_vars, model_var, model

    # Переменные Settings меню
    show_fps_var = tk.BooleanVar(value=config_vars.get("show_fps", False))
    show_bbox_var = tk.BooleanVar(value=config_vars.get("show_bbox", False))
    show_skeleton_var = tk.BooleanVar(value=config_vars.get("show_skeleton", False))
    multiple_gestures_var = tk.BooleanVar(value=config_vars.get("multiple_gestures", False))
    show_grid_var = tk.BooleanVar(value=config_vars.get("show_grid", False))
    model_var = tk.StringVar(value=config_vars.get("model_name", models_list[0]))
    time_period_var = tk.IntVar(value=config_vars.get("frame_time_period", 33))
    frame_skip_var = tk.IntVar(value=config_vars.get("frame_skip", 2))

    show_fps_var.trace("w", lambda *args: save_config_callback(show_fps_var, "show_fps"))
    show_bbox_var.trace("w", lambda *args: save_config_callback(show_bbox_var, "show_bbox"))
    show_skeleton_var.trace("w", lambda *args: save_config_callback(show_skeleton_var, "show_skeleton"))
    multiple_gestures_var.trace("w", lambda *args: (clear_hand_gestures_settings(), save_config_callback(multiple_gestures_var, "multiple_gestures")))
    show_grid_var.trace("w", lambda *args: save_config_callback(show_grid_var, "show_grid"))
    model_var.trace("w", lambda *args: (clear_model_param(), save_config_callback(model_var, "model_name")))
    time_period_var.trace("w", lambda *args: save_config_callback(time_period_var, "frame_time_period"))
    frame_skip_var.trace("w", lambda *args: save_config_callback(frame_skip_var, "frame_skip"))

    settings_menu.add_checkbutton(label="Show FPS", variable=show_fps_var)
    settings_menu.add_checkbutton(label="Show Hand bounding box", variable=show_bbox_var)
    settings_menu.add_checkbutton(label="Show hand skeleton", variable=show_skeleton_var)
    settings_menu.add_checkbutton(label="Multiple gestures for action", variable=multiple_gestures_var)
    settings_menu.add_checkbutton(label="Show Grid", variable=show_grid_var)

    models_menu = tk.Menu(settings_menu, tearoff=0)
    for model_name in models_list:
        models_menu.add_radiobutton(label=f"{model_name}", variable=model_var, value=model_name)

    settings_menu.add_cascade(label="Model", menu=models_menu)
    settings_menu.add_command(label="Frames time period", command=lambda: ask_time_period(time_period_var))
    settings_menu.add_command(label="Skip frames", command=lambda: ask_frame_skip(frame_skip_var))

    main_menu.add_cascade(label="Settings", menu=settings_menu)
    root.config(menu=main_menu)


def configure_bottom_panel():
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(side="bottom", fill="x")

    def toggle():
        global is_running, config_vars, actions
        if is_running:
            is_running = False
            button.config(text="Start", bg="green", activebackground="green")
            main_menu.entryconfig("Settings", state="normal")
            for dropdown in option_menu.values():
                dropdown.config(state="normal")
        else:
            global config_handler, model
            button.config(text="Stop", bg="red", activebackground="red")
            config_handler.save_config(config_vars)
            main_menu.entryconfig("Settings", state="disabled")
            for dropdown in option_menu.values():
                dropdown.config(state="disabled")
            if model is None:
                model = model_factory.create_model(config_vars.get("model_name", models_list[0]))
            is_running = True

    button = tk.Button(bottom_frame, text="Start", command=toggle, font=global_font, bg="green",
                       activebackground="green")
    button.pack(fill="x", expand=True, padx=10, pady=10)


# Определяем вспомогательные массивы
default_option = "not selected"
options = [default_option, 'right click', 'left click', 'middle click', 'double click', 'scroll up', 'scroll down',
           'step back', 'step forward', 'press left button', 'release left button', 'custom action']

hand_gestures_active = [
    'call', 'dislike', 'fist', 'four', 'like', 'mute', 'ok', 'one', 'palm',
    'peace', 'peace_inverted', 'rock', 'stop', 'stop_inverted', 'three',
    'three2', 'two_up', 'two_up_inverted'
]

models_list = os.listdir("models")

# Словарь для сохранение картинок в меню
gesture_images = {}

# Словарь для сохранения "жест": str - "действие": StrVal
actions = {}

# Словарь всех dropdown меню жестов в приложении
option_menu = {}

# Размер картинки жеста в меню
hand_gesture_img_size = 100

# Определяем переменные меню
model_var = None
main_menu = None
is_running = False

# Настройки окна
root = configure_app_window()

# Настройка хэндлеров
camera_handler = AppCameraHandler()
config_handler = ConfigHandler("config.json", hand_gestures_active, default_option)
config_vars = config_handler.load_config()

# Определяем хэндлер для моделей классификации
model_factory = ModelFactory()

# Определяем переменную для модели классификации
model = None

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
configure_camera_frame(side="left")

# Правая часть — список
configure_scrolling_frame("right")

update_gestures_option_menu()

root.mainloop()
