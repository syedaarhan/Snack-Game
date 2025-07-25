import pygame
import random
import time
import json
import os
import math

# Initialize pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 80, 80)
GREEN = (100, 255, 100)
DARK_GREEN = (50, 180, 50)
BACKGROUND = (30, 30, 45)  # Dark blue-gray background
GRID_COLOR = (40, 40, 60)
ACCENT = (100, 150, 255)  # Blue accent color

# Game settings
WIDTH, HEIGHT = 720, 480  # Larger window
GRID_SIZE = 24
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
SNAKE_SPEED = 8
SAFE_MARGIN = 3  # Blocks from edge where food won't spawn

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game - Premium Edition')
clock = pygame.time.Clock()

# Load fonts
try:
    title_font = pygame.font.Font(None, 72)
    large_font = pygame.font.Font(None, 48)
    medium_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
except:
    # Fallback to system fonts if custom font fails
    title_font = pygame.font.SysFont('arial', 72, bold=True)
    large_font = pygame.font.SysFont('arial', 48)
    medium_font = pygame.font.SysFont('arial', 36)
    small_font = pygame.font.SysFont('arial', 24)

# High score file
HIGH_SCORE_FILE = "snake_highscore.json"

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, 'r') as f:
            try:
                data = json.load(f)
                return data.get('high_score', 0)
            except:
                return 0
    return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, 'w') as f:
        json.dump({'high_score': score}, f)

def draw_rounded_rect(surface, color, rect, radius=5):
    """Draw rectangle with rounded corners"""
    x, y, width, height = rect
    pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
    pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)

def get_valid_food_position(snake_body):
    """Get food position that's not near edges or on snake"""
    while True:
        food_pos = [
            random.randint(SAFE_MARGIN, GRID_WIDTH - 1 - SAFE_MARGIN),
            random.randint(SAFE_MARGIN, GRID_HEIGHT - 1 - SAFE_MARGIN)
        ]
        if food_pos not in snake_body:
            return food_pos

def draw_grid():
    """Draw subtle grid lines"""
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y), 1)

