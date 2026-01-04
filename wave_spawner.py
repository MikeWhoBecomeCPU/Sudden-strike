import random
from BadSoldier import BadSoldier, BadSoldierAI

class WaveSpawner:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        
        # Хвилі атаки
        self.current_wave = 0
        self.wave_timer = 0
        self.wave_interval = 60.0  # 60 секунд між хвилями
        self.first_wave_delay = 5.0    # Перша хвиля через 5 секунд
        self.is_first_wave = True
        self.wave_active = False
        
        #НАЛАШТУВАННЯ КІЛЬКОСТІ ВОРОГІВ -------------------------------------------------------------==============================
        self.enemy_base_count = 5      # Базова кількість
        self.enemy_wave_bonus = 3      # Приріст за кожну хвилю
        
        # Зони спавну  
        self.spawn_zones = self._generate_spawn_zones()
        
        # Статистика
        self.total_spawned = 0
        self.active_enemies = 0
    
    def _generate_spawn_zones(self):
        #Генерація зон спавну (права сторона карти)
        zones = []
        right_start = int(self.grid_width * 0.75)
        num_zones = 4
        zone_height = self.grid_height // num_zones
        
        for i in range(num_zones):
            zone = {
                'x_min': right_start,
                'x_max': self.grid_width - 1,
                'y_min': i * zone_height,
                'y_max': min((i + 1) * zone_height, self.grid_height - 1)
            }
            zones.append(zone)
        
        return zones
    
    def get_spawn_position(self, zone_index=None):
        #Отримати випадкову позицію в зоні спавну
        if zone_index is None:
            zone = random.choice(self.spawn_zones)
        else:
            zone = self.spawn_zones[zone_index % len(self.spawn_zones)]
        
        x = random.randint(zone['x_min'], zone['x_max'])
        y = random.randint(zone['y_min'], zone['y_max'])
        return x, y
    
    def update(self, dt):
        #Оновлення таймера хвиль
        self.wave_timer += dt
        
        if not self.wave_active:
            if self.is_first_wave:
                if self.wave_timer >= self.first_wave_delay:
                    return 'start_wave'
            else:
                if self.wave_timer >= self.wave_interval:
                    return 'start_wave'
        
        return None
    
    def spawn_wave(self, all_soldiers, reserved_cells, GridSoldier_class):
        
        self.current_wave += 1
        self.wave_timer = 0
        self.wave_active = True
        
        if self.is_first_wave:
            self.is_first_wave = False
        
        base_count = self.enemy_base_count
        wave_bonus = min(self.current_wave * self.enemy_wave_bonus, 30)
        enemy_count = base_count + wave_bonus + random.randint(-1, 2)
        
        spawned_enemies = []
        
        # СПАВН ВОРОГІВ
        for i in range(enemy_count):
            zone_index = i % len(self.spawn_zones)
            
            attempts = 0
            max_attempts = 30
            
            while attempts < max_attempts:
                spawn_x, spawn_y = self.get_spawn_position(zone_index)
                
                # Перевірка чи вільна клітинка
                if not self._is_cell_occupied(spawn_x, spawn_y, all_soldiers, reserved_cells):
                    task = self._choose_initial_task(i, enemy_count)
                    
                    try:
                        # Створюємо базового солдата
                        soldier = GridSoldier_class(
                            grid_x=spawn_x,
                            grid_y=spawn_y,
                            soldier_type='soldier_bad',
                            team='BAD'
                        )
                        bad_soldier = BadSoldier(
                            soldier, 
                            self.grid_width,
                            self.grid_height,
                            initial_task=task
                        )
                        
                        spawned_enemies.append(bad_soldier)
                        self.total_spawned += 1
                        self.active_enemies += 1
                        
                        if i < 3 or i == enemy_count - 1:  # Показуємо тільки перших 3 і останнього
                            print(f" Ворог #{i+1} створений на ({spawn_x}, {spawn_y})")
                        elif i == 3:
                            print(f"   ... створюємо решту ворогів ...")
                        break
                        
                    except Exception as e:
                        print(f"  Помилка при створенні ворога #{i+1}: {e}")
                        import traceback
                        traceback.print_exc()
                        break
                
                attempts += 1
            
            if attempts >= max_attempts:
                print(f"  Не вдалося знайти місце для ворога #{i+1}")
        
        self.wave_active = False

        return spawned_enemies
    
    def _is_cell_occupied(self, x, y, all_soldiers, reserved_cells): 
        # Перевірка солдатів
        for soldier in all_soldiers:
            if hasattr(soldier, 'soldier'):
                if soldier.soldier.alive and soldier.soldier.grid_x == x and soldier.soldier.grid_y == y:
                    return True
            else:  
                if soldier.alive and soldier.grid_x == x and soldier.grid_y == y:
                    return True
        
        # Перевірка зарезервованих клітинок
        if (x, y) in reserved_cells:
            return True
        
        return False
    
    def _choose_initial_task(self, soldier_index, total_in_wave):
        # Розподіл задач:==================================================================================------------
        # 50% - атакувати
        # 20% - захопити окоп
        # 15% - сховатися в лісі
        # 15% - патрулювати
        
        if soldier_index < total_in_wave * 0.5:
            return BadSoldierAI.TASK_ATTACK_SOLDIER
        elif soldier_index < total_in_wave * 0.7:
            return BadSoldierAI.TASK_CAPTURE_TRENCH
        elif soldier_index < total_in_wave * 0.85:
            return BadSoldierAI.TASK_HIDE_IN_FOREST
        else:
            return BadSoldierAI.TASK_PATROL
    
    def on_enemy_death(self):
        self.active_enemies = max(0, self.active_enemies - 1)
    
    def get_stats(self):
        return {
            'current_wave': self.current_wave,
            'total_spawned': self.total_spawned,
            'active_enemies': self.active_enemies,
            'next_wave_in': max(0, (self.first_wave_delay if self.is_first_wave else self.wave_interval) - self.wave_timer)
        }