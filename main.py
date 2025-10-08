import pygame, random, numpy as np
from snake import Snake
from food import Food
import sys

pygame.init()

# Get user input for grid dimensions and food count
print("Snake Game Configuration")

# Try to get grid dimension from command line argument first
if len(sys.argv) > 1:
    try:
        GRID_DIMENSION = int(sys.argv[1])
        print(f"Using grid dimension from command line: {GRID_DIMENSION}")
    except ValueError:
        print("Invalid command line argument. Using default grid dimension of 20.")
        GRID_DIMENSION = 20
else:
    try:
        grid_input = input("Enter grid dimensions (e.g., 10 for 10x10 grid, default is 20 for 20x20): ").strip()
        GRID_DIMENSION = int(grid_input) if grid_input else 20
    except (ValueError, EOFError):
        print("Invalid input or no input. Using default grid dimension of 20.")
        GRID_DIMENSION = 20

# Try to get food count from command line argument second
if len(sys.argv) > 2:
    try:
        FOOD_COUNT = int(sys.argv[2])
        print(f"Using food count from command line: {FOOD_COUNT}")
    except ValueError:
        print("Invalid command line argument. Using default food count of 3.")
        FOOD_COUNT = 3
else:
    try:
        food_count_input = input("Enter number of food items (default is 3): ").strip()
        FOOD_COUNT = int(food_count_input) if food_count_input else 3
    except (ValueError, EOFError):
        print("Invalid input or no input. Using default food count of 3.")
        FOOD_COUNT = 3

