import math
import random
import tkinter as tk

#DEFINIÇOES DE TELA
SCREEN_WIDTH = 20
SCREEN_HEIGHT = 20

SCALE = 20
#cores das bolinhas
COLORS = ['pink', 'purple', 'yellow', 'red', 'blue', 'green']

DIRECTIONS = {
    'Left': -1,
    'Right': 1
}

#pontuação e definiçoes de jogo
class BubbleShooter:

    def __init__(self, canvas, score_label):
        self.canvas = canvas
        self.score_label = score_label
        self.bubbles = self.make_bubbles()
        self.draw_bubbles()
        self.bullet = self.make_bullet()
        self.draw_bullet()
        self.gun = self.make_gun()
        self.draw_gun()
        self.time = 0
        self.score = 0

    def aim(self, event):
        direction = event.keysym
        self.gun[0].x += DIRECTIONS[direction]
        self.canvas.delete('gun')
        self.draw_gun()
#eventos = encosta uma bolinha na outra --- se encostar uma cor semelhante contar como pontos
    def shoot(self, event=None):
        direction_vector = self.gun[0] - self.gun[1]
        direction_vector /= direction_vector.length()
        self.bullet[0], self.bullet[1] = self.gun[1] + self.time * direction_vector

        if (
            not 0 < self.bullet[0] < SCREEN_WIDTH * 20 or
            not 0 < self.bullet[1] < SCREEN_HEIGHT * 20
        ):
            self.new_round()
            return

        self.canvas.delete('bullet')
        self.draw_bullet()
        self.time += 0.2

        if not self.bullet_is_about_to_collide():
            self.canvas.after(10, self.shoot)
        else:
            self.land_bullet()

    def update_score(self):
        self.score_label['text'] = f'PONTOS: {self.score}'
#cores e posições de bolas
    def land_bullet(self):
        y = int(round(self.bullet[1]))
        x = int(round(self.bullet[0])) + (0.5 if y % 2 != 0 else 0)
        wanted_landing_position = self.bubbles[(x, y)]
        if wanted_landing_position['color'] is None:
            self.bubbles[(x, y)]['color'] = self.bullet[2]
        else:
            potential_landing_positions = {
                k: v for k, v in self.bubbles.items() if k in [
                    (x - 0.5, y - 1),
                    (x + 0.5, y - 1),
                    (x - 1, y),
                    (x + 1, y),
                    (x - 0.5, y + 1),
                    (x + 0.5, y + 1)
                ] if v['color'] is None
            }

            distances = [
                abs(
                    Vector(
                        x - coord[0],
                        y - coord[1]
                    ).length()
                )
                for coord in potential_landing_positions.keys()
            ]

            min_distance_index = distances.index(min(distances))

            final_position = list(potential_landing_positions.keys())[min_distance_index]

            self.bullet = [
                final_position[0], final_position[1], self.bullet[2]
            ]

            self.bubbles[(final_position[0], final_position[1])] = {
                'color': self.bullet[2]
            }

        self.explode(x, y)

        self.new_round()

        self.canvas.delete('bubble')
        self.draw_bubbles()

    def explode(self, x, y):
        surroundings = {
            k: v for k, v in self.bubbles.items() if k in [
                (x - 0.5, y - 1),
                (x + 0.5, y - 1),
                (x - 1, y),
                (x + 1, y),
                (x - 0.5, y + 1),
                (x + 0.5, y + 1)
            ]
        }

        surroundings = {
            k: v for k, v in surroundings.items() if v['color'] == self.bullet[2]
        }

        if surroundings:
            self.bubbles[(x, y)]['color'] = None

        for x, y in surroundings.keys():
            self.score += 10
            self.update_score()
            self.bubbles[(x, y)]['color'] = None
            self.explode(x, y)

    def bullet_is_about_to_collide(self):
        bullet_center = (
            self.bullet[0], self.bullet[1]
        )
        return any(
            (Vector(*bubble_center) - Vector(*bullet_center)).length() < 1
            for bubble_center in [
                (x, y) for (x, y), info in self.bubbles.items() if info['color'] is not None
            ]
        )

    def new_round(self):
        self.time = 0
        self.canvas.delete('bullet')
        self.bullet = self.make_bullet()
        self.draw_bullet()

    def make_gun(self):
        return [
            Vector(SCREEN_WIDTH // 2 , 0),
            Vector(SCREEN_WIDTH // 2, SCREEN_HEIGHT)
        ]

    def make_bullet(self):
        return [
            SCREEN_WIDTH // 2 - 0.5, SCREEN_HEIGHT - 1, random.choice(COLORS), True
        ]

    def make_bubbles(self):
        bubbles = {}
        for y in range(SCREEN_HEIGHT):
            for x in range(SCREEN_WIDTH):
                x += 0.5 if y % 2 != 0 else 0
                bubbles[(x, y)] = {
                    'color': random.choice(COLORS) if y < SCREEN_HEIGHT // 4 else None
                }
        return bubbles

    def draw_bubbles(self):
        for (x, y), info in self.bubbles.items():
            if info['color'] is not None:
                self.canvas.create_oval(
                    x * SCALE, y * SCALE,
                    (x + 1) * SCALE, (y + 1) * SCALE,
                    fill=info['color'], tags=['bubble']
                )

    def draw_bullet(self):
        self.canvas.create_oval(
            self.bullet[0] * SCALE, self.bullet[1] * SCALE,
            (self.bullet[0] + 1) * SCALE, (self.bullet[1] + 1) * SCALE,
            fill=self.bullet[2], tags=['bullet']
        )

    def draw_gun(self):
        self.canvas.create_line(
            self.gun[0].x * SCALE, self.gun[0].y * SCALE,
            self.gun[1].x * SCALE, self.gun[1].y * SCALE,
            tags=['gun']
        )

#vetor de encaixe de bola
class Vector:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, vector):
        return Vector(self.x + vector.x, self.y + vector.y)

    def __sub__(self, vector):
        return Vector(self.x - vector.x, self.y - vector.y)

    def __rmul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)

    def length(self):
        return math.hypot(self.x, self.y)

    def __iter__(self):
        yield self.x
        yield self.y

#fundo de tela
def main():
    root = tk.Tk()
    canvas = tk.Canvas(
        root,
        width=SCALE*SCREEN_WIDTH+(0.5*SCALE),
        height=SCALE*SCREEN_HEIGHT,
        background='gray'
    )
    canvas.pack()
    score_label = tk.Label(root, text='PONTOS: 0')
    score_label.pack()

    game = BubbleShooter(canvas, score_label)

    for direction in DIRECTIONS:
        root.bind(f'<{direction}>', game.aim)

    root.bind('<space>', game.shoot)

    root.mainloop()


if __name__ == '__main__':
    main()