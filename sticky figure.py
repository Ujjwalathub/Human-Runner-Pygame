# Enhanced Sticky Runner - Realistic Human Character
# Make sure to install pygame: pip install pygame

import pygame
import sys
import random
import math

# --- Initialization ---
pygame.init()

# --- Screen Setup ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Enhanced Sticky Runner - Human Character")

# --- Enhanced Colors ---
SKY_BLUE = (135, 206, 235)
SKY_LIGHT = (200, 230, 255)
GRASS_GREEN = (34, 139, 34)
GRASS_DARK = (20, 100, 20)
DIRT_BROWN = (139, 69, 19)
DIRT_LIGHT = (160, 90, 40)

# Human character colors
SKIN_TONE = (255, 219, 172)
SKIN_SHADOW = (220, 180, 140)
HAIR_COLOR = (101, 67, 33)
SHIRT_COLOR = (0, 100, 200)
SHIRT_SHADOW = (0, 70, 150)
PANTS_COLOR = (50, 50, 50)
PANTS_SHADOW = (30, 30, 30)
SHOE_COLOR = (20, 20, 20)

OBSTACLE_GRAY = (105, 105, 105)
ROCK_COLOR = (70, 70, 70)
TREE_GREEN = (0, 100, 0)
TREE_BROWN = (101, 67, 33)
CLOUD_WHITE = (255, 255, 255)
CLOUD_GRAY = (240, 240, 240)
SUN_YELLOW = (255, 255, 0)
SUN_ORANGE = (255, 200, 0)
DIG_BROWN = (101, 67, 33)
CRYSTAL_PURPLE = (147, 0, 211)
CRYSTAL_LIGHT = (200, 100, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# --- Player Properties ---
player_x = 80
player_y = 0
player_normal_height = 85
player_crouch_height = 45
player_width = 35
player_height = player_normal_height
player_velocity_y = 0
gravity = 0.6
jump_strength = -16
is_jumping = False
is_crouching = False
is_digging = False

# --- Game Properties ---
initial_speed = 5
current_speed = initial_speed
ground_level = 580
obstacles = []
background_objects = []
clouds = []
particles = []

# --- Game State ---
game_started = False
game_over = False
score = 0
font = pygame.font.Font(None, 84)
small_font = pygame.font.Font(None, 42)
tiny_font = pygame.font.Font(None, 28)

# --- Enhanced Obstacle Pattern ---
obstacle_pattern = ['up', 'down', 'dig', 'up', 'down', 'dig', 'up', 'dig', 'down', 'up']
pattern_index = 0

# --- Particle System ---
class Particle:
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0, life=60):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.life = life
        self.max_life = life
    
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.1
        self.life -= 1
        return self.life > 0
    
    def draw(self, surface):
        if self.life > 0:
            size = max(1, int(3 * (self.life / self.max_life)))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)

def add_particle_effect(x, y, color, count=5):
    """Add particle effects for visual flair"""
    for _ in range(count):
        vel_x = random.uniform(-2, 2)
        vel_y = random.uniform(-3, -1)
        particles.append(Particle(x, y, color, vel_x, vel_y, random.randint(30, 60)))

# --- Background Functions ---
def create_background():
    """Creates background elements"""
    global clouds, background_objects
    
    clouds.clear()
    background_objects.clear()
    
    # Create clouds
    for _ in range(8):
        cloud_x = random.randint(-100, SCREEN_WIDTH * 2)
        cloud_y = random.randint(50, 200)
        cloud_size = random.randint(40, 80)
        cloud_speed = random.uniform(0.1, 0.3)
        clouds.append({
            'x': cloud_x, 'y': cloud_y, 'size': cloud_size, 'speed': cloud_speed
        })
    
    # Create background trees
    for _ in range(15):
        tree_x = random.randint(-200, SCREEN_WIDTH * 3)
        tree_height = random.randint(80, 150)
        background_objects.append({
            'type': 'tree', 'x': tree_x, 'height': tree_height
        })

