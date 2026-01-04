import pygame
import sys

def show_main_menu(screen, clock):
    
    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()
    
    # Шрифти
    title_font = pygame.font.Font(None, 72)
    option_font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)
    
    # Кольори
    BG_COLOR = (20, 20, 30)
    TITLE_COLOR = (255, 215, 0)
    TEXT_COLOR = (200, 200, 200)
    SELECTED_COLOR = (255, 255, 100)
    BUTTON_COLOR = (50, 50, 70)
    BUTTON_HOVER = (70, 70, 100)
    
    # Налаштування
    settings = {
        'mode': 'normal',
        'ua_count': 30,
        'enemy_base': 5,
        'enemy_bonus': 3
    }
    
    # Опції меню
    modes = [
        {'name': 'Легкий', 'ua': 50, 'enemy_base': 3, 'enemy_bonus': 2},
        {'name': 'Нормальний', 'ua': 30, 'enemy_base': 5, 'enemy_bonus': 3},
        {'name': 'Важкий', 'ua': 20, 'enemy_base': 8, 'enemy_bonus': 5},
        {'name': 'Пекло', 'ua': 15, 'enemy_base': 12, 'enemy_bonus': 8},
    ]
    
    selected_mode = 1  # Нормальний за замовчуванням
    
    # Кнопки
    button_start = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 150, 300, 60)
    button_exit = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 70, 300, 60)
    
    running = True
    
    while running:
        screen.fill(BG_COLOR)
        
        # Заголовок
        title_text = title_font.render("БИТВА ЗА УКРАЇНУ", True, TITLE_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title_text, title_rect)
        
        # Підзаголовок
        subtitle_text = small_font.render("Оберіть складність", True, TEXT_COLOR)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Режими гри
        y_offset = 240
        for i, mode in enumerate(modes):
            color = SELECTED_COLOR if i == selected_mode else TEXT_COLOR
            
            mode_text = option_font.render(f"{mode['name']}", True, color)
            mode_rect = mode_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(mode_text, mode_rect)
            
            if i == selected_mode:
                # Показуємо деталі вибраного режиму
                details = [
                    f"UA солдатів: {mode['ua']}",
                    f"Ворогів (база): {mode['enemy_base']}",
                    f"Приріст за хвилю: +{mode['enemy_bonus']}"
                ]
                
                detail_y = y_offset + 50
                for detail in details:
                    detail_text = small_font.render(detail, True, (150, 150, 150))
                    detail_rect = detail_text.get_rect(center=(SCREEN_WIDTH // 2, detail_y))
                    screen.blit(detail_text, detail_rect)
                    detail_y += 35
            
            y_offset += 150
        
        # Кнопки
        mouse_pos = pygame.mouse.get_pos()
        
        # Кнопка "Почати гру"
        if button_start.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER, button_start, border_radius=10)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, button_start, border_radius=10)
        pygame.draw.rect(screen, TEXT_COLOR, button_start, 2, border_radius=10)
        
        start_text = option_font.render("Почати гру", True, TEXT_COLOR)
        start_rect = start_text.get_rect(center=button_start.center)
        screen.blit(start_text, start_rect)
        
        # Кнопка "Вийти"
        if button_exit.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER, button_exit, border_radius=10)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, button_exit, border_radius=10)
        pygame.draw.rect(screen, TEXT_COLOR, button_exit, 2, border_radius=10)
        
        exit_text = option_font.render("Вийти", True, TEXT_COLOR)
        exit_rect = exit_text.get_rect(center=button_exit.center)
        screen.blit(exit_text, exit_rect)
        
        # Інструкції
        instructions = [
            "↑↓ - Вибір режиму",
            "Enter - Почати гру",
            "Esc - Вийти"
        ]
        
        instr_y = SCREEN_HEIGHT - 250
        for instr in instructions:
            instr_text = small_font.render(instr, True, (100, 100, 100))
            instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH // 2, instr_y))
            screen.blit(instr_text, instr_rect)
            instr_y += 30
        pygame.display.flip()

        # Обробка подій
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                
                elif event.key == pygame.K_UP:
                    selected_mode = (selected_mode - 1) % len(modes)
                
                elif event.key == pygame.K_DOWN:
                    selected_mode = (selected_mode + 1) % len(modes)
                
                elif event.key == pygame.K_RETURN:
                    mode_data = modes[selected_mode]
                    return {
                        'mode': mode_data['name'],
                        'ua_count': mode_data['ua'],
                        'enemy_base': mode_data['enemy_base'],
                        'enemy_bonus': mode_data['enemy_bonus']
                    }
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if button_start.collidepoint(mouse_pos):
                        mode_data = modes[selected_mode]
                        return {
                            'mode': mode_data['name'],
                            'ua_count': mode_data['ua'],
                            'enemy_base': mode_data['enemy_base'],
                            'enemy_bonus': mode_data['enemy_bonus']
                        }
                    
                    elif button_exit.collidepoint(mouse_pos):
                        return None
        
        clock.tick(60)
    
    return None