# Calculate grid size based on window dimensions and grid count
WIDTH, HEIGHT = 600, 400
GRID_SIZE = min(WIDTH // GRID_DIMENSION, HEIGHT // GRID_DIMENSION)

# Ensure minimum grid size of 10 pixels
GRID_SIZE = max(GRID_SIZE, 10)

print(f"Grid size set to {GRID_DIMENSION}x{GRID_DIMENSION} with cell size {GRID_SIZE}px")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Snake AI Auto Move - Multiple Food")

snake = Snake(GRID_SIZE)
food = Food(WIDTH, HEIGHT, GRID_SIZE, max_food=FOOD_COUNT)

score = 0
running = True
font = pygame.font.Font(None, 36)

def is_safe_move(direction, snake_body, grid_size, width, height):
    """Check if moving in a direction is safe (won't cause collision)"""
    head_x, head_y = snake_body[0]
    
    # Calculate new head position
    if direction == "UP":
        new_head = (head_x, head_y - grid_size)
    elif direction == "DOWN":
        new_head = (head_x, head_y + grid_size)
    elif direction == "LEFT":
        new_head = (head_x - grid_size, head_y)
    elif direction == "RIGHT":
        new_head = (head_x + grid_size, head_y)
    
    # Check boundaries
    if (new_head[0] < 0 or new_head[0] >= width or 
        new_head[1] < 0 or new_head[1] >= height):
        return False
    
    # Check self-collision (skip the tail since it will move)
    if new_head in snake_body[:-1]:
        return False
    
    return True

def count_available_space(start_pos, snake_body, grid_size, width, height, max_depth=15):
    """BFS to count available space from a position - helps avoid traps"""
    visited = set()
    queue = [start_pos]
    visited.add(start_pos)
    count = 0
    
    while queue and count < max_depth:
        current = queue.pop(0)
        count += 1
        x, y = current
        
        # Check all 4 directions
        for dx, dy in [(0, -grid_size), (0, grid_size), (-grid_size, 0), (grid_size, 0)]:
            new_pos = (x + dx, y + dy)
            
            # Check if valid and not visited
            if (new_pos not in visited and
                0 <= new_pos[0] < width and 
                0 <= new_pos[1] < height and
                new_pos not in snake_body[:-1]):  # Exclude tail as it will move
                visited.add(new_pos)
                queue.append(new_pos)
    
    return count

def get_new_head_position(direction, head_x, head_y, grid_size):
    """Calculate new head position based on direction"""
    if direction == "UP":
        return (head_x, head_y - grid_size)
    elif direction == "DOWN":
        return (head_x, head_y + grid_size)
    elif direction == "LEFT":
        return (head_x - grid_size, head_y)
    elif direction == "RIGHT":
        return (head_x + grid_size, head_y)
    return (head_x, head_y)

def ai_move():
    """Improved AI with space-awareness to avoid getting trapped"""
    head_x, head_y = snake.body[0]
    
    # Find closest food
    closest_food = None
    min_distance = float('inf')
    
    for food_pos in food.positions:
        food_x, food_y = food_pos
        distance = abs(head_x - food_x) + abs(head_y - food_y)  # Manhattan distance
        if distance < min_distance:
            min_distance = distance
            closest_food = food_pos
    
    if closest_food:
        food_x, food_y = closest_food
        
        # Build list of all possible moves with their space scores
        move_options = []
        all_directions = ["UP", "DOWN", "LEFT", "RIGHT"]
        
        for direction in all_directions:
            if is_safe_move(direction, snake.body, snake.size, WIDTH, HEIGHT):
                # Calculate how much space is available after this move
                new_head = get_new_head_position(direction, head_x, head_y, snake.size)
                space_available = count_available_space(new_head, snake.body, snake.size, WIDTH, HEIGHT)
                
                # Calculate distance to food after this move
                distance_to_food = abs(new_head[0] - food_x) + abs(new_head[1] - food_y)
                
                # Is this direction towards food?
                towards_food = False
                if (direction == "RIGHT" and head_x < food_x) or \
                   (direction == "LEFT" and head_x > food_x) or \
                   (direction == "DOWN" and head_y < food_y) or \
                   (direction == "UP" and head_y > food_y):
                    towards_food = True
                
                move_options.append({
                    'direction': direction,
                    'space': space_available,
                    'distance': distance_to_food,
                    'towards_food': towards_food
                })
        
        if move_options:
            # Sort by: 1) Space available (most important), 2) Towards food, 3) Shorter distance
            # Prioritize moves with more space to avoid getting trapped
            move_options.sort(key=lambda m: (-m['space'], not m['towards_food'], m['distance']))
            
            best_move = move_options[0]
            snake.change_direction(best_move['direction'])
            return
    
    # Fallback: if no food or no good move found, just pick the safest direction
    all_directions = ["UP", "DOWN", "LEFT", "RIGHT"]
    best_space = -1
    best_direction = None
    
    for direction in all_directions:
        if is_safe_move(direction, snake.body, snake.size, WIDTH, HEIGHT):
            new_head = get_new_head_position(direction, head_x, head_y, snake.size)
            space = count_available_space(new_head, snake.body, snake.size, WIDTH, HEIGHT)
            if space > best_space:
                best_space = space
                best_direction = direction
    
    if best_direction:
        snake.change_direction(best_direction)

def draw_score():
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    
    food_count = font.render(f"Food: {len(food.positions)}", True, (255, 255, 255))
    screen.blit(food_count, (WIDTH - 120, 10))

# Food positions are initialized in the Food class constructor

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Allow manual control for debugging
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.change_direction("UP")
            elif event.key == pygame.K_DOWN:
                snake.change_direction("DOWN")
            elif event.key == pygame.K_LEFT:
                snake.change_direction("LEFT")
            elif event.key == pygame.K_RIGHT:
                snake.change_direction("RIGHT")

    ai_move()  # 🧠 automatic movement

    snake.move()

    # Check food collisions with all food items
    for i, food_pos in enumerate(food.positions[:]):
        if snake.body[0] == food_pos:
            snake.grow()
            score += 1
            food.respawn(snake.body, i)

    # Check boundaries and self-collision
    head_x, head_y = snake.body[0]
    if (head_x < 0 or head_x >= WIDTH or 
        head_y < 0 or head_y >= HEIGHT or 
        snake.collision_with_self()):
        print(f"Game Over! Final Score: {score}")
        running = False

    # Drawing
    screen.fill((30, 30, 30))
    
    # Draw grid for better visibility
    for x in range(0, WIDTH, snake.size):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, snake.size):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (WIDTH, y))
    
    # Draw snake
    for i, block in enumerate(snake.body):
        color = (0, 255, 0) if i == 0 else (0, 200, 0)  # Head is brighter
        pygame.draw.rect(screen, color, (*block, snake.size, snake.size))
        # Draw outline for better visibility
        pygame.draw.rect(screen, (0, 100, 0), (*block, snake.size, snake.size), 1)
    
    # Draw food
    food.draw(screen)
    draw_score()

    pygame.display.flip()
    clock.tick(10)  # speed

pygame.quit()