def draw_background():
    """Draws the complete background"""
    # Sky gradient
    for y in range(ground_level):
        ratio = y / ground_level
        r = int(SKY_BLUE[0] + (SKY_LIGHT[0] - SKY_BLUE[0]) * ratio * 0.5)
        g = int(SKY_BLUE[1] + (SKY_LIGHT[1] - SKY_BLUE[1]) * ratio * 0.5)
        b = int(SKY_BLUE[2] + (SKY_LIGHT[2] - SKY_BLUE[2]) * ratio * 0.3)
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    # Sun
    sun_x, sun_y = SCREEN_WIDTH - 100, 80
    pygame.draw.circle(screen, SUN_YELLOW, (sun_x, sun_y), 40)
    pygame.draw.circle(screen, SUN_ORANGE, (sun_x, sun_y), 30)
    
    # Clouds
    for cloud in clouds:
        pygame.draw.circle(screen, CLOUD_WHITE, (int(cloud['x']), int(cloud['y'])), cloud['size']//2)
        pygame.draw.circle(screen, CLOUD_WHITE, (int(cloud['x'] + cloud['size']//3), int(cloud['y'])), cloud['size']//2)
        pygame.draw.circle(screen, CLOUD_WHITE, (int(cloud['x'] - cloud['size']//3), int(cloud['y'])), cloud['size']//2)
        
        cloud['x'] -= cloud['speed']
        if cloud['x'] < -100:
            cloud['x'] = SCREEN_WIDTH + 50
    
    # Ground
    pygame.draw.rect(screen, GRASS_GREEN, (0, ground_level, SCREEN_WIDTH, 20))
    pygame.draw.rect(screen, DIRT_BROWN, (0, ground_level + 20, SCREEN_WIDTH, SCREEN_HEIGHT - ground_level - 20))
    
    # Background trees
    for obj in background_objects:
        if obj['type'] == 'tree' and -50 < obj['x'] < SCREEN_WIDTH + 50:
            draw_tree(obj['x'], obj['height'])
        obj['x'] -= current_speed * 0.2

def draw_tree(x, height):
    """Draw a simple tree"""
    trunk_width = 8
    trunk_height = height // 3
    crown_radius = height // 4
    
    # Trunk
    pygame.draw.rect(screen, TREE_BROWN, (x - trunk_width//2, ground_level - trunk_height, trunk_width, trunk_height))
    # Crown
    pygame.draw.circle(screen, TREE_GREEN, (int(x), int(ground_level - trunk_height - crown_radius//2)), crown_radius)

def spawn_obstacle():
    """Creates obstacles"""
    global pattern_index
    
    obstacle_type = obstacle_pattern[pattern_index]
    
    last_obstacle_x = 0
    if obstacles:
        last_obstacle_x = obstacles[-1]['hitbox'].x
        
    gap = random.randint(280, 400)
    x_pos = max(SCREEN_WIDTH + 50, last_obstacle_x + 120 + gap)

    if obstacle_type == 'up':
        height = random.randint(40, 65)
        width = random.randint(90, 130)
        y_pos = ground_level - player_normal_height - height + 25
        
        hitbox = pygame.Rect(x_pos, y_pos, width, height)
        obstacles.append({'type': 'up', 'hitbox': hitbox, 'width': width, 'height': height})
        
    elif obstacle_type == 'down':
        height = random.randint(50, 85)
        width = random.randint(45, 70)
        y_pos = ground_level - height
        
        hitbox = pygame.Rect(x_pos, y_pos, width, height)
        obstacles.append({
            'type': 'down', 'hitbox': hitbox, 'width': width, 'height': height,
            'rock_type': random.choice(['boulder', 'spikes', 'crystal'])
        })
        
    else:  # dig
        width = random.randint(120, 180)
        depth = random.randint(45, 70)
        
        hitbox = pygame.Rect(x_pos, ground_level - depth + 20, width, depth - 20)
        obstacles.append({'type': 'dig', 'hitbox': hitbox, 'width': width, 'depth': depth})
    
    pattern_index = (pattern_index + 1) % len(obstacle_pattern)

def draw_realistic_human(surface, x, y, width, height, crouching, jumping, digging):
    """Draws a realistic human character with proper proportions"""
    time = pygame.time.get_ticks()
    
    # Human proportions (head = 1 unit, body = 7-8 units)
    head_size = height // 8
    torso_height = height // 2.5
    leg_height = height - head_size - torso_height
    
    # Animation effects
    bounce = 0 if jumping or crouching else int(1 * math.sin(time * 0.01))
    
    # Calculate positions
    head_x = x + width // 2
    head_y = y + head_size + bounce
    neck_y = head_y + head_size // 2
    shoulder_y = neck_y + head_size // 4
    torso_bottom_y = shoulder_y + torso_height
    hip_y = torso_bottom_y
    
    # === HEAD ===
    # Head shadow
    pygame.draw.circle(surface, SKIN_SHADOW, (head_x + 1, head_y + 1), head_size)
    # Main head
    pygame.draw.circle(surface, SKIN_TONE, (head_x, head_y), head_size)
    
    # Hair
    hair_points = [
        (head_x - head_size, head_y - head_size//2),
        (head_x + head_size, head_y - head_size//2),
        (head_x + head_size//2, head_y - head_size),
        (head_x - head_size//2, head_y - head_size)
    ]
    pygame.draw.polygon(surface, HAIR_COLOR, hair_points)
    
    # Face features
    eye_y = head_y - head_size // 4
    # Eyes
    pygame.draw.circle(surface, WHITE, (head_x - head_size//3, eye_y), 3)
    pygame.draw.circle(surface, WHITE, (head_x + head_size//3, eye_y), 3)
    pygame.draw.circle(surface, BLACK, (head_x - head_size//3, eye_y), 2)
    pygame.draw.circle(surface, BLACK, (head_x + head_size//3, eye_y), 2)
    
    # Nose (small line)
    pygame.draw.line(surface, SKIN_SHADOW, (head_x, head_y), (head_x, head_y + 3), 1)
    
    # Mouth
    mouth_y = head_y + head_size // 4
    if jumping:
        # Surprised mouth (O shape)
        pygame.draw.circle(surface, BLACK, (head_x, mouth_y), 2)
    else:
        # Smile
        smile_rect = pygame.Rect(head_x - 4, mouth_y - 2, 8, 4)
        pygame.draw.arc(surface, BLACK, smile_rect, 0, math.pi, 2)
    
    # === TORSO ===
    # Neck
    pygame.draw.line(surface, SKIN_TONE, (head_x, head_y + head_size//2), (head_x, neck_y + 5), 6)
    
    # Shirt (torso)
    torso_width = width * 0.8
    torso_rect = pygame.Rect(x + (width - torso_width)//2, shoulder_y, torso_width, torso_height)
    
    # Shirt shadow
    shadow_rect = pygame.Rect(torso_rect.x + 2, torso_rect.y + 2, torso_rect.width, torso_rect.height)
    pygame.draw.rect(surface, SHIRT_SHADOW, shadow_rect)
    
    # Main shirt
    pygame.draw.rect(surface, SHIRT_COLOR, torso_rect)
    pygame.draw.rect(surface, SHIRT_SHADOW, torso_rect, 2)
    
    # === ARMS ===
    shoulder_left = (torso_rect.left, shoulder_y + 5)
    shoulder_right = (torso_rect.right, shoulder_y + 5)
    arm_length = torso_height * 0.8
    
    if digging:
        # Digging pose - arms forward
        elbow_left = (shoulder_left[0] + arm_length//2, shoulder_left[1] + 10)
        hand_left = (elbow_left[0] + arm_length//2 + 5, elbow_left[1] + 15)
        elbow_right = (shoulder_right[0] + arm_length//2, shoulder_right[1] + 10)
        hand_right = (elbow_right[0] + arm_length//2 + 5, elbow_right[1] + 15)
        
        # Digging particles
        if random.random() < 0.3:
            add_particle_effect(hand_right[0] + 10, hand_right[1], DIRT_BROWN, 2)
            
    elif jumping:
        # Arms up and out when jumping
        elbow_left = (shoulder_left[0] - 15, shoulder_left[1] - 10)
        hand_left = (elbow_left[0] - 10, elbow_left[1] - 15)
        elbow_right = (shoulder_right[0] + 15, shoulder_right[1] - 10)
        hand_right = (elbow_right[0] + 10, elbow_right[1] - 15)
        
    else:
        # Running arms - alternating swing
        arm_swing = math.sin(time * 0.02) * 15
        elbow_left = (shoulder_left[0] - 8 + arm_swing, shoulder_left[1] + arm_length//2)
        hand_left = (elbow_left[0] - 5 + arm_swing, elbow_left[1] + arm_length//2)
        elbow_right = (shoulder_right[0] + 8 - arm_swing, shoulder_right[1] + arm_length//2)
        hand_right = (elbow_right[0] + 5 - arm_swing, elbow_right[1] + arm_length//2)
    
    # Draw arms (upper arm, forearm)
    pygame.draw.line(surface, SKIN_SHADOW, (shoulder_left[0] + 1, shoulder_left[1] + 1), 
                    (elbow_left[0] + 1, elbow_left[1] + 1), 8)
    pygame.draw.line(surface, SKIN_TONE, shoulder_left, elbow_left, 8)
    pygame.draw.line(surface, SKIN_TONE, elbow_left, hand_left, 6)
    
    pygame.draw.line(surface, SKIN_SHADOW, (shoulder_right[0] + 1, shoulder_right[1] + 1), 
                    (elbow_right[0] + 1, elbow_right[1] + 1), 8)
    pygame.draw.line(surface, SKIN_TONE, shoulder_right, elbow_right, 8)
    pygame.draw.line(surface, SKIN_TONE, elbow_right, hand_right, 6)
    
    # Hands
    pygame.draw.circle(surface, SKIN_TONE, hand_left, 4)
    pygame.draw.circle(surface, SKIN_TONE, hand_right, 4)
    
    # === LEGS ===
    hip_left = (torso_rect.left + torso_rect.width//4, hip_y)
    hip_right = (torso_rect.right - torso_rect.width//4, hip_y)
    
    if crouching:
        # Crouched legs
        knee_left = (hip_left[0] - 5, hip_y + leg_height//2)
        foot_left = (knee_left[0] - 8, y + height)
        knee_right = (hip_right[0] + 5, hip_y + leg_height//2)
        foot_right = (knee_right[0] + 8, y + height)
        
    elif jumping:
        # Jumping legs - knees up
        knee_left = (hip_left[0] - 10, hip_y + leg_height//3)
        foot_left = (knee_left[0] - 5, knee_left[1] + leg_height//3)
        knee_right = (hip_right[0] + 10, hip_y + leg_height//3)
        foot_right = (knee_right[0] + 5, knee_right[1] + leg_height//3)
        
    else:
        # Running legs - alternating
        leg_swing = math.sin(time * 0.025) * 12
        knee_left = (hip_left[0] + leg_swing//2, hip_y + leg_height//2)
        foot_left = (knee_left[0] + leg_swing, y + height)
        knee_right = (hip_right[0] - leg_swing//2, hip_y + leg_height//2)
        foot_right = (knee_right[0] - leg_swing, y + height)
        
        # Running dust
        if random.random() < 0.15:
            add_particle_effect(foot_left[0], foot_left[1], (200, 180, 140), 2)
    
    # Draw pants (thighs)
    pygame.draw.line(surface, PANTS_SHADOW, (hip_left[0] + 1, hip_left[1] + 1), 
                    (knee_left[0] + 1, knee_left[1] + 1), 12)
    pygame.draw.line(surface, PANTS_COLOR, hip_left, knee_left, 12)
    pygame.draw.line(surface, PANTS_SHADOW, (hip_right[0] + 1, hip_right[1] + 1), 
                    (knee_right[0] + 1, knee_right[1] + 1), 12)
    pygame.draw.line(surface, PANTS_COLOR, hip_right, knee_right, 12)
    
    # Draw shins
    pygame.draw.line(surface, PANTS_COLOR, knee_left, foot_left, 10)
    pygame.draw.line(surface, PANTS_COLOR, knee_right, foot_right, 10)
    
    # Draw shoes
    shoe_width = 12
    shoe_height = 6
    
    # Left shoe
    left_shoe_rect = pygame.Rect(foot_left[0] - shoe_width//2, foot_left[1] - shoe_height//2, 
                                shoe_width, shoe_height)
    pygame.draw.ellipse(surface, SHOE_COLOR, left_shoe_rect)
    
    # Right shoe
    right_shoe_rect = pygame.Rect(foot_right[0] - shoe_width//2, foot_right[1] - shoe_height//2, 
                                 shoe_width, shoe_height)
    pygame.draw.ellipse(surface, SHOE_COLOR, right_shoe_rect)

def draw_obstacle(obstacle):
    """Draws obstacles"""
    hitbox = obstacle['hitbox']
    
    if obstacle['type'] == 'up':
        # Hanging obstacle
        pygame.draw.rect(screen, OBSTACLE_GRAY, hitbox)
        pygame.draw.rect(screen, ROCK_COLOR, hitbox, 3)
        
        # Stalactites
        num_stalactites = hitbox.width // 20
        for i in range(num_stalactites):
            x = hitbox.x + (i + 1) * hitbox.width // (num_stalactites + 1)
            points = [(x - 5, hitbox.bottom), (x + 5, hitbox.bottom), (x, hitbox.bottom + 15)]
            pygame.draw.polygon(screen, ROCK_COLOR, points)
            
    elif obstacle['type'] == 'down':
        rock_type = obstacle.get('rock_type', 'boulder')
        
        if rock_type == 'boulder':
            center = hitbox.center
            radius = min(hitbox.width, hitbox.height) // 2
            pygame.draw.circle(screen, OBSTACLE_GRAY, center, radius)
            pygame.draw.circle(screen, ROCK_COLOR, center, radius, 3)
            
        elif rock_type == 'spikes':
            pygame.draw.rect(screen, OBSTACLE_GRAY, hitbox)
            num_spikes = hitbox.width // 15
            for i in range(num_spikes):
                spike_x = hitbox.x + i * 15 + 7
                points = [(spike_x - 6, hitbox.bottom), (spike_x + 6, hitbox.bottom), (spike_x, hitbox.top - 8)]
                pygame.draw.polygon(screen, ROCK_COLOR, points)
                
        else:  # crystal
            center = hitbox.center
            points = [
                (center[0], hitbox.top - 5),
                (hitbox.right + 3, center[1]),
                (center[0], hitbox.bottom + 5),
                (hitbox.left - 3, center[1])
            ]
            pygame.draw.polygon(screen, CRYSTAL_PURPLE, points)
            pygame.draw.polygon(screen, CRYSTAL_LIGHT, points, 3)
            
    else:  # dig hole
        hole_rect = pygame.Rect(hitbox.x, ground_level, obstacle['width'], obstacle['depth'])
        pygame.draw.rect(screen, DIG_BROWN, hole_rect)
        pygame.draw.rect(screen, BLACK, hole_rect, 3)
        
        # Walls
        pygame.draw.line(screen, DIRT_BROWN, (hitbox.x, ground_level), 
                        (hitbox.x, ground_level + obstacle['depth']), 5)
        pygame.draw.line(screen, DIRT_BROWN, (hitbox.x + obstacle['width'], ground_level), 
                        (hitbox.x + obstacle['width'], ground_level + obstacle['depth']), 5)

def reset_game():
    """Reset game state"""
    global player_y, player_velocity_y, player_height, is_jumping, is_crouching, is_digging
    global obstacles, game_over, game_started, score, pattern_index, current_speed
    
    player_y = ground_level - player_normal_height
    player_velocity_y = 0
    player_height = player_normal_height
    is_jumping = False
    is_crouching = False
    is_digging = False
    
    obstacles.clear()
    pattern_index = 0
    for _ in range(4):
        spawn_obstacle()

    game_over = False
    game_started = False
    score = 0
    current_speed = initial_speed
    create_background()

# --- Main Game Loop ---
reset_game()
running = True
clock = pygame.time.Clock()

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if not game_started and not game_over and event.key == pygame.K_SPACE:
                game_started = True
            if game_over and event.key == pygame.K_r:
                reset_game()

    # Game logic
    if game_started and not game_over:
        keys = pygame.key.get_pressed()

        # Jump
        if not is_jumping and (keys[pygame.K_w] or keys[pygame.K_UP]):
            is_jumping = True
            player_velocity_y = jump_strength

        # Crouch/Dig
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and not is_jumping:
            is_crouching = True
            player_height = player_crouch_height
            
            # Check if over dig hole
            for obs in obstacles:
                if obs['type'] == 'dig' and obs['hitbox'].x <= player_x <= obs['hitbox'].x + obs['width']:
                    is_digging = True
                    break
            else:
                is_digging = False
        else:
            is_crouching = False
            is_digging = False
            player_height = player_normal_height

        # Update game state
        score += 1
        current_speed = initial_speed + (score // 800) * 0.7
        
        # Move obstacles
        for obs in obstacles[:]:
            obs['hitbox'].x -= current_speed
            if obs['hitbox'].right < 0:
                obstacles.remove(obs)
        
        if len(obstacles) < 6:
            spawn_obstacle()

        # Player physics
        if is_jumping:
            player_velocity_y += gravity
            player_y += player_velocity_y

        if player_y + player_height >= ground_level:
            player_y = ground_level - player_height
            is_jumping = False
            player_velocity_y = 0
            
        # Collision detection
        current_player_y = player_y
        if is_crouching and not is_jumping:
            current_player_y = ground_level - player_crouch_height
        player_rect = pygame.Rect(player_x, current_player_y, player_width, player_height)

        for obs in obstacles:
            if obs['type'] == 'dig':
                if not is_crouching and player_rect.colliderect(obs['hitbox']):
                    game_over = True
                    game_started = False
            else:
                if player_rect.colliderect(obs['hitbox']):
                    game_over = True
                    game_started = False

    # Update particles
    for particle in particles[:]:
        if not particle.update():
            particles.remove(particle)

    # Drawing
    draw_background()

    # Draw obstacles
    for obs in obstacles:
        draw_obstacle(obs)

    # Draw particles
    for particle in particles:
        particle.draw(screen)

    # Draw player
    current_player_y_draw = player_y
    if is_crouching and not is_jumping:
        current_player_y_draw = ground_level - player_crouch_height
    
    draw_realistic_human(screen, player_x, current_player_y_draw, player_width, player_height, 
                        is_crouching, is_jumping, is_digging)

    # UI
    score_text = small_font.render(f"Score: {score}  Speed: {current_speed:.1f}", True, BLACK)
    screen.blit(score_text, (15, 15))
    
    controls_text = tiny_font.render("W/↑: Jump  S/↓: Crouch/Dig  SPACE: Start  R: Restart", True, BLACK)
    screen.blit(controls_text, (15, 55))

    # Messages
    if not game_started and not game_over:
        title_text = font.render("HUMAN RUNNER", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 60))
        screen.blit(title_text, title_rect)
        
        start_text = small_font.render("Press SPACEBAR to Start", True, BLACK)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20))
        screen.blit(start_text, start_rect)

    if game_over:
        game_over_text = font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40))
        screen.blit(game_over_text, game_over_rect)
        
        restart_text = small_font.render("Press R to Restart", True, BLACK)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20))
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()