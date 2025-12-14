import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
pygame.mixer.init()

try:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WIDTH, HEIGHT = screen.get_size()
    print(f"✓ Fullscreen: {WIDTH}x{HEIGHT}")
except Exception as e:
    print(f"✗ Failed fullscreen: {e}")
    WIDTH, HEIGHT = 1536, 864
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    print(f"✓ Windowed: {WIDTH}x{HEIGHT}")

pygame.display.set_caption("Connect Four")

music_enabled = True
music_volume = 0.3
try:
    pygame.mixer.music.load("music_darrenifyouask_Playing_BPM_174_016.mp3")
    pygame.mixer.music.set_volume(music_volume)
    if music_enabled:
        pygame.mixer.music.play(-1)
except:
    music_enabled = False

try:
    from game import ConnectFourGame
    game = ConnectFourGame(screen, WIDTH, HEIGHT)
    print("Game created successfully!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

clock = pygame.time.Clock()
running = True
bg_x = 0

font_small = pygame.font.SysFont(None, 24)
font_medium = pygame.font.SysFont(None, 28)
font_large = pygame.font.SysFont(None, 36)

COLORS = {
    'panel_bg': (20, 30, 40, 200),
    'panel_border': (52, 152, 219, 150),
    'text': (240, 240, 240),
    'text_muted': (180, 180, 200),
    'highlight': (52, 152, 219),
    'success': (46, 204, 113),
    'warning': (241, 196, 15),
    'error': (231, 76, 60),
    'music': (155, 89, 182)
}

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                game.reset()
                print("Game reset")
            elif event.key == pygame.K_a:
                game.toggle_ai()
                status = "ON" if game.ai_enabled else "OFF"
                print(f"AI {status}")
            elif event.key == pygame.K_v:
                game.toggle_ai_vs_ai()
                status = "ON" if game.ai_vs_ai_mode else "OFF"
                print(f"AI vs AI Mode {status}")
            elif event.key == pygame.K_m:
                music_enabled = not music_enabled
                if music_enabled:
                    pygame.mixer.music.play(-1)
                else:
                    pygame.mixer.music.stop()
                status = "ON" if music_enabled else "OFF"
                print(f"Music {status}")
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                music_volume = min(1.0, music_volume + 0.1)
                pygame.mixer.music.set_volume(music_volume)
                print(f"Volume: {music_volume:.1f}")
            elif event.key == pygame.K_MINUS:
                music_volume = max(0.0, music_volume - 0.1)
                pygame.mixer.music.set_volume(music_volume)
                print(f"Volume: {music_volume:.1f}")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not game.game_over and not game.ai_thinking:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                game.handle_click(mouse_x, mouse_y)

    game.update()
    
    bg_x -= 1
    if bg_x <= -WIDTH:
        bg_x = 0
    
    if hasattr(game, 'bg_image'):
        screen.blit(game.bg_image, (bg_x, 0))
        screen.blit(game.bg_image, (bg_x + WIDTH, 0))
    else:
        screen.fill((30, 30, 50))
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))
    
    game.draw()
    
    status_panel_width = 300
    status_panel_height = 220
    status_panel_x = 20
    status_panel_y = (HEIGHT - status_panel_height) // 2
    
    status_panel = pygame.Surface((status_panel_width, status_panel_height), pygame.SRCALPHA)
    pygame.draw.rect(status_panel, COLORS['panel_bg'], (0, 0, status_panel_width, status_panel_height), 
                    border_radius=15)
    pygame.draw.rect(status_panel, COLORS['panel_border'], (0, 0, status_panel_width, status_panel_height), 
                    3, border_radius=15)
    
    screen.blit(status_panel, (status_panel_x, status_panel_y))
    
    status_title = font_medium.render("GAME STATUS", True, COLORS['highlight'])
    screen.blit(status_title, (status_panel_x + status_panel_width//2 - status_title.get_width()//2, 
                               status_panel_y + 15))
    
    game_status = "PLAYING" if not game.game_over else "GAME OVER"
    status_color = COLORS['success'] if not game.game_over else COLORS['error']
    
    status_line1 = font_small.render(f"Status: {game_status}", True, status_color)
    screen.blit(status_line1, (status_panel_x + 20, status_panel_y + 50))
    
    player_color = COLORS['error'] if game.current_player == 1 else (COLORS['music'] if game.ai_enabled else COLORS['success'])
    current_player = f"Player {game.current_player}"
    if game.game_over:
        current_player = "Game Ended"
        player_color = COLORS['warning']
    
    status_line2 = font_small.render(f"Turn: {current_player}", True, player_color)
    screen.blit(status_line2, (status_panel_x + 20, status_panel_y + 80))
    
    ai_status = "ENABLED" if game.ai_enabled else "DISABLED"
    ai_color = COLORS['success'] if game.ai_enabled else COLORS['text_muted']
    
    status_line3 = font_small.render(f"AI: {ai_status}", True, ai_color)
    screen.blit(status_line3, (status_panel_x + 20, status_panel_y + 110))

    ai_vs_ai_status = "ENABLED" if game.ai_vs_ai_mode else "DISABLED"
    ai_vs_ai_color = (241, 196, 15) if game.ai_vs_ai_mode else COLORS['text_muted']
    
    status_line4 = font_small.render(f"AI vs AI: {ai_vs_ai_status}", True, ai_vs_ai_color)
    screen.blit(status_line4, (status_panel_x + 20, status_panel_y + 140))
    
    music_status = "ON" if music_enabled else "OFF"
    music_status_color = COLORS['music'] if music_enabled else COLORS['text_muted']
    
    status_line5 = font_small.render(f"Music: {music_status}", True, music_status_color)
    screen.blit(status_line5, (status_panel_x + 20, status_panel_y + 170))
    
    controls_panel_width = 300
    controls_panel_height = 250
    controls_panel_x = 20
    controls_panel_y = HEIGHT - controls_panel_height - 20
    
    controls_panel = pygame.Surface((controls_panel_width, controls_panel_height), pygame.SRCALPHA)
    pygame.draw.rect(controls_panel, COLORS['panel_bg'], (0, 0, controls_panel_width, controls_panel_height), 
                    border_radius=15)
    pygame.draw.rect(controls_panel, COLORS['panel_border'], (0, 0, controls_panel_width, controls_panel_height), 
                    3, border_radius=15)
    
    screen.blit(controls_panel, (controls_panel_x, controls_panel_y))
    
    controls_title = font_medium.render("CONTROLS", True, COLORS['highlight'])
    screen.blit(controls_title, (controls_panel_x + controls_panel_width//2 - controls_title.get_width()//2, 
                                 controls_panel_y + 15))
    
    controls_list = [
        {"key": "ESC", "action": "Exit Game", "color": COLORS['error']},
        {"key": "R", "action": "Reset Board", "color": COLORS['warning']},
        {"key": "A", "action": "Toggle AI", "color": COLORS['success']},
        {"key": "V", "action": "AI vs AI", "color": (241, 196, 15)},
        {"key": "M", "action": "Toggle Music", "color": COLORS['music']},
        {"key": "+/-", "action": "Adjust Volume", "color": COLORS['text_muted']},
        {"key": "CLICK", "action": "Make Move", "color": COLORS['highlight']}
    ]
    
    for i, control in enumerate(controls_list):
        y_pos = controls_panel_y + 50 + i * 25
        
        key_text = font_small.render(control["key"], True, control["color"])
        screen.blit(key_text, (controls_panel_x + 20, y_pos))
        
        action_text = font_small.render(f" - {control['action']}", True, COLORS['text'])
        screen.blit(action_text, (controls_panel_x + 70, y_pos))
    
    info_panel_width = 220
    info_panel_height = 90
    info_panel_x = WIDTH - info_panel_width - 20
    info_panel_y = 20
    
    info_panel = pygame.Surface((info_panel_width, info_panel_height), pygame.SRCALPHA)
    pygame.draw.rect(info_panel, COLORS['panel_bg'], (0, 0, info_panel_width, info_panel_height), 
                    border_radius=10)
    pygame.draw.rect(info_panel, COLORS['panel_border'], (0, 0, info_panel_width, info_panel_height), 
                    2, border_radius=10)
    
    screen.blit(info_panel, (info_panel_x, info_panel_y))
    
    screen_info = font_small.render(f"Screen: {WIDTH}x{HEIGHT}", True, COLORS['text_muted'])
    screen.blit(screen_info, (info_panel_x + 15, info_panel_y + 15))
    
    volume_info = font_small.render(f"Volume: {int(music_volume * 100)}%", True, COLORS['text'])
    screen.blit(volume_info, (info_panel_x + 15, info_panel_y + 45))
    
    game_title = font_large.render("CONNECT FOUR", True, (255, 255, 200))
    title_shadow = font_large.render("CONNECT FOUR", True, (100, 100, 100, 150))
    
    screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 3, 33))
    screen.blit(game_title, (WIDTH//2 - game_title.get_width()//2, 30))
    
    pygame.display.update()
    clock.tick(60)

print("Exiting game...")
pygame.quit()
sys.exit()