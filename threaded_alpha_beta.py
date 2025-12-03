import numpy as np
from collections import defaultdict

class ThreadMemory:
    def init(self):
        self.transposition_table = {}
        self.killer_moves = [[] for _ in range(100)]
        self.history = defaultdict(int)
        self.opening_book = {}
        empty_hash = hash(str(np.zeros((6, 7))))
        self.opening_book[empty_hash] = 3

class ThreadEnhancedAI:
    def init(self, player_number, max_depth=8):
        self.player = player_number
        self.max_depth = max_depth
        self.memory = ThreadMemory()
        self.nodes_searched = 0
    
    def get_best_move(self, board):
        self.nodes_searched = 0
        
        legal_moves = [col for col in range(board.width) 
                      if board.heights[col] < board.height]
        
        if sum(board.heights) == 0:
            empty_hash = hash(str(np.zeros((6, 7))))
            return self.memory.opening_book.get(empty_hash, 3)
        
        ordered_moves = self._order_moves(board, legal_moves)
        best_move = ordered_moves[0]
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        
        for move in ordered_moves:
            test_board = self._copy_board(board)
            test_board.make_move(move)
            move_value = self._thread_alpha_beta(test_board, self.max_depth - 1, alpha, beta, False)
            
            if move_value > best_value:
                best_value = move_value
                best_move = move
                alpha = max(alpha, best_value)
        
        return best_move
    
    def _thread_alpha_beta(self, board, depth, alpha, beta, maximizing_player):
        self.nodes_searched += 1
        original_alpha = alpha
        
        winner = self._check_winner(board)
        if winner != 0:
            return 10000 if winner == self.player else -10000
        
        if depth == 0:
            return self._evaluate_board(board)
        
        board_hash = board.hash_board()
        tt_entry = self.memory.transposition_table.get(board_hash)
        
        if tt_entry and tt_entry['depth'] >= depth:
            if tt_entry['flag'] == 'EXACT':
                return tt_entry['score']
            elif tt_entry['flag'] == 'LOWER':
                alpha = max(alpha, tt_entry['score'])
            elif tt_entry['flag'] == 'UPPER':
                beta = min(beta, tt_entry['score'])
            
            if alpha >= beta:
                return tt_entry['score']
        
        legal_moves = [col for col in range(board.width) 
                      if board.heights[col] < board.height]
        ordered_moves = self._order_moves(board, legal_moves)
        
        if maximizing_player:
            best_score = -float('inf')
            for move in ordered_moves:
                test_board = self._copy_board(board)
                test_board.make_move(move)
                score = self._thread_alpha_beta(test_board, depth - 1, alpha, beta, False)
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                
                if score >= beta:
                    if move not in self.memory.killer_moves[depth]:
                        self.memory.killer_moves[depth].insert(0, move)
                        if len(self.memory.killer_moves[depth]) > 2:
                            self.memory.killer_moves[depth].pop()
                    break
                
                if alpha >= beta:
                    break
        else:
            best_score = float('inf')
            for move in ordered_moves:
                test_board = self._copy_board(board)
                test_board.make_move(move)
                score = self._thread_alpha_beta(test_board, depth - 1, alpha, beta, True)
                best_score = min(best_score, score)
                beta = min(beta, best_score)
                
                if alpha >= beta:
                    break
        
        if best_score <= original_alpha:
            flag = 'UPPER'
        elif best_score >= beta:
            flag = 'LOWER'
        else:
            flag = 'EXACT'
        
        self.memory.transposition_table[board_hash] = {
            'score': best_score,
            'depth': depth,
            'flag': flag
        }
        
        return best_score
    
    def _order_moves(self, board, moves):
        if not moves:
            return moves
        
        center = board.width // 2
        ordered = sorted(moves, key=lambda x: abs(x - center))
        
        killer_moves = self.memory.killer_moves[self.max_depth]
        for killer in killer_moves:
            if killer in ordered:
                ordered.remove(killer)
                ordered.insert(0, killer)
        
        ordered.sort(key=lambda move: self.memory.history.get((board.current_player, move), 0), reverse=True)
        return ordered
    
    def _evaluate_board(self, board):
        score = 0
        center_col = board.width // 2
        center_count = sum(1 for row in range(board.height) if board.board[row][center_col] == self.player)
        score += center_count * 3
        
        for row in range(board.height):
            for col in range(board.width - 3):
                window = [board.board[row][col + i] for i in range(4)]
                score += self._evaluate_window(window)
        
        for col in range(board.width):
            for row in range(board.height - 3):
                window = [board.board[row + i][col] for i in range(4)]
                score += self._evaluate_window(window)
        
        for row in range(board.height - 3):
            for col in range(board.width - 3):
                window = [board.board[row + i][col + i] for i in range(4)]
                score += self._evaluate_window(window)
        
        for row in range(3, board.height):
            for col in range(board.width - 3):
                window = [board.board[row - i][col + i] for i in range(4)]
                score += self._evaluate_window(window)
        
        return score
    
    def _evaluate_window(self, window):
        ai_count = window.count(self.player)
        opponent_count = window.count(3 - self.player)
        
        if ai_count == 4:
            return 1000
        elif opponent_count == 4:
            return -1000
        elif ai_count == 3 and opponent_count == 0:
            return 50
        elif ai_count == 2 and opponent_count == 0:
            return 10
        elif opponent_count == 3 and ai_count == 0:
            return -80
        elif opponent_count == 2 and ai_count == 0:
            return -5
        return 0
    
    def _check_winner(self, board):
        for row in range(board.height):
            for col in range(board.width - 3):
                window = [board.board[row][col + i] for i in range(4)]
                if all(cell == 1 for cell in window):
                    return 1
                if all(cell == 2 for cell in window):
                    return 2
        
        for col in range(board.width):
            for row in range(board.height - 3):
                window = [board.board[row + i][col] for i in range(4)]
                if all(cell == 1 for cell in window):
                    return 1
                if all(cell == 2 for cell in window):
                    return 2
        
        for row in range(board.height - 3):
            for col in range(board.width - 3):
                window = [board.board[row + i][col + i] for i in range(4)]
                if all(cell == 1 for cell in window):
                    return 1
                if all(cell == 2 for cell in window):
                    return 2
        
        for row in range(3, board.height):
            for col in range(board.width - 3):
                window = [board.board[row - i][col + i] for i in range(4)]
                if all(cell == 1 for cell in window):
                    return 1
                if all(cell == 2 for cell in window):
                    return 2
        
        return 0
    
    def _copy_board(self, board):
        class SimpleBoard:
            def init(self, original):
                self.width = original.width
                self.height = original.height
                self.board = original.board.copy()
                self.heights = original.heights.copy()
                self.current_player = original.current_player
            
            def make_move(self, col):
                if self.heights[col] >= self.height:
                    return False
                row = self.height - 1 - self.heights[col]
                self.board[row][col] = self.current_player
                self.heights[col] += 1
                self.current_player = 3 - self.current_player
                return True
            
            def hash_board(self):
                return hash(str(self.board))
        
        return SimpleBoard(board)
    
    def reset_memory(self):
        self.memory=ThreadMemory()