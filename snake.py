import pygame

class Snake:
    def __init__(self, size=20):
        self.size = size
        # Start in a safer position with more space, aligned to grid
        start_x = (600 // 2 // size) * size  # Center of screen, aligned to grid
        start_y = (400 // 2 // size) * size  # Center of screen, aligned to grid
        self.body = [(start_x, start_y), (start_x - size, start_y), (start_x - 2*size, start_y)]
        self.direction = "RIGHT"

    def move(self):
        x, y = self.body[0]
        if self.direction == "UP":
            y -= self.size
        elif self.direction == "DOWN":
            y += self.size
        elif self.direction == "LEFT":
            x -= self.size
        elif self.direction == "RIGHT":
            x += self.size

        self.body.insert(0, (x, y))
        self.body.pop()

    def grow(self):
        self.body.append(self.body[-1])

    def change_direction(self, direction):
        opposite = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
        if direction != opposite[self.direction]:
            self.direction = direction

    def collision_with_self(self):
        return self.body[0] in self.body[1:]