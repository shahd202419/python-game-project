import numpy as np
from collections import defaultdict
import time

class ThreadMemory:
    def __init__(self): 
        self.transposition_table = {}
        self.killer_moves = [[] for _ in range(20)]
        self.history = defaultdict(int)
        self.opening_book = {}
        empty_hash = hash(str(np.zeros((6, 7))))
        self.opening_book[empty_hash] = 3

class ThreadEnhancedAI:
    def __init__(self, player_number, max_depth=6):
        self.player = player_number
        self.max_depth = max_depth
        self.memory = ThreadMemory()
        self.nodes_searched = 0
        self.time_limit = 2.0

    def get_best_move(self, board):
        start_time = time.time()
        self.nodes_searched = 0
        legal_moves = [col for col in range(board.width) if board.heights[col] < board.height]
        if not legal_moves:
            return 3
        if sum(board.heights) == 0:
            return 3
        for move in legal_moves:
            if self.is_winning_move(board, move, self.player):
                return move
        opponent = 3 - self.player
        for move in legal_moves:
            if self.is_winning_move(board, move, opponent):
                return move
        ordered_moves = self._order_moves_smart(board, legal_moves)
        best_move = ordered_moves[0]
        alpha = -float('inf')
        beta = float('inf')
        for depth in range(1, min(7, self.max_depth + 1)):
            if time.time() - start_time > self.time_limit:
                break
            current_best = None
            current_value = -float('inf')
            for move in ordered_moves:
                if time.time() - start_time > self.time_limit:
                    break
                test_board = self._copy_board(board)
                test_board.make_move(move)
                value = self._alpha_beta_pruning(test_board, depth - 1, alpha, beta, False, start_time)
                if value > current_value:
                    current_value = value
                    current_best = move
                    alpha = max(alpha, value)
            if current_best is not None:
                best_move = current_best
        return best_move

    def _alpha_beta_pruning(self, board, depth, alpha, beta, maximizing_player, start_time):
        if time.time() - start_time > self.time_limit:
            return 0
        self.nodes_searched += 1
        winner = self._check_winner(board)
        if winner != 0:
            if winner == self.player:
                return 100000 - (self.max_depth - depth)
            else:
                return -100000 + (self.max_depth - depth)
        if depth == 0:
            return self._evaluate_board_advanced(board)
        legal_moves = [col for col in range(board.width) if board.heights[col] < board.height]
        if not legal_moves:
            return 0
        if maximizing_player:
            value = -float('inf')
            for move in legal_moves:
                if time.time() - start_time > self.time_limit:
                    return value
                test_board = self._copy_board(board)
                test_board.make_move(move)
                value = max(value, self._alpha_beta_pruning(test_board, depth - 1, alpha, beta, False, start_time))
                if value >= beta:
                    if move not in self.memory.killer_moves[depth]:
                        self.memory.killer_moves[depth].insert(0, move)
                        if len(self.memory.killer_moves[depth]) > 2:
                            self.memory.killer_moves[depth].pop()
                    break
                alpha = max(alpha, value)
            return value
        else:
            value = float('inf')
            for move in legal_moves:
                if time.time() - start_time > self.time_limit:
                    return value
                test_board = self._copy_board(board)
                test_board.make_move(move)
                value = min(value, self._alpha_beta_pruning(test_board, depth - 1, alpha, beta, True, start_time))
                if value <= alpha:
                    break
                beta = min(beta, value)
            return value

    def _order_moves_smart(self, board, moves):
        if not moves:
            return moves
        scores = []
        opponent = 3 - self.player
        for move in moves:
            score = 0
            center = board.width // 2
            score += 10 / (abs(move - center) + 1)
            if self.is_winning_move(board, move, self.player):
                score += 1000
            if self.is_winning_move(board, move, opponent):
                score += 800
            threat_score = self._evaluate_threats(board, move, self.player)
            score += threat_score * 5
            opponent_threat = self._evaluate_threats(board, move, opponent)
            score -= opponent_threat * 4
            row = board.height - 1 - board.heights[move]
            if row == board.height - 1:
                score += 20
            scores.append((move, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in scores]

    def _evaluate_threats(self, board, col, player):
        if board.heights[col] >= board.height:
            return 0
        temp_board = self._copy_board(board)
        temp_board.make_move(col)
        threats = 0
        for r in range(temp_board.height):
            for c in range(temp_board.width - 3):
                window = [temp_board.board[r][c + i] for i in range(4)]
                if window.count(player) == 3 and window.count(0) == 1:
                    threats += 1
        for c in range(temp_board.width):
            for r in range(temp_board.height - 3):
                window = [temp_board.board[r + i][c] for i in range(4)]
                if window.count(player) == 3 and window.count(0) == 1:
                    threats += 1
        for r in range(temp_board.height - 3):
            for c in range(temp_board.width - 3):
                window = [temp_board.board[r + i][c + i] for i in range(4)]
                if window.count(player) == 3 and window.count(0) == 1:
                    threats += 1
        for r in range(3, temp_board.height):
            for c in range(temp_board.width - 3):
                window = [temp_board.board[r - i][c + i] for i in range(4)]
                if window.count(player) == 3 and window.count(0) == 1:
                    threats += 1
        return threats

    def _evaluate_board_advanced(self, board):
        score = 0
        opponent = 3 - self.player
        center_col = board.width // 2
        for row in range(board.height):
            if board.board[row][center_col] == self.player:
                score += 6
            elif board.board[row][center_col] == opponent:
                score -= 6
        score += self._evaluate_all_windows(board, self.player) * 2
        score -= self._evaluate_all_windows(board, opponent) * 2
        for col in range(board.width):
            height = board.heights[col]
            if height > 0:
                row = board.height - height
                if board.board[row][col] == self.player:
                    score += 2
                elif board.board[row][col] == opponent:
                    score -= 2
        my_threats = self._count_potential_wins(board, self.player)
        opponent_threats = self._count_potential_wins(board, opponent)
        score += (my_threats - opponent_threats) * 50
        return score

    def _evaluate_all_windows(self, board, player):
        score = 0
        for r in range(board.height):
            for c in range(board.width - 3):
                window = [board.board[r][c + i] for i in range(4)]
                score += self._evaluate_window_advanced(window, player)
        for c in range(board.width):
            for r in range(board.height - 3):
                window = [board.board[r + i][c] for i in range(4)]
                score += self._evaluate_window_advanced(window, player)
        for r in range(board.height - 3):
            for c in range(board.width - 3):
                window = [board.board[r + i][c + i] for i in range(4)]
                score += self._evaluate_window_advanced(window, player)
        for r in range(3, board.height):
            for c in range(board.width - 3):
                window = [board.board[r - i][c + i] for i in range(4)]
                score += self._evaluate_window_advanced(window, player)
        return score

    def _evaluate_window_advanced(self, window, player):
        opponent = 3 - player
        my_count = window.count(player)
        opp_count = window.count(opponent)
        empty_count = window.count(0)
        if my_count == 4:
            return 10000
        elif opp_count == 4:
            return -10000
        elif my_count == 3 and empty_count == 1:
            return 100
        elif my_count == 2 and empty_count == 2:
            return 10
        elif opp_count == 3 and empty_count == 1:
            return -80
        elif opp_count == 2 and empty_count == 2:
            return -5
        return 0

    def _count_potential_wins(self, board, player):
        count = 0
        for r in range(board.height):
            for c in range(board.width - 3):
                window = [board.board[r][c + i] for i in range(4)]
                if window.count(player) == 3 and window.count(0) == 1:
                    count += 1
        for c in range(board.width):
            for r in range(board.height - 3):
                window = [board.board[r + i][c] for i in range(4)]
                if window.count(player) == 3 and window.count(0) == 1:
                    count += 1
        for r in range(board.height - 3):
            for c in range(board.width - 3):
                window = [board.board[r + i][c + i] for i in range(4)]
                if window.count(player) == 3 and window.count(0) == 1:
                    count += 1
        for r in range(3, board.height):
            for c in range(board.width - 3):
                window = [board.board[r - i][c + i] for i in range(4)]
                if window.count(player) == 3 and window.count(0) == 1:
                    count += 1
        return count

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

    def is_winning_move(self, board, col, player):
        if board.heights[col] >= board.height:
            return False
        test_board = self._copy_board(board)
        test_board.make_move(col)
        return self._check_winner(test_board) == player

    def _copy_board(self, board):
        class SimpleBoard:
            def __init__(self, original):  
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
        self.memory = ThreadMemory()

class HybridAI(ThreadEnhancedAI):
    def __init__(self, player_number, max_depth=6, use_threading=False):
        super().__init__(player_number, max_depth)
        self.use_threading = use_threading