def draw_snake_segment(pos, is_head=False):
    """Draw a single snake segment with nice styling"""
    x, y = pos[0] * GRID_SIZE, pos[1] * GRID_SIZE
    size = GRID_SIZE
    
    # Draw segment base
    color = DARK_GREEN if is_head else GREEN
    draw_rounded_rect(screen, color, (x, y, size, size), radius=4)
    
    # Add highlights for 3D effect
    if is_head:
        # Eyes for the head
        eye_size = size // 5
        pygame.draw.circle(screen, WHITE, (x + size//3, y + size//3), eye_size)
        pygame.draw.circle(screen, WHITE, (x + 2*size//3, y + size//3), eye_size)
        pygame.draw.circle(screen, BLACK, (x + size//3, y + size//3), eye_size//2)
        pygame.draw.circle(screen, BLACK, (x + 2*size//3, y + size//3), eye_size//2)
    else:
        # Subtle highlight for body segments
        highlight = (min(color[0]+40, 255), min(color[1]+40, 255), min(color[2]+40, 255))
        pygame.draw.rect(screen, highlight, (x+2, y+2, size//2, size//4), 0, 2)

def draw_food(pos):
    """Draw the food with nice styling"""
    x, y = pos[0] * GRID_SIZE, pos[1] * GRID_SIZE
    size = GRID_SIZE
    
    # Main apple shape
    pygame.draw.circle(screen, RED, (x + size//2, y + size//2), size//2 - 2)
    
    # Apple highlight
    highlight = (min(RED[0]+50, 255), min(RED[1]+50, 255), min(RED[2]+50, 255))
    pygame.draw.circle(screen, highlight, (x + size//3, y + size//3), size//5)
    
    # Apple stem
    pygame.draw.rect(screen, (100, 70, 30), (x + size//2 - 1, y - size//6, 2, size//4))
    
    # Apple leaf
    leaf_points = [
        (x + size//2 + 2, y - size//6),
        (x + size//2 + size//3, y - size//4),
        (x + size//2 + size//6, y - size//6)
    ]
    pygame.draw.polygon(screen, (100, 200, 100), leaf_points)

def show_pause_screen():
    """Show a beautiful pause screen"""
    # Dark overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Pause text
    pause_text = large_font.render("GAME PAUSED", True, ACCENT)
    instruction = medium_font.render("Press SPACE to continue", True, WHITE)
    
    screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT//2 + 20))
    
    pygame.display.update()

def draw_score_panel(score, high_score):
    """Draw the score panel with modern design"""
    # Panel background
    panel_height = 60
    pygame.draw.rect(screen, (20, 20, 35), (0, 0, WIDTH, panel_height))
    
    # Score display
    score_text = medium_font.render(f"SCORE: {score}", True, WHITE)
    high_score_text = medium_font.render(f"HIGH SCORE: {high_score}", True, ACCENT)
    
    screen.blit(score_text, (20, panel_height//2 - score_text.get_height()//2))
    screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 20, 
                                panel_height//2 - high_score_text.get_height()//2))
    
    # Controls hint
    controls_text = small_font.render("ARROWS: Move | SPACE: Pause", True, (200, 200, 200))
    screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, 
                              panel_height//2 - controls_text.get_height()//2))

def show_game_over_screen(score, high_score):
    """Show a polished game over screen"""
    # Dark overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Game over text
    game_over_text = title_font.render("GAME OVER", True, ACCENT)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 120))
    
    # Score display
    score_text = large_font.render(f"Your Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 40))
    
    # High score display (if applicable)
    if score == high_score and score > 0:
        new_record_text = medium_font.render("NEW HIGH SCORE!", True, (255, 215, 0))  # Gold color
        screen.blit(new_record_text, (WIDTH//2 - new_record_text.get_width()//2, HEIGHT//2 + 10))
    else:
        high_score_text = medium_font.render(f"High Score: {high_score}", True, WHITE)
        screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 10))
    
    # Restart/quit options
    restart_text = medium_font.render("Press R to Restart", True, GREEN)
    quit_text = medium_font.render("Press Q to Quit", True, RED)
    
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 80))
    screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 130))
    
    pygame.display.update()

def game_loop():
    # Initial snake position and body
    snake_pos = [[GRID_WIDTH // 2, GRID_HEIGHT // 2]]
    snake_body = [[GRID_WIDTH // 2, GRID_HEIGHT // 2]]
    
    # Initial food position (not near edges)
    food_pos = get_valid_food_position(snake_body)
    food_spawn = True
    
    # Initial direction (right)
    direction = 'RIGHT'
    change_to = direction
    
    # Initial score
    score = 0
    high_score = load_high_score()
    
    # Game states
    game_over = False
    paused = False
    
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            # Key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    change_to = 'UP'
                if event.key == pygame.K_DOWN:
                    change_to = 'DOWN'
                if event.key == pygame.K_LEFT:
                    change_to = 'LEFT'
                if event.key == pygame.K_RIGHT:
                    change_to = 'RIGHT'
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_ESCAPE and (game_over or paused):
                    return  # Exit to menu
        
        if paused:
            show_pause_screen()
            continue
        
        # Validate direction (no opposite movement)
        if change_to == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'
        
        # Move the snake
        if direction == 'UP':
            snake_pos[0][1] -= 1
        if direction == 'DOWN':
            snake_pos[0][1] += 1
        if direction == 'LEFT':
            snake_pos[0][0] -= 1
        if direction == 'RIGHT':
            snake_pos[0][0] += 1
        
        # Snake body mechanism
        snake_body.insert(0, list(snake_pos[0]))
        if snake_pos[0] == food_pos:
            score += 1
            food_spawn = False
        else:
            snake_body.pop()
        
        # Spawn new food (not near edges)
        if not food_spawn:
            food_pos = get_valid_food_position(snake_body)
            food_spawn = True
        
        # Clear screen with new background color
        screen.fill(BACKGROUND)
        draw_grid()
        
        # Draw food first (so snake can appear over it)
        draw_food(food_pos)
        
        # Draw snake
        for i, pos in enumerate(snake_body):
            draw_snake_segment(pos, i == 0)  # First segment is head
        
        # Draw score panel
        draw_score_panel(score, high_score)
        
        # Game over conditions
        # Hit the wall
        if (snake_pos[0][0] < 0 or snake_pos[0][0] >= GRID_WIDTH or
            snake_pos[0][1] < 0 or snake_pos[0][1] >= GRID_HEIGHT):
            game_over = True
        
        # Hit itself
        for block in snake_body[1:]:
            if snake_pos[0] == block:
                game_over = True
        
        pygame.display.update()
        clock.tick(SNAKE_SPEED)
    
    # Update high score if needed
    if score > high_score:
        high_score = score
        save_high_score(high_score)
    
    # Show game over screen
    show_game_over_screen(score, high_score)
    
    # Wait for player input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    game_loop()  # Restart game
                if event.key == pygame.K_q:
                    pygame.quit()
                    return

# Start screen
def show_start_screen():
    screen.fill(BACKGROUND)
    
    # Title
    title_text = title_font.render("SNAKE GAME", True, ACCENT)
    subtitle_text = medium_font.render("Premium Edition", True, WHITE)
    
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))
    screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, HEIGHT//4 + 80))
    
    # Snake graphic
    demo_snake = [
        [GRID_WIDTH//2 - 2, GRID_HEIGHT//2],
        [GRID_WIDTH//2 - 1, GRID_HEIGHT//2],
        [GRID_WIDTH//2, GRID_HEIGHT//2],
        [GRID_WIDTH//2 + 1, GRID_HEIGHT//2],
    ]
    for i, pos in enumerate(demo_snake):
        draw_snake_segment([pos[0], pos[1]], i == len(demo_snake)-1)
    
    # Food graphic
    draw_food([GRID_WIDTH//2 + 3, GRID_HEIGHT//2])
    
    # Start instructions
    start_text = large_font.render("Press ANY KEY to Start", True, WHITE)
    controls_text = medium_font.render("Use Arrow Keys to Move", True, (200, 200, 200))
    pause_text = medium_font.render("SPACE to Pause", True, (200, 200, 200))
    
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT*3//4))
    screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT*3//4 + 60))
    screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT*3//4 + 100))
    
    pygame.display.update()
    
    # Wait for key press
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                waiting = False
                game_loop()

# Start the game
show_start_screen()