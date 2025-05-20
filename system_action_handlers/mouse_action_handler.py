from pynput.mouse import Button, Controller

class MouseActionHandler:
    def __init__(self, mouse_speed_near, mouse_speed_far = None):
        self.mouse = Controller()
        self.mouse_speed_near = mouse_speed_near
        if mouse_speed_far is not None:
            self.mouse_speed_far = mouse_speed_far
        else:
            self.mouse_speed_far = 4 * mouse_speed_near

    def move_mouse(self, center, x1, x2, y1, y2, s1_x, s1_y, s2_x, s2_y):
        x, y = center

        # Определяем скорость
        if s1_x <= x <= s2_x and s1_y <= y <= s2_y:
            speed = self.mouse_speed_near
        else:
            speed = self.mouse_speed_far
        diagonal_speed = speed / 1.414

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