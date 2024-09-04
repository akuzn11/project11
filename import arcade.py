import arcade
import random
import math


SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_TITLE = "dots"


NUM_RED_POINTS = 15
NUM_BLUE_POINTS = 15
NUM_GREEN_POINTS = 15


RADIUS = 4
MIN_DISTANCE = 5 * RADIUS
CLICK_RADIUS = 100


CENTER_ATTRACTION_RED = 1
CENTER_ATTRACTION_BLUE = 1
CENTER_ATTRACTION_GREEN = 1


RED_ATTRACTION = 0.1
BLUE_ATTRACTION = 0.1
GREEN_ATTRACTION = 0.01

RED_REPULSION = 0.005
BLUE_REPULSION = 0.02
GREEN_REPULSION = 0.02


RED_BLUE_ATTRACTION = 0.5
BLUE_GREEN_ATTRACTION = 0.5
RED_GREEN_ATTRACTION = 0.0


RED_BLUE_REPULSION = 0.0
BLUE_GREEN_REPULSION = 0.1
RED_GREEN_REPULSION = 0.1



FRICTION = 0.95
SEPARATION_FORCE = 0.3
IMPULSE_MAGNITUDE = 10
BORDER_DISTANCE = 50
REPULSION_STRENGTH = 0.1

# Центр экрана
CENTER_X = SCREEN_WIDTH / 2
CENTER_Y = SCREEN_HEIGHT / 2

class Point:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = 0
        self.vy = 0

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        self.red_points = [Point(CENTER_X + random.uniform(-20, 20), CENTER_Y + random.uniform(-20, 20), arcade.color.RED) for _ in range(NUM_RED_POINTS)]
        self.blue_points = [Point(CENTER_X + random.uniform(-100, 100), CENTER_Y + random.uniform(-100, 100), arcade.color.BLUE) for _ in range(NUM_BLUE_POINTS)]
        self.green_points = [Point(CENTER_X + random.uniform(-200, 200), CENTER_Y + random.uniform(-200, 200), arcade.color.GREEN) for _ in range(NUM_GREEN_POINTS)]

    def on_draw(self):
        arcade.start_render()
        for point in self.red_points + self.blue_points + self.green_points:
            arcade.draw_circle_filled(point.x, point.y, RADIUS, point.color)

    def update(self, delta_time):
        # Притяжение и отталкивание между точками одного цвета
        self.calculate_forces(self.red_points, self.red_points, RED_ATTRACTION, RED_REPULSION)
        self.calculate_forces(self.blue_points, self.blue_points, BLUE_ATTRACTION, BLUE_REPULSION)
        self.calculate_forces(self.green_points, self.green_points, GREEN_ATTRACTION, GREEN_REPULSION)

        # Притяжение и отталкивание между разными цветами
        self.calculate_forces(self.red_points, self.blue_points, RED_BLUE_ATTRACTION, RED_BLUE_REPULSION)
        self.calculate_forces(self.blue_points, self.green_points, BLUE_GREEN_ATTRACTION, BLUE_GREEN_REPULSION)
        self.calculate_forces(self.red_points, self.green_points, RED_GREEN_ATTRACTION, RED_GREEN_REPULSION)  # Новая строка

        # Притяжение всех точек к центру экрана
        self.apply_center_attraction(self.red_points, CENTER_ATTRACTION_RED)
        self.apply_center_attraction(self.blue_points, CENTER_ATTRACTION_BLUE)
        self.apply_center_attraction(self.green_points, CENTER_ATTRACTION_GREEN)

        # Применение отталкивания от границ экрана
        self.apply_border_repulsion(self.red_points + self.blue_points + self.green_points, BORDER_DISTANCE, REPULSION_STRENGTH)

        for point in self.red_points + self.blue_points + self.green_points:
            point.vx *= FRICTION
            point.vy *= FRICTION
            point.x += point.vx
            point.y += point.vy

            if point.x < RADIUS:
                point.x = RADIUS
                point.vx = -point.vx
            elif point.x > SCREEN_WIDTH - RADIUS:
                point.x = SCREEN_WIDTH - RADIUS
                point.vx = -point.vx

            if point.y < RADIUS:
                point.y = RADIUS
                point.vy = -point.vy
            elif point.y > SCREEN_HEIGHT - RADIUS:
                point.y = SCREEN_HEIGHT - RADIUS
                point.vy = -point.vy

    def calculate_forces(self, points1, points2, attraction, repulsion):
        for i in range(len(points1)):
            fx, fy = 0, 0
            for j in range(len(points2)):
                if i == j and points1 is points2:
                    continue
                dx = points2[j].x - points1[i].x
                dy = points2[j].y - points1[i].y
                distance = math.hypot(dx, dy)
                if distance == 0:
                    continue
                if distance < MIN_DISTANCE:
                    fx -= SEPARATION_FORCE * dx / distance
                    fy -= SEPARATION_FORCE * dy / distance
                else:
                    if points1 is points2:
                        force = attraction / distance
                        fx += force * dx / distance
                        fy += force * dy / distance
                    else:
                        fx -= repulsion * dx / distance
                        fy -= repulsion * dy / distance
            points1[i].vx += fx
            points1[i].vy += fy

    def apply_center_attraction(self, points, attraction):
        for point in points:
            dx = CENTER_X - point.x
            dy = CENTER_Y - point.y
            distance = math.hypot(dx, dy)
            if distance == 0:
                continue
            force = attraction
            fx = force * dx / distance
            fy = force * dy / distance
            point.vx += fx
            point.vy += fy

    def apply_impulse(self, pos, magnitude):
        for point in self.red_points + self.blue_points + self.green_points:
            dx = point.x - pos[0]
            dy = point.y - pos[1]
            distance = math.hypot(dx, dy)
            if distance == 0 or distance > CLICK_RADIUS:
                continue
            point.vx += magnitude * dx / distance
            point.vy += magnitude * dy / distance

    def apply_border_repulsion(self, points, border_distance, repulsion_strength):
        for point in points:
            left_dist = point.x - RADIUS
            right_dist = SCREEN_WIDTH - point.x - RADIUS
            top_dist = point.y - RADIUS
            bottom_dist = SCREEN_HEIGHT - point.y - RADIUS

            if left_dist < border_distance:
                point.vx += repulsion_strength * (border_distance - left_dist)
            if right_dist < border_distance:
                point.vx -= repulsion_strength * (border_distance - right_dist)
            if top_dist < border_distance:
                point.vy += repulsion_strength * (border_distance - top_dist)
            if bottom_dist < border_distance:
                point.vy -= repulsion_strength * (border_distance - bottom_dist)

    def on_mouse_press(self, x, y, button, modifiers):
        self.apply_impulse((x, y), IMPULSE_MAGNITUDE)

def main():
    game = MyGame()
    arcade.run()

if __name__ == "__main__":
    main()
