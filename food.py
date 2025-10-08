import pygame, random

class Food:
    def __init__(self, width, height, size, max_food=3):
        self.width = width
        self.height = height
        self.size = size
        self.max_food = max_food
        self.positions = []
        # Initialize food positions
        for _ in range(max_food):
            self.positions.append(self.spawn())

    def spawn(self, snake_body=None):
        """Spawn food at random position, avoiding snake if provided"""
        if snake_body is None:
            snake_body = []
            
        attempts = 0
        while attempts < 100:  # Prevent infinite loop
            # Make sure the food position aligns with the grid
            x = random.randrange(0, self.width, self.size)
            y = random.randrange(0, self.height, self.size)
            new_pos = (x, y)
            
            if new_pos not in snake_body and new_pos not in self.positions:
                return new_pos
            attempts += 1
        
        # Fallback: just return any position that aligns with the grid
        x = random.randrange(0, self.width, self.size)
        y = random.randrange(0, self.height, self.size)
        return (x, y)

    def draw(self, screen):
        for position in self.positions:
            pygame.draw.rect(screen, (255, 0, 0), (*position, self.size, self.size))
            # Draw outline for better visibility
            pygame.draw.rect(screen, (150, 0, 0), (*position, self.size, self.size), 1)

    def respawn(self, snake_body, index):
        """Respawn a specific food item, avoiding snake and other food"""
        new_pos = self.spawn(snake_body)
        if index < len(self.positions):
            self.positions[index] = new_pos
        else:
            self.positions.append(new_pos)