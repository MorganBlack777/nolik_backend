from typing import List, Optional, Tuple
import random
from sqlalchemy.orm import Session
from app.models.models import Game, Move, User, GameStatus
from app.controllers.game_controller import get_board_state, make_move, get_game

class TicTacToeBot:
    def __init__(self, db: Session, game_id: int, bot_user_id: int):
        self.db = db
        self.game_id = game_id
        self.bot_user_id = bot_user_id
        self.game = get_game(db, game_id)
        self.board_size = self.game.board_size
        self.win_length = self.game.win_length

    def make_move(self) -> Optional[Move]:
        """Make a bot move using a simple strategy"""
        try:
            print(f"Bot is making a move for game {self.game_id}")
            board, move_count = get_board_state(self.db, self.game_id)
            
            # Check if it's bot's turn (should be "O")
            current_player = "X" if move_count % 2 == 0 else "O"
            if current_player != "O":
                print(f"Not bot's turn. Current player: {current_player}")
                return None
            
            # Get available spaces first
            available_moves = []
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if board[row][col] is None:
                        available_moves.append((row, col))
            
            if not available_moves:
                print("No available moves for bot")
                return None
            
            # Try to win
            move = self._find_winning_move(board, "O")
            if move and board[move[0]][move[1]] is None:
                print(f"Bot found winning move at {move[0]}, {move[1]}")
                return self._execute_move(move[0], move[1])
            
            # Block opponent's winning move
            move = self._find_winning_move(board, "X")
            if move and board[move[0]][move[1]] is None:
                print(f"Bot blocks opponent at {move[0]}, {move[1]}")
                return self._execute_move(move[0], move[1])
            
            # Take center if available (for odd-sized boards)
            if self.board_size % 2 == 1:
                center = self.board_size // 2
                if board[center][center] is None:
                    print(f"Bot takes center at {center}, {center}")
                    return self._execute_move(center, center)
            
            # Take corners
            corners = [
                (0, 0), 
                (0, self.board_size - 1), 
                (self.board_size - 1, 0), 
                (self.board_size - 1, self.board_size - 1)
            ]
            random.shuffle(corners)
            for row, col in corners:
                if board[row][col] is None:
                    print(f"Bot takes corner at {row}, {col}")
                    return self._execute_move(row, col)
            
            # Take any available space
            if available_moves:
                row, col = random.choice(available_moves)
                print(f"Bot takes random space at {row}, {col}")
                return self._execute_move(row, col)
            
            print("No available moves for bot")
            return None
        except Exception as e:
            print(f"Bot error: {str(e)}")
            return None

    def _find_winning_move(self, board: List[List[Optional[str]]], symbol: str) -> Optional[Tuple[int, int]]:
        """Find a winning move for the given symbol"""
        size = self.board_size
        win_length = self.win_length
        
        # Check rows
        for row in range(size):
            for col in range(size - win_length + 1):
                window = board[row][col:col + win_length]
                if self._is_potential_win(window, symbol):
                    empty_index = next(i for i, val in enumerate(window) if val is None)
                    return (row, col + empty_index)
        
        # Check columns
        for col in range(size):
            for row in range(size - win_length + 1):
                window = [board[row + i][col] for i in range(win_length)]
                if self._is_potential_win(window, symbol):
                    empty_index = next(i for i, val in enumerate(window) if val is None)
                    return (row + empty_index, col)
        
        # Check diagonals (top-left to bottom-right)
        for row in range(size - win_length + 1):
            for col in range(size - win_length + 1):
                window = [board[row + i][col + i] for i in range(win_length)]
                if self._is_potential_win(window, symbol):
                    empty_index = next(i for i, val in enumerate(window) if val is None)
                    return (row + empty_index, col + empty_index)
        
        # Check diagonals (top-right to bottom-left)
        for row in range(size - win_length + 1):
            for col in range(win_length - 1, size):
                window = [board[row + i][col - i] for i in range(win_length)]
                if self._is_potential_win(window, symbol):
                    empty_index = next(i for i, val in enumerate(window) if val is None)
                    return (row + empty_index, col - empty_index)
        
        return None
    
    def _is_potential_win(self, window: List[Optional[str]], symbol: str) -> bool:
        """Check if a window has potential for a win (one empty space and rest are symbol)"""
        return window.count(symbol) == len(window) - 1 and window.count(None) == 1

    def _execute_move(self, row: int, col: int) -> Move:
        """Execute the move through the game controller"""
        try:
            return make_move(self.db, self.game_id, self.bot_user_id, row, col)
        except Exception as e:
            print(f"Bot execution error: {str(e)}")
            raise 