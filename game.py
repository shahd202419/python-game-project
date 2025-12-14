import pygame
import numpy as np
import threading
import time
from algorithm import HybridAI
class ConnectFourGame:
    def _init_(self, screen, width, height, use_ai=True):
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
            self.ai = HybridAI(player_number=2, max_depth=4, use_advanced=False)           
            self.ai_player1 = HybridAI(player_number=1, max_depth=4)
            self.ai_player2 = HybridAI(player_number=2, max_depth=4)
        
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
            self.ai = HybridAI(player_number=2, max_depth=4)
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

            