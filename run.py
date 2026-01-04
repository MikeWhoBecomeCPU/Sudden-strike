import pygame

def show_game_over_screen(screen, game_stats, SCREEN_WIDTH, SCREEN_HEIGHT):
    # Напівпрозорий фон
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((20, 20, 20))
    screen.blit(overlay, (0, 0))
    
    # Шрифти
    title_font = pygame.font.Font(None, 72)
    subtitle_font = pygame.font.Font(None, 48)
    text_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)
    
    y_pos = SCREEN_HEIGHT // 4
    
    # Заголовок
    if game_stats['game_over_reason'] == 'defeat':
        title = title_font.render("ПОРАЗКА", True, (255, 50, 50))
    else:
        title = title_font.render("ПЕРЕМОГА", True, (50, 255, 50))
    
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
    screen.blit(title, title_rect)
    
    y_pos += 100
    
    # Час виживання
    minutes = int(game_stats['survival_time'] // 60)
    seconds = int(game_stats['survival_time'] % 60)
    time_text = subtitle_font.render(
        f"Час виживання: {minutes:02d}:{seconds:02d}",
        True, (0, 0, 0)
    )
    time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
    screen.blit(time_text, time_rect)
    
    y_pos += 80
    
    # Статистика втрат
    ua_survived = game_stats['initial_ua_count'] - game_stats['ua_losses']
    losses_text = text_font.render(
        f"Втрати UA: {game_stats['ua_losses']} з {game_stats['initial_ua_count']}",
        True, (0, 0, 0)
    )
    losses_rect = losses_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
    screen.blit(losses_text, losses_rect)
    
    y_pos += 50
    
    survived_text = text_font.render(
        f"Вижило: {ua_survived}",
        True, (0, 0, 0)
    )
    survived_rect = survived_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
    screen.blit(survived_text, survived_rect)
    
    y_pos += 60
    
    # Статистика ворогів
    enemies_text = text_font.render(
        f"Вбито ворогів: {game_stats['enemies_killed']}",
        True, (0, 0, 0)
    )
    enemies_rect = enemies_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
    screen.blit(enemies_text, enemies_rect)
    
    y_pos += 80
    
    # Розрахунок очків (співвідношення × час)
    if game_stats['ua_losses'] > 0:
        efficiency = game_stats['enemies_killed'] / game_stats['ua_losses']
        points = int(efficiency * game_stats['survival_time'])
        
        efficiency_text = text_font.render(
            f"Співвідношення: {efficiency:.2f}:1",
            True, (0, 0, 0)
        )
        efficiency_rect = efficiency_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        screen.blit(efficiency_text, efficiency_rect)
        y_pos += 50
        
        # Очки (великим шрифтом)
        points_text = subtitle_font.render(
            f"Поінти: {points}",
            True, (255, 215, 0)
        )
        points_rect = points_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        screen.blit(points_text, points_rect)
        y_pos += 70
    
    # Підказка виходу
    exit_text = small_font.render(
        "Натисніть ESC для виходу",
        True, (0, 0, 0)
    )
    exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
    screen.blit(exit_text, exit_rect)


def run_game_loop(game_data):
    screen = game_data['screen']
    clock = game_data['clock']
    
    # Константи
    CELL_SIZE = game_data['CELL_SIZE']
    GRID_WIDTH = game_data['GRID_WIDTH']
    GRID_HEIGHT = game_data['GRID_HEIGHT']
    WORLD_WIDTH = game_data['WORLD_WIDTH']
    WORLD_HEIGHT = game_data['WORLD_HEIGHT']
    SCROLL_SPEED = game_data['SCROLL_SPEED']
    SCREEN_WIDTH = game_data['SCREEN_WIDTH']
    SCREEN_HEIGHT = game_data['SCREEN_HEIGHT']
    # Графіка
    background_image = game_data['background_image']
    world_objects = game_data['world_objects']
    OBJECT_TYPES = game_data['OBJECT_TYPES']
    
    # Ігрові об'єкти
    all_soldiers = game_data['all_soldiers']
    shooting_effects = game_data['shooting_effects']
    reserved_cells = game_data['reserved_cells']
    forest_matrix = game_data['forest_matrix']
    trench_matrix = game_data['trench_matrix']
    
    # Функції
    find_random_path = game_data['find_random_path']
    draw_grid = game_data['draw_grid']
    GridSoldier = game_data['GridSoldier']
    # Система хвиль
    wave_spawner = game_data['wave_spawner']
    bad_soldiers = game_data['bad_soldiers']
    
    # СТАТИСТИКА ГРИ
    game_stats = game_data.get('game_stats', {
        'start_time': pygame.time.get_ticks(),
        'initial_ua_count': len([s for s in all_soldiers if s.team == 'UA']),
        'ua_losses': 0,
        'enemies_killed': 0,
        'game_over': False,
        'game_over_reason': '',
        'survival_time': 0
    })
    
    # Стан гри
    camera_x = 0
    camera_y = 0
    running = True
    show_grid = False
    mouse_drag_start = None
    
    selected_soldier = None
    selected_soldiers = []
    
    frame_count = 0
    
    # ========================================================================
    # ГОЛОВНИЙ ЦИКЛ
    
    while running:
        dt = clock.tick(60) / 1000.0
        frame_count += 1
        
        # ====================================================================
        # ПЕРЕВІРКА СТАТИСТИКИ ТА УМОВ ЗАВЕРШЕННЯ
        
        # Підрахунок живих UA солдатів
        current_ua_alive = len([s for s in all_soldiers if s.team == 'UA' and s.alive])
        ua_dead = game_stats['initial_ua_count'] - current_ua_alive
        
        # Оновлюємо втрати UA
        if ua_dead > game_stats['ua_losses']:
            game_stats['ua_losses'] = ua_dead

        # Підрахунок вбитих ворогів
        enemies_dead = len([bs for bs in bad_soldiers if not bs.soldier.alive])
        if enemies_dead > game_stats['enemies_killed']:
            game_stats['enemies_killed'] = enemies_dead
            print(f"☠️ Вбито ворогів: {game_stats['enemies_killed']}")
        
        # ПЕРЕВІРКА ПРОГРАШУ (всі UA мертві)
        if current_ua_alive == 0 and not game_stats['game_over']:
            game_stats['game_over'] = True
            game_stats['game_over_reason'] = 'defeat'
            current_time = pygame.time.get_ticks()
            game_stats['survival_time'] = (current_time - game_stats['start_time']) / 1000
        
        # ВІДОБРАЖЕННЯ ЕКРАНУ ЗАВЕРШЕННЯ
        if game_stats['game_over']:
            # Малюємо останній кадр гри
            if background_image:
                screen.blit(background_image, (-camera_x, -camera_y))
            
            if show_grid:
                draw_grid(screen, camera_x, camera_y)
            
            for obj in world_objects:
                draw_x = obj['x'] - camera_x
                draw_y = obj['y'] - camera_y
                image_to_draw = OBJECT_TYPES[obj['type']]['image']
                screen.blit(image_to_draw, (draw_x, draw_y))
            
            for soldier in all_soldiers:
                try:
                    soldier.draw(screen, camera_x, camera_y)
                except Exception as e:
                    pass
            
            for effect in shooting_effects:
                effect.draw(screen, camera_x, camera_y)
            
            # Показуємо екран Game Over поверх
            show_game_over_screen(screen, game_stats, SCREEN_WIDTH, SCREEN_HEIGHT)
            pygame.display.flip()
            
            # Чекаємо на натискання клавіші
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return True
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                            return True
                clock.tick(30)
        
        # ====================================================================
        # ОБРОБКА ПОДІЙ
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    running = False
                if event.key == pygame.K_g:
                    show_grid = not show_grid
                if event.key == pygame.K_d:
                    # Зупинка виділених солдатів
                    for soldier in selected_soldiers:
                        if soldier.is_controllable():
                            soldier.stop_moving()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # ЛКМ
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_x = mouse_x + camera_x
                world_y = mouse_y + camera_y
                clicked_grid_x = int(world_x // CELL_SIZE)
                clicked_grid_y = int(world_y // CELL_SIZE)
                
                clicked_soldier = None
                for soldier in all_soldiers:
                    if soldier.grid_x == clicked_grid_x and soldier.grid_y == clicked_grid_y:
                        if soldier.is_visible():
                            clicked_soldier = soldier
                            break
                
                keys = pygame.key.get_pressed()
                
                if clicked_soldier:
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        # Групове виділення з Shift
                        if clicked_soldier not in selected_soldiers:
                            clicked_soldier.selected = True
                            selected_soldiers.append(clicked_soldier)
                        else:
                            clicked_soldier.selected = False
                            selected_soldiers.remove(clicked_soldier)
                    else:
                        # Звичайне виділення
                        for soldier in selected_soldiers:
                            soldier.selected = False
                        selected_soldiers = [clicked_soldier]
                        clicked_soldier.selected = True
                    
                    selected_soldier = clicked_soldier if len(selected_soldiers) == 1 else None
                else:
                    # Клік по порожньому місцю
                    for soldier in selected_soldiers:
                        soldier.selected = False
                    selected_soldiers = []
                    selected_soldier = None
                    mouse_drag_start = (mouse_x, mouse_y)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # ПКМ
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_x = mouse_x + camera_x
                world_y = mouse_y + camera_y
                clicked_grid_x = int(world_x // CELL_SIZE)
                clicked_grid_y = int(world_y // CELL_SIZE)
                
                controllable_soldiers = [s for s in selected_soldiers if s.is_controllable()]
                
                if controllable_soldiers:
                    if len(controllable_soldiers) == 1:
                        # Один солдат
                        path = find_random_path(
                            controllable_soldiers[0].grid_x, 
                            controllable_soldiers[0].grid_y,
                            clicked_grid_x, 
                            clicked_grid_y
                        )
                        if path:
                            controllable_soldiers[0].set_path(path)
                    else:
                        # Група - строєм
                        center_x = sum(s.grid_x for s in controllable_soldiers) / len(controllable_soldiers)
                        center_y = sum(s.grid_y for s in controllable_soldiers) / len(controllable_soldiers)
                        
                        offset_x = clicked_grid_x - center_x
                        offset_y = clicked_grid_y - center_y
                        
                        for soldier in controllable_soldiers:
                            target_x = int(soldier.grid_x + offset_x)
                            target_y = int(soldier.grid_y + offset_y)
                            
                            target_x = max(0, min(target_x, GRID_WIDTH - 1))
                            target_y = max(0, min(target_y, GRID_HEIGHT - 1))
                            
                            path = find_random_path(
                                soldier.grid_x, 
                                soldier.grid_y,
                                target_x, 
                                target_y
                            )
                            if path:
                                soldier.set_path(path)
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if mouse_drag_start:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    drag_distance = ((mouse_x - mouse_drag_start[0])**2 + (mouse_y - mouse_drag_start[1])**2)**0.5
                    
                    if drag_distance > 5:
                        # Рамка виділення
                        x1 = min(mouse_drag_start[0], mouse_x) + camera_x
                        y1 = min(mouse_drag_start[1], mouse_y) + camera_y
                        x2 = max(mouse_drag_start[0], mouse_x) + camera_x
                        y2 = max(mouse_drag_start[1], mouse_y) + camera_y
                        
                        keys = pygame.key.get_pressed()
                        
                        if not (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
                            for soldier in selected_soldiers:
                                soldier.selected = False
                            selected_soldiers = []
                        
                        for soldier in all_soldiers:
                            if not soldier.is_visible():
                                continue
                            
                            soldier_x = soldier.x
                            soldier_y = soldier.y
                            if x1 <= soldier_x <= x2 and y1 <= soldier_y <= y2:
                                if soldier not in selected_soldiers:
                                    soldier.selected = True
                                    selected_soldiers.append(soldier)
                        
                        selected_soldier = selected_soldiers[0] if len(selected_soldiers) == 1 else None
                    
                    mouse_drag_start = None

        # ====================================================================
        # ОНОВЛЕННЯ
        
        # === ХВИЛЬОВИЙ СПАВН - ВСЕ ОДРАЗУ ===
        wave_status = wave_spawner.update(dt)
        
        if wave_status == 'start_wave':
            try:
                # Спавн всієї хвилі одразу
                new_enemies = wave_spawner.spawn_wave(all_soldiers, reserved_cells, GridSoldier)
                
                for bad_soldier in new_enemies:
                    all_soldiers.append(bad_soldier.soldier)
                    bad_soldiers.append(bad_soldier)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
        
        # === ОНОВЛЕННЯ СОЛДАТІВ ===
        ua_soldiers = [s for s in all_soldiers if s.team == 'UA']
        
        # Звичайні солдати UA
        for soldier in all_soldiers:
            if soldier.team == 'UA':
                try:
                    soldier.update(dt, all_soldiers)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
        
        # Вороги з AI
        for i, bad_soldier in enumerate(bad_soldiers):
            try:
                # Оновлюємо AI тільки для живих
                if bad_soldier.soldier.alive:
                    bad_soldier.update_ai(dt, ua_soldiers, forest_matrix, trench_matrix, all_soldiers)
                
                # Оновлюємо солдата (в т.ч. мертвих для анімації)
                bad_soldier.soldier.update(dt, all_soldiers)
                
                # Повідомляємо про смерть тільки один раз
                if not bad_soldier.soldier.alive and not hasattr(bad_soldier, '_death_reported'):
                    bad_soldier._death_reported = True
                    wave_spawner.on_enemy_death()
                    print(f"Ворог вбитий! Залишилось: {wave_spawner.active_enemies}")
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                # Видаляємо проблемного ворога
                bad_soldiers.remove(bad_soldier)
                if bad_soldier.soldier in all_soldiers:
                    all_soldiers.remove(bad_soldier.soldier)
        
        # Ефекти пострілів
        shooting_effects[:] = [effect for effect in shooting_effects if effect.active]
        for effect in shooting_effects:
            effect.update(dt)

        # ====================================================================
        # КАМЕРА
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        if mouse_x < 20: 
            camera_x -= SCROLL_SPEED
        if mouse_x > SCREEN_WIDTH - 20: 
            camera_x += SCROLL_SPEED
        if mouse_y < 20: 
            camera_y -= SCROLL_SPEED
        if mouse_y > SCREEN_HEIGHT - 20: 
            camera_y += SCROLL_SPEED
            
        camera_x = max(0, min(camera_x, WORLD_WIDTH - SCREEN_WIDTH))
        camera_y = max(0, min(camera_y, WORLD_HEIGHT - SCREEN_HEIGHT))

        # ====================================================================
        # МАЛЮВАННЯ
        
        # Фон
        if background_image:
            screen.blit(background_image, (-camera_x, -camera_y)) 

        # Сітка
        if show_grid:
            draw_grid(screen, camera_x, camera_y)

        # Об'єкти світу
        for obj in world_objects:
            draw_x = obj['x'] - camera_x
            draw_y = obj['y'] - camera_y
            image_to_draw = OBJECT_TYPES[obj['type']]['image']
            screen.blit(image_to_draw, (draw_x, draw_y))
        
        # Солдати (в т.ч. мертві - для анімації смерті)
        for soldier in all_soldiers:
            try:
                soldier.draw(screen, camera_x, camera_y)
            except Exception as e:
                import traceback
                traceback.print_exc()
        
        # Ефекти
        for effect in shooting_effects:
            effect.draw(screen, camera_x, camera_y)
        
        # Рамка виділення
        if mouse_drag_start:
            current_mouse = pygame.mouse.get_pos()
            rect_x = min(mouse_drag_start[0], current_mouse[0])
            rect_y = min(mouse_drag_start[1], current_mouse[1])
            rect_w = abs(current_mouse[0] - mouse_drag_start[0])
            rect_h = abs(current_mouse[1] - mouse_drag_start[1])
            
            selection_surface = pygame.Surface((rect_w, rect_h), pygame.SRCALPHA)
            selection_surface.fill((0, 255, 0, 50))
            screen.blit(selection_surface, (rect_x, rect_y))
            pygame.draw.rect(screen, (0, 255, 0), (rect_x, rect_y, rect_w, rect_h), 2)
        
        # ====================================================================
        # UI З ПОВНОЮ СТАТИСТИКОЮ
        font = pygame.font.Font(None, 24)
        
        # Підказки
        help_text = font.render(
            "G - Сітка | D - stop | LKM - Вибір | PKM - Рух | Shift - Додати до групи | ESC - Вихід", 
            True, (255, 255, 255)
        )
        screen.blit(help_text, (10, 10))
        
        # Статистика хвиль
        stats = wave_spawner.get_stats()
        current_time = (pygame.time.get_ticks() - game_stats['start_time']) / 1000
        minutes = int(current_time // 60)
        seconds = int(current_time % 60)
        
        wave_text = font.render(
            f"Волна: {stats['current_wave']} | Ворогів: {stats['active_enemies']} | "
            f"Наступна хвиля: {int(stats['next_wave_in'])}s",
            True, (255, 100, 100)
        )
        screen.blit(wave_text, (10, 40))
        
        # Втрати та вбиті вороги
        losses_text = font.render(
            f"UA: {current_ua_alive}/{game_stats['initial_ua_count']} "
            f"(Втрат: {game_stats['ua_losses']}) | "
            f"Вбито: {game_stats['enemies_killed']}",
            True, (100, 255, 100)
        )
        screen.blit(losses_text, (10, 70))
        
        # Час виживання
        time_text = font.render(
            f"Час: {minutes:02d}:{seconds:02d}",
            True, (255, 255, 100)
        )
        screen.blit(time_text, (10, 100))
        
        # Інформація про виділених
        if selected_soldiers:
            controllable = len([s for s in selected_soldiers if s.is_controllable()])
            total = len(selected_soldiers)
            alive = len([s for s in selected_soldiers if s.alive])
            
            if controllable < total:
                count_text = font.render(
                    f"Обрано: {total} (Живих: {alive}, Керованих: {controllable})", 
                    True, (255, 255, 0)
                )
            else:
                count_text = font.render(
                    f"Обрано: {total} (Живих: {alive})", 
                    True, (255, 255, 0)
                )
            screen.blit(count_text, (10, 130))
        
        # ВІДОБРАЖАЄМО КАДР
        pygame.display.flip()
    return True