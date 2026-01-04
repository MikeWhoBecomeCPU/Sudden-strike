import random

class BadSoldierAI:

    TASK_ATTACK_SOLDIER = "attack_soldier"
    TASK_CAPTURE_TRENCH = "capture_trench"
    TASK_HIDE_IN_FOREST = "hide_in_forest"
    TASK_WAIT = "wait"
    TASK_PATROL = "patrol"
    
    def __init__(self, soldier, grid_width, grid_height, initial_task=None):
        self.soldier = soldier
        self.grid_width = grid_width
        self.grid_height = grid_height
        
        self.current_task = initial_task or self.TASK_ATTACK_SOLDIER
        self.task_target = None
        self.task_timer = 0
        self.wait_duration = 0
        self.patrol_points = []
        self.patrol_index = 0
        
        # Налаштунки поведінки 
        self.aggression = random.uniform(0.6, 1.0)    # Агресивність
        self.caution = random.uniform(0.3, 0.8)       # Обережність
        self.intelligence = random.uniform(0.5, 1.0)  # "Розум" 
        
        self.decision_cooldown = 0
        self.stuck_timer = 0
        self.last_position = (soldier.grid_x, soldier.grid_y)
        
        # Пам'ять про ворогів
        self.last_seen_enemy = None
        self.last_enemy_position = None
    
    def set_task(self, task_type, target=None, duration=0):
        self.current_task = task_type
        self.task_target = target
        self.task_timer = 0
        self.wait_duration = duration
        
        if task_type == self.TASK_WAIT:
            self.soldier.stop_moving()
    
    def update(self, dt, ua_soldiers, forest_matrix, trench_matrix, all_soldiers):
        if not self.soldier.alive:
            return
        
        self.task_timer += dt
        self.decision_cooldown -= dt
        
        # Перевірка на застрягання
        current_pos = (self.soldier.grid_x, self.soldier.grid_y)
        if current_pos == self.last_position and self.soldier.is_moving:
            self.stuck_timer += dt
            if self.stuck_timer > 3.0:
                self._handle_stuck()
        else:
            self.stuck_timer = 0
        self.last_position = current_pos
        
        # Виконання поточної задачі
        if self.current_task == self.TASK_WAIT:
            self._task_wait(dt)
        elif self.current_task == self.TASK_ATTACK_SOLDIER:
            self._task_attack_soldier(ua_soldiers, all_soldiers)
        elif self.current_task == self.TASK_CAPTURE_TRENCH:
            self._task_capture_trench(trench_matrix)
        elif self.current_task == self.TASK_HIDE_IN_FOREST:
            self._task_hide_in_forest(forest_matrix)
        elif self.current_task == self.TASK_PATROL:
            self._task_patrol()
        
        # Періодична переоцінка ситуації (частота залежить від "інтелекту")
        if self.decision_cooldown <= 0:
            self._reassess_situation(ua_soldiers, forest_matrix, trench_matrix)
            self.decision_cooldown = random.uniform(1.5, 4.0) / self.intelligence
    
    # ========================================================================
    # ЗАДАЧІ
    
    def _task_wait(self, dt):
        #Задача: чекати
        if self.task_timer >= self.wait_duration:
            self._choose_random_task()
    
    def _task_attack_soldier(self, ua_soldiers, all_soldiers):
        #Задача: атакувати конкретного солдата
        alive_ua = [s for s in ua_soldiers if s.alive]
        
        if not alive_ua:
            self._choose_random_task()
            return
        
        # Якщо немає цілі або ціль мертва
        if not self.task_target or not self.task_target.alive:
            self.task_target = self._choose_target(alive_ua)
            if self.task_target:
                self.last_seen_enemy = self.task_target
                self.last_enemy_position = (self.task_target.grid_x, self.task_target.grid_y)
        
        # Якщо солдат не рухається, оновлюємо шлях до цілі
        if not self.soldier.is_moving and self.task_target:
            target_x = self.task_target.grid_x
            target_y = self.task_target.grid_y
            
            # Якщо ціль далеко, йдемо до неї
            distance = abs(self.soldier.grid_x - target_x) + abs(self.soldier.grid_y - target_y)
            
            if distance > 3:
                self._move_to(target_x, target_y)
            elif distance <= 1:
                # А якщо дужже близько - можливо відступити трохи назад
                if self.soldier.hp < 50 and random.random() < 0.3:
                    retreat_x = self.soldier.grid_x + (1 if target_x < self.soldier.grid_x else -1)
                    retreat_y = self.soldier.grid_y + (1 if target_y < self.soldier.grid_y else -1)
                    retreat_x = max(0, min(retreat_x, self.grid_width - 1))
                    retreat_y = max(0, min(retreat_y, self.grid_height - 1))
                    self._move_to(retreat_x, retreat_y)
    
    def _task_capture_trench(self, trench_matrix):
        #Задача - захопити окоп
        if not self.task_target:
            trench_pos = self._find_nearest_trench(trench_matrix)
            if trench_pos:
                self.task_target = trench_pos
            else:
                self._choose_random_task()
                return
        
        if not self.soldier.is_moving:
            tx, ty = self.task_target
            if self.soldier.grid_x == tx and self.soldier.grid_y == ty:
                # Досягли окопу - залишаємося або змінюємо задачу
                if random.random() < 0.4:
                    self.set_task(self.TASK_WAIT, duration=random.uniform(10, 30))
                else:
                    self._choose_random_task()
            else:
                self._move_to(tx, ty)
    
    def _task_hide_in_forest(self, forest_matrix):
        #адача: сховатися в лісі
        if self.soldier.in_forest:
            # Вже в лісі - іноді вибираємо нову задачу
            if random.random() < 0.05:
                self._choose_random_task()
            return
        
        if not self.task_target:
            forest_pos = self._find_nearest_forest(forest_matrix)
            if forest_pos:
                self.task_target = forest_pos
            else:
                self._choose_random_task()
                return
        
        if not self.soldier.is_moving:
            fx, fy = self.task_target
            self._move_to(fx, fy)
    
    def _task_patrol(self):
        #Задача- патрулювати між точками
        if not self.patrol_points:
            self.patrol_points = self._generate_patrol_points()
        
        if not self.soldier.is_moving and self.patrol_points:
            target = self.patrol_points[self.patrol_index]
            self._move_to(target[0], target[1])
            
            # Якщо досягли точки, переходимо до наступної
            if (self.soldier.grid_x, self.soldier.grid_y) == target:
                self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
    
    # ========================================================================
    # ДОПОМІЖНІ ФУНКЦІЇ
    
    def _choose_target(self, ua_soldiers):
        #Вибрати ціль для атаки 
        if not ua_soldiers:
            return None
        
        visible = [s for s in ua_soldiers if s.is_visible()]
        
        if not visible:
            # Якщо нікого не видно, йдемо до останньої відомої позиції
            if self.last_enemy_position and random.random() < 0.7:
                return self.last_seen_enemy if self.last_seen_enemy and self.last_seen_enemy.alive else random.choice(ua_soldiers)
            return random.choice(ua_soldiers)
        
        # Вибираємо ціль залежно від агресивності
        if self.aggression > 0.8:
            # Дуже агресивні - атакують найслабшого
            target = min(visible, key=lambda s: s.hp)
        elif self.aggression > 0.5:
            # Помірно агресивні - атакують найближчого
            target = min(visible, key=lambda s: 
                abs(s.grid_x - self.soldier.grid_x) + abs(s.grid_y - self.soldier.grid_y))
        else:
            # Обережні - атакують випадкового
            target = random.choice(visible)
        
        return target
    
    def _find_nearest_trench(self, trench_matrix):
        #Знайти найближчий окоп
        min_dist = float('inf')
        best_pos = None
        
        # Шукаємо з кроком для оптимізації
        for y in range(0, self.grid_height, 2):
            for x in range(0, self.grid_width, 2):
                if trench_matrix[y][x]:
                    dist = abs(x - self.soldier.grid_x) + abs(y - self.soldier.grid_y)
                    if dist < min_dist:
                        min_dist = dist
                        best_pos = (x, y)
        
        return best_pos
    
    def _find_nearest_forest(self, forest_matrix):
        #Знайти найближчий ліс
        min_dist = float('inf')
        best_pos = None
        
        for y in range(0, self.grid_height, 2):
            for x in range(0, self.grid_width, 2):
                if forest_matrix[y][x]:
                    dist = abs(x - self.soldier.grid_x) + abs(y - self.soldier.grid_y)
                    if dist < min_dist:
                        min_dist = dist
                        best_pos = (x, y)
        
        return best_pos
    
    def _generate_patrol_points(self):
        #Створити точки патрулювання
        points = []
        num_points = random.randint(3, 5)
        
        # Генеруємо точки в правій половині карти
        for _ in range(num_points):
            x = random.randint(self.grid_width // 2, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            points.append((x, y))
        
        return points
    
    def _move_to(self, target_x, target_y):
        #Відправити солдата до цілі
        path = []
        current_x = self.soldier.grid_x
        current_y = self.soldier.grid_y
        
        # Випадковий вибір: спочатку X або Y
        if random.random() < 0.5:
            # Спочатку рухаємося по X
            while current_x != target_x:
                if current_x < target_x:
                    current_x += 1
                else:
                    current_x -= 1
                path.append((current_x, current_y))
            
            # Потім по Y
            while current_y != target_y:
                if current_y < target_y:
                    current_y += 1
                else:
                    current_y -= 1
                path.append((current_x, current_y))
        else:
            # Спочатку рухаємося по Y
            while current_y != target_y:
                if current_y < target_y:
                    current_y += 1
                else:
                    current_y -= 1
                path.append((current_x, current_y))
            
            # Потім по X
            while current_x != target_x:
                if current_x < target_x:
                    current_x += 1
                else:
                    current_x -= 1
                path.append((current_x, current_y))
        
        if path:
            self.soldier.set_path(path)
    
    def _reassess_situation(self, ua_soldiers, forest_matrix, trench_matrix):
        if self.soldier.hp < 30 * self.caution:
            if not self.soldier.in_forest:
                self.set_task(self.TASK_HIDE_IN_FOREST)
                return
        if self.soldier.in_trench and self.soldier.hp < 70:
            if self.current_task != self.TASK_WAIT:
                self.set_task(self.TASK_WAIT, duration=random.uniform(5, 15))
                return

        if self.current_task == self.TASK_WAIT and self.task_timer > 20:
            self._choose_random_task()
            return
        
        nearby_enemies = [s for s in ua_soldiers if s.alive and 
                         abs(s.grid_x - self.soldier.grid_x) + abs(s.grid_y - self.soldier.grid_y) < 5]
        
        if len(nearby_enemies) > 3 and self.soldier.hp < 60:
            if random.random() < 0.4:
                self.set_task(self.TASK_HIDE_IN_FOREST)
                return
    
    def _handle_stuck(self):
        #Обробка застрягання
        #print(f" Солдат BAD застряг на ({self.soldier.grid_x}, {self.soldier.grid_y})")
        self.soldier.stop_moving()
        self.stuck_timer = 0
        self._choose_random_task()
    
    def _choose_random_task(self):
        # залежать від агресивності солдата
        attack_weight = 0.3 + self.aggression * 0.3
        hide_weight = 0.1 + self.caution * 0.2
        
        tasks = [
            (self.TASK_ATTACK_SOLDIER, attack_weight),
            (self.TASK_CAPTURE_TRENCH, 0.2),
            (self.TASK_HIDE_IN_FOREST, hide_weight),
            (self.TASK_WAIT, 0.1),
            (self.TASK_PATROL, 0.1)
        ]
        
        total_weight = sum(w for _, w in tasks)
        tasks = [(t, w/total_weight) for t, w in tasks]
        
        rand = random.random()
        cumulative = 0
        
        for task, probability in tasks:
            cumulative += probability
            if rand <= cumulative:
                if task == self.TASK_WAIT:
                    self.set_task(task, duration=random.uniform(20, 60))
                else:
                    self.set_task(task)
                    self.task_target = None
                break


class BadSoldier:
    def __init__(self, base_soldier, grid_width, grid_height, initial_task=None):

        self.soldier = base_soldier
        self.ai = BadSoldierAI(base_soldier, grid_width, grid_height, initial_task)
        
        # Відкладена ініціалізація (щоб не всі солдати рухалися одночасно)
        self.initialization_delay = random.uniform(0.1, 0.5)
        self.initialized = False
    
    def update_ai(self, dt, ua_soldiers, forest_matrix, trench_matrix, all_soldiers):
        
        if not self.soldier.alive:
            return
        
        # Відкладена ініціалізація
        if not self.initialized:
            self.initialization_delay -= dt
            if self.initialization_delay <= 0:
                self.initialized = True
            else:
                return
        
        # Оновлюємо AI
        try:
            self.ai.update(dt, ua_soldiers, forest_matrix, trench_matrix, all_soldiers)
        except Exception as e:
            print(f"Помилка в AI солдата на ({self.soldier.grid_x}, {self.soldier.grid_y}): {e}")