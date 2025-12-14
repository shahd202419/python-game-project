import pygame
import numpy as np
import threading
import time
from algorithm import HybridAI
class ConnectFourGame:
    def __init__(self, screen, width, height, use_ai=True):
        self.screen = screen
        self.WIDTH = width
        self.HEIGHT = height
        
        # backdround
        try:
            self.bg_image = pygame.image.load("pp2.jpg")
            self.bg_image = pygame.transform.scale(self.bg_image, (width, height))
        except:
            self.bg_image = None
        

        self.ROWS = 6
        self.COLS = 7
        self.board = np.zeros((self.ROWS, self.COLS), dtype=int)
        self.heights = [0] * self.COLS
        self.current_player = 1
        self.game_over = False
        self.winner = 0
        self.moves_count = 0
        self.history = []
        
        # AI
        self.ai_enabled = use_ai
        self.ai_thinking = False
        self.ai_move_pending = False
        self.ai_move_column = None
        self.ai_move_time = 0
        self.ai_delay = 0
        self.ai_thread = None
        
        # AI VS AI
        self.ai_vs_ai_mode = False
        self.ai_vs_ai_speed = 0.8  
        self.ai_vs_ai_thread = None
        self.ai_vs_ai_running = False
        
        if self.ai_enabled:
            self.ai = HybridAI(player_number=2, max_depth=4, use_threading=False)           
            self.ai_player1 = HybridAI(player_number=1, max_depth=4,use_threading=False)
            self.ai_player2 = HybridAI(player_number=2, max_depth=4,use_threading=False)
        
        self.grid_width = min(700, width * 0.8)
        self.grid_height = self.grid_width * 0.75
        self.grid_x = (width - self.grid_width) // 2
        self.grid_y = (height - self.grid_height) // 2
        
        self.cell_width = self.grid_width // self.COLS
        self.cell_height = self.grid_height // self.ROWS
        self.hole_radius = self.cell_width // 2 - 10
        

        self.colors = {
            'grid_bg': (41, 128, 185),
            'hole_bg': (26, 82, 118),
            'player1': (231, 76, 60),
            'player2': (46, 204, 113),
            'ai': (155, 89, 182),
            'ai_vs_ai': (241, 196, 15),  
            'text': (255, 255, 255)
        }

    def reset(self):
        self.board = np.zeros((self.ROWS, self.COLS), dtype=int)
        self.heights = [0] * self.COLS
        self.current_player = 1
        self.game_over = False
        self.winner = 0
        self.moves_count = 0
        self.history = []
        self.ai_thinking = False
        self.ai_move_pending = False
        self.ai_move_column = None
        
        if self.ai_vs_ai_mode and self.ai_vs_ai_running:
            self.start_ai_vs_ai()
    
    def toggle_ai(self):
        
        self.ai_enabled = not self.ai_enabled
        if self.ai_enabled and not hasattr(self, 'ai'):
            self.ai = HybridAI(player_number=2, max_depth=4,use_threading=False)
        elif not self.ai_enabled:
            self.ai_thinking = False
            self.ai_move_pending = False

    def make_move(self, col):
        
        if self.game_over or self.heights[col] >= self.ROWS:
            return False
        
        row = self.ROWS - 1 - self.heights[col]
        self.board[row][col] = self.current_player
        self.heights[col] += 1
        self.moves_count += 1
        
        self.history.append({
            'col': col,
            'row': row,
            'player': self.current_player
        })
        
        
        if self.check_winner(self.current_player):
            self.game_over = True
            self.winner = self.current_player
        elif self.moves_count == self.ROWS * self.COLS:
            self.game_over = True
            self.winner = -1  
        else:
            self.current_player = 3 - self.current_player
            
            if not self.ai_vs_ai_mode:
                if self.ai_enabled and self.current_player == 2 and not self.game_over:
                    self.start_ai_thinking()
        
        return True
    
    def check_winner(self, player):
        
        for r in range(self.ROWS):
            for c in range(self.COLS - 3):
                if (self.board[r][c] == player and 
                    self.board[r][c+1] == player and 
                    self.board[r][c+2] == player and 
                    self.board[r][c+3] == player):
                    return True
        
        
        for c in range(self.COLS):
            for r in range(self.ROWS - 3):
                if (self.board[r][c] == player and 
                    self.board[r+1][c] == player and 
                    self.board[r+2][c] == player and 
                    self.board[r+3][c] == player):
                    return True
        
        
        for r in range(self.ROWS - 3):
            for c in range(self.COLS - 3):
                if (self.board[r][c] == player and 
                    self.board[r+1][c+1] == player and 
                    self.board[r+2][c+2] == player and 
                    self.board[r+3][c+3] == player):
                    return True
        
        
        for r in range(3, self.ROWS):
            for c in range(self.COLS - 3):
                if (self.board[r][c] == player and 
                    self.board[r-1][c+1] == player and 
                    self.board[r-2][c+2] == player and 
                    self.board[r-3][c+3] == player):
                    return True
        
        return False
    
    def handle_click(self, mouse_x, mouse_y):
        
        if self.game_over or self.ai_thinking:
            return
        
        if (self.grid_x <= mouse_x <= self.grid_x + self.grid_width and
            self.grid_y <= mouse_y <= self.grid_y + self.grid_height):
            
            col = (mouse_x - self.grid_x) // self.cell_width
            if 0 <= col < self.COLS:
                self.make_move(col)

    
    def draw_grid(self):
        
        pygame.draw.rect(self.screen, self.colors['grid_bg'],
                        (self.grid_x, self.grid_y, self.grid_width, self.grid_height),
                        border_radius=15)
        
        for r in range(self.ROWS):
            for c in range(self.COLS):
                x = self.grid_x + c * self.cell_width + self.cell_width // 2
                y = self.grid_y + r * self.cell_height + self.cell_height // 2
                
                
                pygame.draw.circle(self.screen, self.colors['hole_bg'],
                                 (x, y), self.hole_radius)
                
                
                if self.board[r][c] == 1:
                    pygame.draw.circle(self.screen, self.colors['player1'],
                                     (x, y), self.hole_radius - 5)
                elif self.board[r][c] == 2:
                    color = self.colors['ai'] if self.ai_enabled else self.colors['player2']
                    pygame.draw.circle(self.screen, color, (x, y), self.hole_radius - 5)

    def draw_history(self):
        
        if not self.history:
            return
        
        
        history_bg = pygame.Surface((200, 150), pygame.SRCALPHA)
        pygame.draw.rect(history_bg, (44, 62, 80, 200), (0, 0, 200, 150), border_radius=10)
        self.screen.blit(history_bg, (20, 20))
        
        
        font = pygame.font.SysFont(None, 24)
        title = font.render("History", True, (236, 240, 241))
        self.screen.blit(title, (30, 30))
        
        
        for i, move in enumerate(self.history[-3:]):
            player_text = "Shahd" if move['player'] == 1 else ("AI" if self.ai_enabled else "Player 2")
            text = f"{player_text}: ({move['col'] + 1}, {move['row'] + 1})"
            color = self.colors['player1'] if move['player'] == 1 else (self.colors['ai'] if self.ai_enabled else self.colors['player2'])
            
            move_text = font.render(text, True, color)
            self.screen.blit(move_text, (30, 60 + i * 25))

    def toggle_ai_vs_ai(self):
        if not self.ai_enabled:
            self.ai_enabled = True
            if not hasattr(self, 'ai_player1'):
                self.ai_player1 = HybridAI(player_number=1, max_depth=4, use_threading=False)
                self.ai_player2 = HybridAI(player_number=2, max_depth=4, use_threading=False)
        
        self.ai_vs_ai_mode = not self.ai_vs_ai_mode
        
        if self.ai_vs_ai_mode:
            self.ai_thinking = False
            self.ai_move_pending = False
            self.ai_vs_ai_running = True
            
            self.start_ai_vs_ai()
            print("AI vs AI mode: ON")
        else:
            self.ai_vs_ai_running = False
            if self.ai_vs_ai_thread:
                self.ai_vs_ai_thread = None
            print("AI vs AI mode: OFF")  

    def ai_vs_ai_loop(self):
        """حلقة AI ضد AI"""
        while self.ai_vs_ai_mode and not self.game_over and self.ai_vs_ai_running:
            time.sleep(self.ai_vs_ai_speed)
            
            if not self.ai_vs_ai_mode or self.game_over or not self.ai_vs_ai_running:
                break
            
            if self.current_player == 1:
                ai_to_use = self.ai_player1
            else:
                ai_to_use = self.ai_player2
            
            class BoardForAI:
                def __init__(self, game):
                    self.width = game.COLS
                    self.height = game.ROWS
                    self.board = game.board.copy()
                    self.heights = game.heights.copy()
                    self.current_player = game.current_player
                
                def hash_board(self):
                    return hash(str(self.board))
            
            board_wrapper = BoardForAI(self)
            
            try:
                col = ai_to_use.get_best_move(board_wrapper)
                
                if col is not None and 0 <= col < self.COLS:
                    self.execute_ai_vs_ai_move(col)
                    
            except Exception as e:
                print(f"Error in AI vs AI: {e}")
                continue

    def execute_ai_vs_ai_move(self, col):
        self.make_move(col)


    def start_ai_thinking(self):
        if self.ai_thinking or self.ai_move_pending:
            return
        
        self.ai_thinking = True
        
        self.ai_thread = threading.Thread(target=self.calculate_ai_move, daemon=True)
        self.ai_thread.start()

    def calculate_ai_move(self):
        try:
            time.sleep(0.1)
            
            class BoardForAI:
                def _init_(self, game):
                    self.width = game.COLS
                    self.height = game.ROWS
                    self.board = game.board.copy()
                    self.heights = game.heights.copy()
                    self.current_player = game.current_player
                
                def hash_board(self):
                    return hash(str(self.board))
            
            board_for_ai = BoardForAI(self)
            
            col = self.ai.get_best_move(board_for_ai)
            
            self.ai_move_column = col
            self.ai_move_pending = True
            self.ai_move_time = pygame.time.get_ticks() + self.ai_delay
            
        except Exception as e:
            print(f"AI calculation error: {e}")
            self.ai_thinking = False
            self.ai_move_pending = False

    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.ai_move_pending and current_time >= self.ai_move_time:
            if self.ai_move_column is not None and 0 <= self.ai_move_column < self.COLS:
                self.execute_ai_move(self.ai_move_column)
            
            self.ai_move_pending = False
            self.ai_move_column = None
            self.ai_thinking = False

    def execute_ai_move(self, col):
        if self.game_over or self.heights[col] >= self.ROWS:
            return
        
        row = self.ROWS - 1 - self.heights[col]
        self.board[row][col] = self.current_player
        self.heights[col] += 1
        self.moves_count += 1
        
        self.history.append({
            'col': col,
            'row': row,
            'player': self.current_player
        })
        
        if self.check_winner(self.current_player):
            self.game_over = True
            self.winner = self.current_player
        elif self.moves_count == self.ROWS * self.COLS:
            self.game_over = True
            self.winner = -1  # تعادل
        else:
            self.current_player = 3 - self.current_player
            
            if self.ai_enabled and self.current_player == 2 and not self.game_over:
                self.start_ai_thinking()

    def draw_players(self):
        font_large = pygame.font.SysFont(None, 32)
        font_small = pygame.font.SysFont(None, 24)
        
        if self.ai_vs_ai_mode:
            player1_name = "AI 1"
            player1_color = self.colors['ai']
            player2_name = "AI 2"
            player2_color = self.colors['ai']
        else:
            player1_name = "Shahd"
            player1_color = self.colors['player1']
            player2_name = "AI" if self.ai_enabled else "Searing"
            player2_color = self.colors['ai'] if self.ai_enabled else self.colors['player2']
        
        pygame.draw.rect(self.screen, player1_color,
                        (self.grid_x - 220, self.grid_y, 200, 80),
                        border_radius=10)
        
        name1 = font_large.render(player1_name, True, self.colors['text'])
        type1 = font_small.render("Red" if self.ai_vs_ai_mode else "Player 1", True, self.colors['text'])
        self.screen.blit(name1, (self.grid_x - 210, self.grid_y + 15))
        self.screen.blit(type1, (self.grid_x - 210, self.grid_y + 50))
        
        pygame.draw.rect(self.screen, player2_color,
                        (self.grid_x + self.grid_width + 20, self.grid_y, 200, 80),
                        border_radius=10)
        
        name2 = font_large.render(player2_name, True, self.colors['text'])
        type2 = font_small.render("Yellow" if self.ai_vs_ai_mode else "Player 2", True, self.colors['text'])
        self.screen.blit(name2, (self.grid_x + self.grid_width + 30, self.grid_y + 15))
        self.screen.blit(type2, (self.grid_x + self.grid_width + 30, self.grid_y + 50))

    def draw_turn_indicator(self):
        font = pygame.font.SysFont(None, 28)
        
        if self.ai_vs_ai_mode:
            text = "AI vs AI Mode"
            color = self.colors['ai_vs_ai']
        elif self.ai_thinking:
            text = "AI is thinking..."
            color = self.colors['ai']
        elif self.game_over:
            if self.winner == 1:
                text = "AI 1 Wins!" if self.ai_vs_ai_mode else "Shahd Wins!"
                color = self.colors['ai'] if self.ai_vs_ai_mode else self.colors['player1']
            elif self.winner == 2:
                text = "AI 2 Wins!" if self.ai_vs_ai_mode else ("AI Wins!" if self.ai_enabled else "Searing Wins!")
                color = self.colors['ai'] if self.ai_vs_ai_mode or self.ai_enabled else self.colors['player2']
            else:
                text = "It's a Draw!"
                color = (255, 215, 0) 
        elif self.current_player == 1:
            text = "AI 1's Turn" if self.ai_vs_ai_mode else "Shahd's Turn"
            color = self.colors['ai'] if self.ai_vs_ai_mode else self.colors['player1']
        else:
            text = "AI 2's Turn" if self.ai_vs_ai_mode else ("AI's Turn" if self.ai_enabled else "Searing's Turn")
            color = self.colors['ai'] if self.ai_vs_ai_mode or self.ai_enabled else self.colors['player2']
        
        text_surface = font.render(text, True, color)
        x = self.WIDTH // 2 - text_surface.get_width() // 2
        y = self.grid_y - 40
        self.screen.blit(text_surface, (x, y))

    def draw_thinking_indicator(self):
        current_time = pygame.time.get_ticks()
        dot_offset = (current_time // 300) % 4
        
        center_x = self.WIDTH // 2
        center_y = self.grid_y - 80
        
        for i in range(3):
            x = center_x - 30 + i * 20
            y = center_y
            
            dot_size = 5
            if i == dot_offset:
                dot_size = 8
            
            pygame.draw.circle(self.screen, self.colors['ai'], (x, y), dot_size)

    def draw_winner(self):
        if not self.game_over:
            return
        
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        frame_width = 500
        frame_height = 300
        frame_x = (self.WIDTH - frame_width) // 2
        frame_y = (self.HEIGHT - frame_height) // 2
        
        if self.winner == 1:
            if self.ai_vs_ai_mode:
                color = self.colors['ai']
                text = "AI 1 Wins!"
            else:
                color = self.colors['player1']
                text = "Shahd Wins!"
        elif self.winner == 2:
            if self.ai_vs_ai_mode:
                color = self.colors['ai']
                text = "AI 2 Wins!"
            elif self.ai_enabled:
                color = self.colors['ai']
                text = "AI Wins!"
            else:
                color = self.colors['player2']
                text = "Searing Wins!"
        else:
            color = (255, 215, 0)  
            text = "It's a Draw!"
        
        pygame.draw.rect(self.screen, color,
                        (frame_x, frame_y, frame_width, frame_height),
                        border_radius=20)
        
        pygame.draw.rect(self.screen, (255, 255, 255),
                        (frame_x, frame_y, frame_width, frame_height),
                        5, border_radius=20)
        
        font_big = pygame.font.SysFont(None, 64)
        font_small = pygame.font.SysFont(None, 32)
        
        winner_text = font_big.render(text, True, (255, 255, 255))
        restart_text = font_small.render("Press R to play again", True, (220, 220, 220))
        
        self.screen.blit(winner_text,
                        (self.WIDTH//2 - winner_text.get_width()//2,
                         frame_y + 80))
        
        self.screen.blit(restart_text,
                        (self.WIDTH//2 - restart_text.get_width()//2,
                         frame_y + 180))

    def draw(self):
        self.draw_grid()
        
        self.draw_history()
        
        self.draw_players()
        
        self.draw_turn_indicator()
        
        if self.game_over:
            self.draw_winner()
        
        if self.ai_thinking:
            self.draw_thinking_indicator()
                  