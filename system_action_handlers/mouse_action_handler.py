import math

from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as ButtonController


class MouseActionHandler:
    def __init__(self, mouse_speed_near, mouse_speed_far=None):
        self.mouse = ButtonController()
        self.keyboard = KeyboardController()
        self.mouse_speed_near = mouse_speed_near
        if mouse_speed_far is not None:
            self.mouse_speed_far = mouse_speed_far
        else:
            self.mouse_speed_far = 4 * mouse_speed_near
        self.action_map = {
            'right click': self.right_click,
            'left click': self.left_click,
            'middle click': self.middle_click,
            'double click': self.double_click,
            'scroll up': self.scroll_up,
            'scroll down': self.scroll_down,
            'step back': self.step_back,
            'step forward': self.step_forward,
            'press left button': self.press_left_button,
            'release left button': self.release_left_button,
            'custom action': self.custom_action
        }

    def move_mouse(self, center, x1, x2, y1, y2, s1_x, s1_y, s2_x, s2_y):
        x, y = center

        # Определяем скорость
        if s1_x <= x <= s2_x and s1_y <= y <= s2_y:
            speed = self.mouse_speed_near
        else:
            speed = self.mouse_speed_far
        diagonal_speed = math.ceil(speed / 1.414)

        # Определяем зону (N, S, E, W, NE, NW, SE, SW, Center)
        if x1 <= x <= x2 and y1 <= y <= y2:
            # Center: не двигаем курсор
            return
        elif x > x2 and y < y1:
            # NE: вверх и вправо
            self.mouse.move(diagonal_speed, -diagonal_speed)
        elif x < x1 and y < y1:
            # NW: вверх и влево
            self.mouse.move(-diagonal_speed, -diagonal_speed)
        elif x > x2 and y > y2:
            # SE: вниз и вправо
            self.mouse.move(diagonal_speed, diagonal_speed)
        elif x < x1 and y > y2:
            # SW: вниз и влево
            self.mouse.move(-diagonal_speed, diagonal_speed)
        elif y < y1:
            # N: вверх
            self.mouse.move(0, -speed)
        elif y > y2:
            # S: вниз
            self.mouse.move(0, speed)
        elif x > x2:
            # E: вправо
            self.mouse.move(speed, 0)
        elif x < x1:
            # W: влево
            self.mouse.move(-speed, 0)

    def right_click(self):
        self.mouse.click(Button.right)

    def left_click(self):
        self.mouse.click(Button.left)

    def press_left_button(self):
        self.mouse.press(Button.left)

    def release_left_button(self):
        self.mouse.release(Button.left)

    def middle_click(self):
        self.mouse.click(Button.middle)

    def double_click(self):
        self.mouse.click(Button.left, 2)

    def scroll_up(self):
        self.mouse.scroll(0, 3)

    def scroll_down(self):
        self.mouse.scroll(0, -3)

    def step_back(self):
        with self.keyboard.pressed(Key.alt):
            self.keyboard.press(Key.left)
            self.keyboard.release(Key.left)

    def step_forward(self):
        with self.keyboard.pressed(Key.alt):
            self.keyboard.press(Key.right)
            self.keyboard.release(Key.right)

    def custom_action(self):
        pass

    def perform_action(self, action):
        if action == 'not selected':
            return
        if action not in self.action_map:
            raise ValueError(f"Неизвестное действие: {action}")
        self.action_map[action]()