import pygame
import sys 
import random
import time

from soldier import load_all_soldier_animations, ALL_SOLDIER_ANIMATIONS
from BadSoldier import BadSoldier, BadSoldierAI
from wave_spawner import WaveSpawner
from run import run_game_loop
from main_menu import show_main_menu

UNIQUE_ID = random.randint(1000, 9999)

# ============================================================================
# ИНІЦИАЛИЗАЦІЯ
pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) 
SCREEN_WIDTH = screen.get_width()
SCREEN_HEIGHT = screen.get_height()

clock = pygame.time.Clock()

# ============================================================================
#  ПОКАЗУЄМО ГОЛОВНЕ МЕНЮ
menu_result = show_main_menu(screen, clock)

if menu_result is None:
    pygame.quit()
    sys.exit()

START_UA_COUNT = menu_result['ua_count']
ENEMY_BASE_COUNT = menu_result['enemy_base']
ENEMY_WAVE_BONUS = menu_result['enemy_bonus']

# Параметри матриці
CELL_SIZE = 25
GRID_WIDTH = 200
GRID_HEIGHT = 140
WORLD_WIDTH = GRID_WIDTH * CELL_SIZE
WORLD_HEIGHT = GRID_HEIGHT * CELL_SIZE
SCROLL_SPEED = 12

# Параметрм вогню
SHOOTING_RANGE = 20
SHOOTING_COOLDOWN = 0.5
SHOOTING_ANIMATION_DURATION = 0.2

# ============================================================================
# ЗАГРУЗКА РЕСУРСІВ
base_path = r"C:\Users\Dima\Desktop\Pictures_artillerist\Map_obj"

forrest_image = pygame.image.load(f"{base_path}\\Forrest.png").convert_alpha()
background_image = pygame.image.load(f"{base_path}\\Ground.png").convert() 
forrest2_image = pygame.image.load(f"{base_path}\\Forrest2.png").convert_alpha()
Mark_shahed = pygame.image.load(f"{base_path}\\Mark_fallen_shahed.png").convert_alpha()
Mark_Hedgerows = pygame.image.load(f"{base_path}\\Mark_Hedgerows.png").convert_alpha()
Mark_Dragon = pygame.image.load(f"{base_path}\\Mark_Dragon_teeth.png").convert_alpha()
Mark_Bomb = pygame.image.load(f"{base_path}\\Mark_Bombed_zone.png").convert_alpha()
Mark_Graves = pygame.image.load(f"{base_path}\\Mark_tree_friends.png").convert_alpha()
Capturable_Trench = pygame.image.load(f"{base_path}\\Capturable_trench.png").convert_alpha()

Boomed = pygame.image.load(f"{base_path}\\Boomed.png").convert_alpha()

# Постріли
Shooting_Element = pygame.image.load(f"{base_path}\\Shooting_Element.png").convert_alpha()
Shooting_Element2 = pygame.image.load(f"{base_path}\\Shooting_Element2.png").convert_alpha()

# розмір Лісів
forrest_image = pygame.transform.scale(forrest_image, (CELL_SIZE * 5, CELL_SIZE * 3))
forrest2_image = pygame.transform.scale(forrest2_image, (CELL_SIZE * 4, CELL_SIZE * 4))

