import pygame
import math
import sys
import random
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from random import shuffle, randrange

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 850, 850
FPS = 60
PLAYER_SIZE = 25
ENEMY_SIZE = 50
TROPHY_SIZE = 30
original_maze = [
    "***************************",
    "*                         *",
    "* ************  ***********",
    "*  *                      *",
    "*  * ******************** *",
    "*  *                    * *",
    "*  * ****************** * *",
    "*  *                  * * *",
    "*  * ******** ******* * * *",
    "*  *                * * * *",
    "*  * ************** * * * *",
    "*  *              * * * * *",
    "*  * ************ * *   * *",
    "*  *            * * * * * *",
    "*  *******  ***** *   * * *",
    "*                 * * * * *",
    "******** ******** * * * * *",
    "*               * * * * * *",
    "* ***** ******* * * * *   *",
    "*             * * * * * * *",
    "* *********** * * * * * * *",
    "*         *   * * * * * * *",
    "* *** *** *** * * * * * * *",
    "*         *   * * * * * * *",
    "***************************",
]
MAZE = original_maze

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Get the Cum Laude!")

# Clock to control the frame rate
clock = pygame.time.Clock()

# Game states
MENU = 0
PLAYING = 1
AUTONOMOUS_PLAYING = 2

# Set initial game state
game_state = MENU

# Font for the menu text
font = pygame.font.Font(None, 36)

# Initialize game_over variable
game_over = False

def draw_maze():
    for y, row in enumerate(MAZE):
        for x, cell in enumerate(row):
            if cell == "*":
                pygame.draw.rect(screen, WHITE, (x * 30, y * 30, 30, 30))

