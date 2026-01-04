import pygame
import sys
import os
import pygame.time

DIRECTIONS = ['right', 'left', 'up', 'down']
FRAME_COUNT = 3
ANIMATION_SPEED = 0.15 # ШВИДКІСТЬ АНІМАЦІЇ ЗМІНЮВАТИ ТУУУТ

ALL_SOLDIER_ANIMATIONS = {}

def load_all_soldier_animations():
    global ALL_SOLDIER_ANIMATIONS
    base_path = r"C:\Users\Dima\Desktop\Pictures_artillerist\Soldiers"
    

        # ЗАГРУЗКА BAD_SOLDIER
    animations_bad = {
        'down': [
            pygame.image.load(os.path.join(base_path, "BSD1.png")).convert_alpha(),
            pygame.image.load(os.path.join(base_path, "BSD2.png")).convert_alpha(),

        ],
        'up': [
            pygame.image.load(os.path.join(base_path, "BSU1.png")).convert_alpha(),
            pygame.image.load(os.path.join(base_path, "BSU2.png")).convert_alpha(),
        ],
        'left': [
            pygame.image.load(os.path.join(base_path, "BSL1.png")).convert_alpha(),
            pygame.image.load(os.path.join(base_path, "BSL2.png")).convert_alpha(),
        ],
        'right': [
            pygame.image.load(os.path.join(base_path, "BSR1.png")).convert_alpha(),
            pygame.image.load(os.path.join(base_path, "BSR2.png")).convert_alpha(),
        ],
        'stay': pygame.image.load(os.path.join(base_path, "BSS.png")).convert_alpha(),
        'dead': pygame.image.load(os.path.join(base_path, "Dead.png")).convert_alpha()
    }
        
        # ЗАГРУЗКА UA_SOLDIER
    animations_ua = {
        'down': [
            pygame.image.load(os.path.join(base_path, "UAD1.png")).convert_alpha(),
            pygame.image.load(os.path.join(base_path, "UAD2.png")).convert_alpha(),
        ],
        'up': [
            pygame.image.load(os.path.join(base_path, "UAU1.png")).convert_alpha(),
            pygame.image.load(os.path.join(base_path, "UAU2.png")).convert_alpha(),
        ],
        'left': [
            pygame.image.load(os.path.join(base_path, "UAL1.png")).convert_alpha(),
            pygame.image.load(os.path.join(base_path, "UAL2.png")).convert_alpha(),
        ],
        'right': [
            pygame.image.load(os.path.join(base_path, "UAR1.png")).convert_alpha(),
            pygame.image.load(os.path.join(base_path, "UAR2.png")).convert_alpha(),
        ],
        'dead': pygame.image.load(os.path.join(base_path, "Dead.png")).convert_alpha(),
        'stay': pygame.image.load(os.path.join(base_path, "UAS.png")).convert_alpha()
    }
        
    ALL_SOLDIER_ANIMATIONS['soldier_bad'] = animations_bad
    ALL_SOLDIER_ANIMATIONS['soldier_ua'] = animations_ua


# ----------------------------------------------------------------------
# --- КЛАСС СОЛДАТА З логікою

class Soldier(pygame.sprite.Sprite):
    def __init__(self, x, y, soldier_type):
        super().__init__()
        
        if soldier_type not in ALL_SOLDIER_ANIMATIONS:
             raise ValueError(f"Тип солдата '{soldier_type}' не знайдено.")

        self.soldier_type = soldier_type 
        self.animations = ALL_SOLDIER_ANIMATIONS[soldier_type]
        
        #  ФИЗІКА 
        self.x = float(x) 
        self.y = float(y) 
        self.move_speed = 1
             
        # NPC ЛОГІКА
        self.target_x = self.x 
        self.target_y = self.y 
        self.is_moving_to_target = False 

        #Таймер
        SHOOT_TIMER = pygame.USEREVENT + 1 
        pygame.time.set_timer(SHOOT_TIMER, 1000)
        
        #  АНІМАЦИЯ 
        self.current_direction = 'down' 
        self.frame_index = 0 
        self.animation_speed = ANIMATION_SPEED 
        self.image = self.animations[self.current_direction][self.frame_index]

        self.rect = self.image.get_rect(topleft=(int(self.x), int(self.y)))

        self.rect.topleft = (int(self.x), int(self.y))
        

    def set_target(self, target_x, target_y):
        self.target_x = float(target_x)
        self.target_y = float(target_y)
        self.is_moving_to_target = True
        

    def update(self, timer_fired):
        distantionX = self.x - self.target_x
        distantionY = self.y - self.target_y
            #coin_flip = random.randint(0, 1)

        self.x = self.x + 0.13


    def draw(self, surface, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        surface.blit(self.image, (draw_x, draw_y))