# Розмір пострілів
Shooting_Element = pygame.transform.scale(Shooting_Element, (CELL_SIZE//4, CELL_SIZE//4))
Shooting_Element.set_colorkey((255, 255, 255))

Shooting_Element2 = pygame.transform.scale(Shooting_Element2, (CELL_SIZE//4, CELL_SIZE//4))
Shooting_Element2.set_colorkey((255, 255, 255))

# Перелік елементів
OBJECT_TYPES = {
    'type1': {
        'image': forrest_image, 
        'grid_width': 5,
        'grid_height': 3,
        'is_forest': True
    },
    'type2': {
        'image': forrest2_image, 
        'grid_width': 4,
        'grid_height': 4,
        'is_forest': True
    },
    'marker_shahed': {
        'image': Mark_shahed, 
        'grid_width': 6,
        'grid_height': 3,
        'is_forest': False
    },
    'marker_hedgerows': {
        'image': Mark_Hedgerows, 
        'grid_width': 12,
        'grid_height': 4,
        'is_forest': False
    },
    'marker_dragon': {
        'image': Mark_Dragon, 
        'grid_width': 4,
        'grid_height': 16,
        'is_forest': False
    },
    'marker_bomb': {
        'image': Mark_Bomb, 
        'grid_width': 4,
        'grid_height': 3,
        'is_forest': False
    },
    'marker_graves': {
        'image': Mark_Graves, 
        'grid_width': 1,
        'grid_height': 1,
        'is_forest': False
    },
    'capturable_trench': {
        'image': Capturable_Trench, 
        'grid_width': 1,
        'grid_height': 4,
        'is_forest': False
    },
}

# Фіксовані маркери
fixed_marker_data = [
    {'grid_x': 20, 'grid_y': 10, 'type': 'marker_shahed'},      
    {'grid_x': 170, 'grid_y': 120, 'type': 'marker_hedgerows'},  
    {'grid_x': 100, 'grid_y': 5, 'type': 'marker_dragon'},        
    {'grid_x': 30, 'grid_y': 130, 'type': 'marker_bomb'},        
    {'grid_x': 180, 'grid_y': 60, 'type': 'marker_graves'},       

    {'grid_x': 25, 'grid_y': 20, 'type': 'capturable_trench'},
    {'grid_x': 30, 'grid_y': 35, 'type': 'capturable_trench'},
    {'grid_x': 28, 'grid_y': 50, 'type': 'capturable_trench'},
    {'grid_x': 32, 'grid_y': 65, 'type': 'capturable_trench'},
    {'grid_x': 26, 'grid_y': 80, 'type': 'capturable_trench'},
    {'grid_x': 30, 'grid_y': 95, 'type': 'capturable_trench'},
    {'grid_x': 28, 'grid_y': 110, 'type': 'capturable_trench'},
    
    {'grid_x': 60, 'grid_y': 40, 'type': 'capturable_trench'},
    {'grid_x': 65, 'grid_y': 70, 'type': 'capturable_trench'},
    {'grid_x': 70, 'grid_y': 100, 'type': 'capturable_trench'},
    
    {'grid_x': 100, 'grid_y': 55, 'type': 'capturable_trench'},
    {'grid_x': 105, 'grid_y': 85, 'type': 'capturable_trench'},
    
    {'grid_x': 140, 'grid_y': 60, 'type': 'capturable_trench'},
    {'grid_x': 145, 'grid_y': 90, 'type': 'capturable_trench'},
    {'grid_x': 150, 'grid_y': 110, 'type': 'capturable_trench'},
]

# підвантаження анімацій
load_all_soldier_animations() 

# Матриці
forest_matrix = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
grid_matrix = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
trench_matrix = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# ============================================================================
# функція перевірки ліній видимості
def has_line_of_sight(x1, y1, x2, y2):

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    
    x, y = x1, y1
    x_inc = 1 if x2 > x1 else -1
    y_inc = 1 if y2 > y1 else -1
    
    if dx > dy:
        error = dx / 2
        while x != x2:
            if (x, y) != (x1, y1):
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    if forest_matrix[y][x]:
                        return False
            
            error -= dy
            if error < 0:
                y += y_inc
                error += dx
            x += x_inc
        
        if (x, y) != (x1, y1) and (x, y) != (x2, y2):
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                if forest_matrix[y][x]:
                    return False
    else:
        error = dy / 2
        while y != y2:
            if (x, y) != (x1, y1):
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    if forest_matrix[y][x]:
                        return False
            
            error -= dx
            if error < 0:
                x += x_inc
                error += dy
            y += y_inc
        
        if (x, y) != (x1, y1) and (x, y) != (x2, y2):
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                if forest_matrix[y][x]:
                    return False
    
    return True

def get_distance(x1, y1, x2, y2):
    return abs(x2 - x1) + abs(y2 - y1)

# ============================================================================
# Клас анімацій вогню

class ShootingEffect:
    def __init__(self, target_x, target_y, shooter_x, shooter_y):
        self.target_x = target_x
        self.target_y = target_y
        self.shooter_x = shooter_x
        self.shooter_y = shooter_y
        self.timer = 0
        self.duration = SHOOTING_ANIMATION_DURATION
        self.active = True
    
    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.active = False
    
    def draw(self, screen, camera_x, camera_y):
        if not self.active:
            return
        
        target_pixel_x = self.target_x * CELL_SIZE + CELL_SIZE // 2 - camera_x
        target_pixel_y = self.target_y * CELL_SIZE + CELL_SIZE // 2 - camera_y
        
        explosion_rect = Shooting_Element.get_rect(center=(target_pixel_x, target_pixel_y))
        screen.blit(Shooting_Element, explosion_rect)
        
        dx = self.target_x - self.shooter_x
        dy = self.target_y - self.shooter_y
        
        if abs(dx) > abs(dy):
            if dx > 0:
                flash_x = (self.shooter_x + 1) * CELL_SIZE + CELL_SIZE // 2 - camera_x
                flash_y = self.shooter_y * CELL_SIZE + CELL_SIZE // 2 - camera_y
            else:
                flash_x = (self.shooter_x - 1) * CELL_SIZE + CELL_SIZE // 2 - camera_x
                flash_y = self.shooter_y * CELL_SIZE + CELL_SIZE // 2 - camera_y
        else:
            if dy > 0:
                flash_x = self.shooter_x * CELL_SIZE + CELL_SIZE // 2 - camera_x
                flash_y = (self.shooter_y + 1) * CELL_SIZE + CELL_SIZE // 2 - camera_y
            else:
                flash_x = self.shooter_x * CELL_SIZE + CELL_SIZE // 2 - camera_x
                flash_y = (self.shooter_y - 1) * CELL_SIZE + CELL_SIZE // 2 - camera_y
        
        flash_rect = Shooting_Element2.get_rect(center=(flash_x, flash_y))
        screen.blit(Shooting_Element2, flash_rect)

# ============================================================================
# Колас солдата

class GridSoldier:
    def __init__(self, grid_x, grid_y, soldier_type, team):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.soldier_type = soldier_type
        self.team = team
        
        self.max_hp = 100
        self.hp = 100
        self.alive = True
        
        self.x = float(grid_x * CELL_SIZE + CELL_SIZE // 2)
        self.y = float(grid_y * CELL_SIZE + CELL_SIZE // 2)
        
        self.animations = ALL_SOLDIER_ANIMATIONS[soldier_type]
        self.current_direction = 'down'
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.15
        
        current_frame = self.animations['stay']
        self.image = pygame.transform.scale(current_frame, (CELL_SIZE, CELL_SIZE))
        
        self.selected = False
        self.base_move_speed = 1.0
        self.move_speed = self.base_move_speed
        
        self.path = []
        self.is_moving = False
        self.target_pixel_x = self.x
        self.target_pixel_y = self.y
        
        self.in_forest = False
        self.in_trench = False
        self.alpha = 255
        
        self.shooting_cooldown = 0
        self.is_shooting = False
        self.shooting_animation_timer = 0
        self.shooting_target = None

        self.waiting_for_cell = None
    
    def take_damage(self, damage):
        if not self.alive:
            return
        
        original_damage = damage
        
        if self.in_forest:
            damage *= 0.65
        
        if self.in_trench:
            damage *= 0.45
        
        damage = int(damage)
        self.hp -= damage
        
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
    
    def is_controllable(self):
        return self.team != 'BAD' and self.alive
    
    def get_selection_color(self):
        if not self.alive:
            return (100, 100, 100)
        return (255, 0, 0) if self.team == 'BAD' else (255, 255, 0)
    
    def is_visible(self):
        if not self.alive:
            return True
        if self.team == 'BAD' and self.in_forest:
            return False
        return True
    
    def set_path(self, path):
        if path and len(path) > 0 and self.alive:
            self.path = path
            self.is_moving = True
            self._set_next_waypoint()
    
    def stop_moving(self):
        self.path.clear()
        self.is_moving = False
        self.waiting_for_cell = None

        # Звільняємо резервації
        for cell, soldier in list(reserved_cells.items()):
            if soldier is self:
                del reserved_cells[cell]

        self.grid_x = int(self.x // CELL_SIZE)
        self.grid_y = int(self.y // CELL_SIZE)
        self.x = self.grid_x * CELL_SIZE + CELL_SIZE // 2
        self.y = self.grid_y * CELL_SIZE + CELL_SIZE // 2

        self.target_pixel_x = self.x
        self.target_pixel_y = self.y

        if not self.is_shooting:
            self.current_direction = 'stay'
            self.frame_index = 0
    
    def _set_next_waypoint(self):
        if not self.path:
            return

        next_grid_x, next_grid_y = self.path[0]
        if is_cell_occupied_by_soldier(next_grid_x, next_grid_y, exclude_soldier=self) \
            or (next_grid_x, next_grid_y) in reserved_cells:

            self.is_moving = False
            self.waiting_for_cell = (next_grid_x, next_grid_y)
            if not self.is_shooting:
                self.current_direction = 'stay'
            return

        reserved_cells[(next_grid_x, next_grid_y)] = self
        self.waiting_for_cell = None

        self.path.pop(0)
        self.target_pixel_x = next_grid_x * CELL_SIZE + CELL_SIZE // 2
        self.target_pixel_y = next_grid_y * CELL_SIZE + CELL_SIZE // 2

        dx = self.target_pixel_x - self.x
        dy = self.target_pixel_y - self.y

        if abs(dx) > abs(dy):
            self.current_direction = 'right' if dx > 0 else 'left'
        else:
            self.current_direction = 'down' if dy > 0 else 'up'

        self.is_moving = True

    def find_target(self, all_soldiers):
        if not self.alive:
            return None
        
        closest_enemy = None
        closest_distance = float('inf')
        
        for soldier in all_soldiers:
            if soldier.team == self.team or not soldier.alive:
                continue
            
            if not soldier.is_visible():
                continue
            
            distance = get_distance(self.grid_x, self.grid_y, soldier.grid_x, soldier.grid_y)
            
            if distance <= SHOOTING_RANGE and distance < closest_distance:
                if has_line_of_sight(self.grid_x, self.grid_y, soldier.grid_x, soldier.grid_y):
                    closest_enemy = soldier
                    closest_distance = distance
        
        return closest_enemy
    
    def start_shooting(self, target):
        self.is_shooting = True
        self.shooting_target = target
        self.shooting_animation_timer = 0
        
        dx = target.grid_x - self.grid_x
        dy = target.grid_y - self.grid_y
        
        if abs(dx) > abs(dy):
            self.current_direction = 'right' if dx > 0 else 'left'
        else:
            self.current_direction = 'down' if dy > 0 else 'up'
        
        damage = random.randint(0, 100)
        target.take_damage(damage)
    
    def update(self, dt, all_soldiers):
        if not self.alive:
            self.current_direction = 'dead'
            self.is_moving = False
            self.is_shooting = False
            self.path = []
            
            # Звільняємо резервації мертвого солдата
            for cell, soldier in list(reserved_cells.items()):
                if soldier is self:
                    del reserved_cells[cell]
            
            self._update_image()
            return
        if self.waiting_for_cell:
            wx, wy = self.waiting_for_cell
            if not is_cell_occupied_by_soldier(wx, wy, exclude_soldier=self) \
                and (wx, wy) not in reserved_cells:
                    self.is_moving = True
                    self._set_next_waypoint()
        
        # Оновлення статусів (ліс, окоп)
        self.in_forest = forest_matrix[self.grid_y][self.grid_x]
        self.in_trench = trench_matrix[self.grid_y][self.grid_x]
        
        if self.in_forest:
            self.move_speed = self.base_move_speed * 0.5
            if self.team == 'BAD':
                self.alpha = 0
            else:
                self.alpha = 128
        else:
            self.move_speed = self.base_move_speed
            self.alpha = 255
        
        # Кулдаун стрільби
        if self.shooting_cooldown > 0:
            self.shooting_cooldown -= dt
        
        # Анімація стрільби
        if self.is_shooting:
            self.shooting_animation_timer += dt
            if self.shooting_animation_timer >= SHOOTING_ANIMATION_DURATION:
                self.is_shooting = False
                self.shooting_target = None
                if not self.is_moving:
                    self.current_direction = 'stay'
        
        # Пошук цілі і стрільба
        if not self.is_shooting and self.shooting_cooldown <= 0:
            target = self.find_target(all_soldiers)
            if target:
                self.start_shooting(target)
                self.shooting_cooldown = SHOOTING_COOLDOWN
                
                shooting_effects.append(ShootingEffect(
                    target.grid_x, target.grid_y,
                    self.grid_x, self.grid_y
                ))
        
        # Рух
        if self.is_moving and not self.is_shooting:
            dx = self.target_pixel_x - self.x
            dy = self.target_pixel_y - self.y
            distance = (dx**2 + dy**2)**0.5
            
            if distance < self.move_speed:
                self.x = self.target_pixel_x
                self.y = self.target_pixel_y
                
                # Звільняємо резервацію після досягнення точки
                for cell, soldier in list(reserved_cells.items()):
                    if soldier is self:
                        del reserved_cells[cell]

                self.grid_x = int(self.x // CELL_SIZE)
                self.grid_y = int(self.y // CELL_SIZE)
                
                if self.path:
                    self._set_next_waypoint()
                else:
                    self.is_moving = False
                    self.current_direction = 'stay'
            else:
                self.x += (dx / distance) * self.move_speed
                self.y += (dy / distance) * self.move_speed
            
            # Анімація ходьби
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % 2
        elif self.path and not self.is_shooting:
            self._set_next_waypoint()
        
        # Анімація стрільби
        if self.is_shooting:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % 2
        
        self._update_image()

    def _update_image(self):
        if not self.alive:
            if 'dead' in self.animations:
                frame = self.animations['dead']
            else:
                frame = self.animations['stay']
        elif self.current_direction == 'stay' and not self.is_shooting:
            frame = self.animations['stay']
        elif self.current_direction in self.animations:
            if isinstance(self.animations[self.current_direction], list):
                frame = self.animations[self.current_direction][self.frame_index]
            else:
                frame = self.animations[self.current_direction]
        else:
            frame = self.animations['stay']
        
        scaled_frame = pygame.transform.scale(frame, (CELL_SIZE, CELL_SIZE))
        self.image = scaled_frame.copy()
        self.image.set_colorkey((255, 255, 255))
        
        if self.alive:
            self.image.set_alpha(self.alpha)
        else:
            self.image.set_alpha(180)
    
    def draw(self, screen, camera_x, camera_y):
        if not self.is_visible():
            if self.selected:
                rect_x = self.grid_x * CELL_SIZE - camera_x
                rect_y = self.grid_y * CELL_SIZE - camera_y
                pygame.draw.rect(screen, self.get_selection_color(), 
                               (rect_x, rect_y, CELL_SIZE, CELL_SIZE), 2)
            return
        
        draw_x = self.x - camera_x - self.image.get_width() // 2
        draw_y = self.y - camera_y - self.image.get_height() // 2
        screen.blit(self.image, (draw_x, draw_y))
        
        if self.selected and self.alive:
            # HP бар
            bar_width = CELL_SIZE
            bar_height = 4
            bar_x = self.x - camera_x - bar_width // 2
            bar_y = self.y - camera_y - CELL_SIZE // 2 - 8
            
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            
            hp_width = int(bar_width * (self.hp / self.max_hp))
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, hp_width, bar_height))
            
            # HP текст
            font_small = pygame.font.Font(None, 16)
            hp_text = font_small.render(f"{self.hp}/{self.max_hp}", True, (255, 255, 255))
            text_rect = hp_text.get_rect(center=(self.x - camera_x, bar_y - 6))
            screen.blit(hp_text, text_rect)
        
        # Рамка виділення
        if self.selected:
            rect_x = self.grid_x * CELL_SIZE - camera_x
            rect_y = self.grid_y * CELL_SIZE - camera_y
            pygame.draw.rect(screen, self.get_selection_color(), 
                           (rect_x, rect_y, CELL_SIZE, CELL_SIZE), 2)
        
        # Відображення шляху
        if self.selected and self.path and self.is_controllable():
            for gx, gy in self.path:
                px = gx * CELL_SIZE + CELL_SIZE // 2 - camera_x
                py = gy * CELL_SIZE + CELL_SIZE // 2 - camera_y
                pygame.draw.circle(screen, self.get_selection_color(), (int(px), int(py)), 3)

# =============================================================================================================
# ФУНКЦІЇ

def find_random_path(start_x, start_y, target_x, target_y):
    if target_x < 0 or target_x >= GRID_WIDTH or target_y < 0 or target_y >= GRID_HEIGHT:
        return []
    
    path = [(start_x, start_y)]
    current_x, current_y = start_x, start_y
    
    steps_x = abs(target_x - start_x)
    steps_y = abs(target_y - start_y)
    
    dir_x = 1 if target_x > start_x else -1 if target_x < start_x else 0
    dir_y = 1 if target_y > start_y else -1 if target_y < start_y else 0
    
    moves = ['x'] * steps_x + ['y'] * steps_y
    random.shuffle(moves)
    
    for move in moves:
        if move == 'x':
            current_x += dir_x
        else:
            current_y += dir_y
        
        if 0 <= current_x < GRID_WIDTH and 0 <= current_y < GRID_HEIGHT:
            path.append((current_x, current_y))
    
    return path

def is_cell_occupied_by_soldier(grid_x, grid_y, exclude_soldier=None): #=====================================фіксити трупи
    for soldier in all_soldiers:
        if soldier.alive and soldier != exclude_soldier and soldier.grid_x == grid_x and soldier.grid_y == grid_y:
            return True
    return False


def mark_cells_forest(grid_x, grid_y, grid_w, grid_h):
    for y in range(grid_y, min(grid_y + grid_h, GRID_HEIGHT)):
        for x in range(grid_x, min(grid_x + grid_w, GRID_WIDTH)):
            forest_matrix[y][x] = True

def mark_cells_occupied(grid_x, grid_y, grid_w, grid_h):
    for y in range(grid_y, min(grid_y + grid_h, GRID_HEIGHT)):
        for x in range(grid_x, min(grid_x + grid_w, GRID_WIDTH)):
            grid_matrix[y][x] = True

def mark_cells_trench(grid_x, grid_y, grid_w, grid_h):
    for y in range(grid_y, min(grid_y + grid_h, GRID_HEIGHT)):
        for x in range(grid_x, min(grid_x + grid_w, GRID_WIDTH)):
            trench_matrix[y][x] = True

def check_cells_free(grid_x, grid_y, grid_w, grid_h):
    if grid_x < 0 or grid_y < 0:
        return False
    if grid_x + grid_w > GRID_WIDTH or grid_y + grid_h > GRID_HEIGHT:
        return False
    
    for y in range(grid_y, grid_y + grid_h):
        for x in range(grid_x, grid_x + grid_w):
            if grid_matrix[y][x]:
                return False
    return True

def draw_grid(screen, camera_x, camera_y):
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(screen, (50, 50, 50), 
                        (x * CELL_SIZE - camera_x, -camera_y),
                        (x * CELL_SIZE - camera_x, WORLD_HEIGHT - camera_y), 1)
    
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(screen, (50, 50, 50),
                        (-camera_x, y * CELL_SIZE - camera_y),
                        (WORLD_WIDTH - camera_x, y * CELL_SIZE - camera_y), 1)

# ============================================================================
# ГЕНЕРАЦІЯ  СВІТУ

world_objects = []

for marker in fixed_marker_data:
    marker_type_data = OBJECT_TYPES[marker['type']]
    grid_w = marker_type_data.get('grid_width', 1)
    grid_h = marker_type_data.get('grid_height', 1)
    
    mark_cells_occupied(marker['grid_x'], marker['grid_y'], grid_w, grid_h)
    
    if marker['type'] == 'capturable_trench':
        mark_cells_trench(marker['grid_x'], marker['grid_y'], grid_w, grid_h)
    
    if marker_type_data.get('is_forest', False):
        mark_cells_forest(marker['grid_x'], marker['grid_y'], grid_w, grid_h)
    
    pixel_x = marker['grid_x'] * CELL_SIZE
    pixel_y = marker['grid_y'] * CELL_SIZE
    
    world_objects.append({
        'x': pixel_x,
        'y': pixel_y,
        'type': marker['type'],
        'grid_x': marker['grid_x'],
        'grid_y': marker['grid_y']
    })

NUM_FOREST_OBJECTS = 140
random_keys = ['type1', 'type2'] 

for _ in range(NUM_FOREST_OBJECTS):
    selected_type_key = random.choice(random_keys) 
    selected_type_data = OBJECT_TYPES[selected_type_key]
    
    obj_grid_width = selected_type_data['grid_width']
    obj_grid_height = selected_type_data['grid_height']
    
    attempts = 0
    max_attempts = 50
    
    while attempts < max_attempts:
        grid_x = random.randint(0, GRID_WIDTH - obj_grid_width)
        grid_y = random.randint(0, GRID_HEIGHT - obj_grid_height)
        
        if check_cells_free(grid_x, grid_y, obj_grid_width, obj_grid_height):
            mark_cells_occupied(grid_x, grid_y, obj_grid_width, obj_grid_height)
            mark_cells_forest(grid_x, grid_y, obj_grid_width, obj_grid_height)
            
            pixel_x = grid_x * CELL_SIZE
            pixel_y = grid_y * CELL_SIZE
            
            world_objects.append({
                'x': pixel_x, 
                'y': pixel_y, 
                'type': selected_type_key,
                'grid_x': grid_x,
                'grid_y': grid_y
            })
            break
        
        attempts += 1

# ============================================================================
# Створення солдатів
all_soldiers = []
shooting_effects = []
reserved_cells = {} 

cols = 5
for i in range(START_UA_COUNT):
    all_soldiers.append(
        GridSoldier(
            grid_x=1 + i % cols,
            grid_y=1 + i // cols,
            soldier_type='soldier_ua',
            team='UA'
        )
    )

print(f"Створено {START_UA_COUNT} UA солдатів")

# ІНІЦІАЛІЗАЦІЯ ВОЛН
wave_spawner = WaveSpawner(GRID_WIDTH, GRID_HEIGHT)
wave_spawner.enemy_base_count = ENEMY_BASE_COUNT
wave_spawner.enemy_wave_bonus = ENEMY_WAVE_BONUS

bad_soldiers = []

# ПУСК ГРИ
game_stats = {
    'start_time': pygame.time.get_ticks(), 
    'initial_ua_count': START_UA_COUNT,
    'ua_losses': 0,  
    'enemies_killed': 0, 
    'game_over': False,  
    'game_over_reason': '',  
    'survival_time': 0  
}

# -----------------------------------------------------------------------------------------------
game_data = {
    'screen': screen,
    'clock': clock,
    'CELL_SIZE': CELL_SIZE,
    'GRID_WIDTH': GRID_WIDTH,
    'GRID_HEIGHT': GRID_HEIGHT,
    'WORLD_WIDTH': WORLD_WIDTH,
    'WORLD_HEIGHT': WORLD_HEIGHT,
    'SCROLL_SPEED': SCROLL_SPEED,
    'SCREEN_WIDTH': SCREEN_WIDTH,
    'SCREEN_HEIGHT': SCREEN_HEIGHT,
    'background_image': background_image,
    'world_objects': world_objects,
    'OBJECT_TYPES': OBJECT_TYPES,
    'all_soldiers': all_soldiers,
    'shooting_effects': shooting_effects,
    'reserved_cells': reserved_cells,
    'forest_matrix': forest_matrix,
    'trench_matrix': trench_matrix,
    'find_random_path': find_random_path,
    'draw_grid': draw_grid,
    'GridSoldier': GridSoldier,
    'wave_spawner': wave_spawner,
    'bad_soldiers': bad_soldiers,
    'game_stats': game_stats,
}

# Запуск ігрового циклу ------------------------------------------------------------------------
run_game_loop(game_data)
pygame.quit() 
sys.exit()