def draw_score():
    score_text = f"Score: {level}"
    score_surface = font.render(score_text, True, RED)
    score_rect = score_surface.get_rect(topleft=(8, 8))
    screen.blit(score_surface, score_rect)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("bocconi.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (PLAYER_SIZE, PLAYER_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (30, 30)

class AutonomousPlayer(pygame.sprite.Sprite):
    def __init__(self, maze, player, trophy):
        super().__init__()
        self.maze = maze
        self.player = player
        self.trophy = trophy
        self.image = pygame.image.load("bocconi.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (PLAYER_SIZE, PLAYER_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (30, 30)
        self.path = []

    def calculate_path(self):
        # Determine maze dimensions
        maze_width = len(self.maze[0])
        maze_height = len(self.maze)

        # Create a numeric matrix for pathfinding
        numeric_maze = [[9999 if cell == '*' else 1 for cell in row] for row in self.maze]

        # Create grid and nodes
        grid = Grid(matrix=numeric_maze)
        start = grid.node(self.rect.x // 30, self.rect.y // 30)
        end = grid.node(self.trophy.rect.x // 30, self.trophy.rect.y // 30)

        # Calculate the path using the A* algorithm
        finder = AStarFinder()
        self.path, _ = finder.find_path(start, end, grid)

        if self.path:
            # Remove the current position from the path
            self.path.pop(0)

    def move_towards(self, target_x, target_y):
        speed = 3
        original_position = self.rect.topleft

        dx = target_x * 30 - self.rect.x
        dy = target_y * 30 - self.rect.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance != 0:
            dx = dx / distance * speed
            dy = dy / distance * speed

            self.rect.x += dx
            self.rect.y += dy

        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == "*":
                    wall_rect = pygame.Rect(x * 30, y * 30, 30, 30)
                    if self.rect.colliderect(wall_rect):
                        self.rect.topleft = original_position
                        return False

        return True

    def update(self):
        if not self.path:
            self.calculate_path()
        elif self.path:
            next_node = self.path[0]
            target_x, target_y = next_node
            moved = self.move_towards(target_x, target_y)
            if moved and self.rect.x == target_x * 30 and self.rect.y == target_y * 30:
                self.path.pop(0)
        if not self.path or not self.move_towards(*self.path[0]):
            # If there is no path or it's not moving, find a new path
            self.calculate_path()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = pygame.image.load("cattolica.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (ENEMY_SIZE, ENEMY_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (random.randint(1, len(MAZE[0])-2) * 30, random.randint(1, len(MAZE)-2) * 30)
        self.player = player
        self.speed = 1.5

    def randomize_position(self):
        while True:
            new_position = (random.randint(1, len(MAZE[0])-2) * 30, random.randint(1, len(MAZE)-2) * 30)
            rect = pygame.Rect(new_position, (ENEMY_SIZE, ENEMY_SIZE))
            if not any(rect.colliderect(pygame.Rect(x * 30, y * 30, 30, 30)) for y, row in enumerate(MAZE) for x, cell in enumerate(row) if cell == "*"):
                self.rect.topleft = new_position
                break

    def update(self):
        target = player
        speed = self.speed
        if self.rect.x < target.rect.x:
            self.rect.x += speed
        elif self.rect.x > target.rect.x:
            self.rect.x -= speed
        if self.rect.y < target.rect.y:
            self.rect.y += speed
        elif self.rect.y > target.rect.y:
            self.rect.y -= speed

class Trophy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("cap.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TROPHY_SIZE, TROPHY_SIZE))
        self.rect = self.image.get_rect()
        self.randomize_position()

    def randomize_position(self):
        while True:
            new_position = (random.randint(1, len(MAZE[0])-2) * 30, random.randint(1, len(MAZE)-2) * 30)
            rect = pygame.Rect(new_position, (TROPHY_SIZE, TROPHY_SIZE))
            if not any(rect.colliderect(pygame.Rect(x * 30, y * 30, 30, 30)) for y, row in enumerate(MAZE) for x, cell in enumerate(row) if cell == "*"):
                self.rect.topleft = new_position
                break

def draw_menu():
    screen.fill((0, 0, 0))
    
    # Create and render the text and buttons
    welcome_text = font.render("Welcome to Get the Cum Laude!", True, WHITE)
    welcome_rect = welcome_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    screen.blit(welcome_text, welcome_rect.topleft)

    description_text = font.render("A game where you try to get your graduation cap!", True, WHITE)
    description_rect = description_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(description_text, description_rect.topleft)

    start_button = font.render("Start Game", True, WHITE)
    start_rect = start_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    pygame.draw.rect(screen, GREEN, start_rect, border_radius=10)
    screen.blit(start_button, start_rect.topleft)

    quit_button = font.render("Quit Game", True, WHITE)
    quit_rect = quit_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
    pygame.draw.rect(screen, RED, quit_rect, border_radius=10)
    screen.blit(quit_button, quit_rect.topleft)

    autonomous_button = font.render("Pathfinding Algorithm", True, WHITE)
    autonomous_rect = autonomous_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 250))
    pygame.draw.rect(screen, BLUE, autonomous_rect, border_radius=10)
    screen.blit(autonomous_button, autonomous_rect.topleft)

    return start_rect, quit_rect, autonomous_rect


def draw_return_button():
    return_button_text = font.render("Return to Menu", True, BLUE)
    return_button_rect = return_button_text.get_rect(topleft = (1,1))
    pygame.draw.rect(screen, WHITE, return_button_rect, border_radius=5)
    screen.blit(return_button_text, return_button_rect.topleft)
    return return_button_rect

def draw_playing():
    screen.fill((0, 0, 0))
    draw_maze()
    all_sprites.draw(screen)
    if game_over:
        game_over_text = font.render("Game Over", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    
    if game_state == AUTONOMOUS_PLAYING:
        return_button_rect = draw_return_button()

def make_maze(w = 9, h = 12):
    vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
    ver = [["*  "] * w + ['*'] for _ in range(h)] + [[]]
    hor = [["***"] * w + ['*'] for _ in range(h + 1)]

    def walk(x, y):
        vis[y][x] = 1

        d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
        shuffle(d)
        for (xx, yy) in d:
            if vis[yy][xx]: continue
            if xx == x: hor[max(y, yy)][x] = "*  "
            if yy == y: ver[y][max(x, xx)] = "   "
            walk(xx, yy)

    walk(randrange(w), randrange(h))

    s = ""
    for (a, b) in zip(hor, ver):
        s += ''.join(a + ['\n'] + b + ['\n'])
    s = s.splitlines()

    s = [i[:-2]for i in s]
    s = [i + '*' for i in s]
    s = s[:-1]
    return s

def manhattan(node, end):
    x1, y1 = divmod(node, 27)
    x2, y2 = divmod(end, 27)
    return abs(x1 - x2) + abs(y1 - y2)




# Create sprites
player = Player()
enemy = Enemy(player)
trophy = Trophy()
all_sprites = pygame.sprite.Group(player, enemy, trophy)
autonomous_player = AutonomousPlayer(MAZE, player, trophy)

# Game loop
running = True
level = 1
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == MENU:
                start_rect, quit_rect, autonomous_rect = draw_menu()
                if start_rect.collidepoint(event.pos):
                    all_sprites.empty()
                    all_sprites.add(player)
                    all_sprites.add(enemy)
                    all_sprites.add(trophy)
                    MAZE = original_maze
                    game_state = PLAYING
                    game_over = False
                    player.rect.topleft = (30, 30)
                    trophy.randomize_position()
                    enemy.randomize_position()
                    enemy.speed = 1.5
                    level = 1
                elif quit_rect.collidepoint(event.pos):
                    running = False
                elif autonomous_rect.collidepoint(event.pos):
                    game_state = AUTONOMOUS_PLAYING
                    all_sprites.empty()
                    all_sprites.add(autonomous_player)
                    all_sprites.add(trophy)
                    level = 1
                    trophy.randomize_position()
                    autonomous_player.maze = MAZE
                    autonomous_player.calculate_path
                    autonomous_player.update
                    game_over =  False
            elif game_state == AUTONOMOUS_PLAYING:
                return_button_rect = draw_return_button()
                if return_button_rect.collidepoint(event.pos):
                    game_state = MENU
                    all_sprites.empty()
                    level = 1

    keys = pygame.key.get_pressed()
    player_speed = 5
    current_position = player.rect.topleft

    if game_state == PLAYING:
        if keys[pygame.K_LEFT]:
            player.rect.x -= player_speed
            for y, row in enumerate(MAZE):
                for x, cell in enumerate(row):
                    if cell == "*":
                        wall_rect = pygame.Rect(x * 30, y * 30, 30, 30)
                        if player.rect.colliderect(wall_rect):
                            player.rect.topleft = current_position

        if keys[pygame.K_RIGHT]:
            player.rect.x += player_speed
            for y, row in enumerate(MAZE):
                for x, cell in enumerate(row):
                    if cell == "*":
                        wall_rect = pygame.Rect(x * 30, y * 30, 30, 30)
                        if player.rect.colliderect(wall_rect):
                            player.rect.topleft = current_position

        if keys[pygame.K_UP]:
            player.rect.y -= player_speed
            for y, row in enumerate(MAZE):
                for x, cell in enumerate(row):
                    if cell == "*":
                        wall_rect = pygame.Rect(x * 30, y * 30, 30, 30)
                        if player.rect.colliderect(wall_rect):
                            player.rect.topleft = current_position

        if keys[pygame.K_DOWN]:
            player.rect.y += player_speed
            for y, row in enumerate(MAZE):
                for x, cell in enumerate(row):
                    if cell == "*":
                        wall_rect = pygame.Rect(x * 30, y * 30, 30, 30)
                        if player.rect.colliderect(wall_rect):
                            player.rect.topleft = current_position

    if pygame.sprite.collide_rect(player, trophy):
        print(f"Level {level} passed!")
        level += 1
        enemy.speed += 0.1
        player.rect.topleft = (30, 30)
        trophy.randomize_position()
    
    if pygame.sprite.collide_rect(autonomous_player, trophy):
        print(f"Level {level} passed!")
        level += 1
        autonomous_player.rect.topleft = (30, 30)
        MAZE = make_maze()
        autonomous_player.maze = MAZE
        autonomous_player.calculate_path()
        trophy.randomize_position()

    enemy.update()
    if pygame.sprite.collide_rect(player, enemy) and game_state == PLAYING:
        game_over = True

    screen.fill((0, 0, 0))
    if game_state == PLAYING:
        draw_playing()
        draw_score()
    elif game_state == MENU:
        intro_text = font.render("Welcome to Get the Cum Laude! A game where you try your best ti outrun Catollica and get your well deserved graduation cap!", True, WHITE)
        screen.blit(intro_text,(WIDTH // 2 - 250, HEIGHT//2 + 250))
        draw_menu()
    elif game_state == AUTONOMOUS_PLAYING:
        autonomous_player.update()
        draw_playing()  

    if game_over:
        game_over_text = font.render(f"Game Over. You have reached a score of: {level}", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - 250, HEIGHT // 2 - 150))
        game_state = MENU

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
