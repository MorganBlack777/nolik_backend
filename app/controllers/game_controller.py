from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Optional, Tuple

from app.models.models import Game, User, Move, GameStatus
from app.schemas.schemas import GameCreate, GameBoard

def create_game(db: Session, game: GameCreate, current_user_id: int):
    """Create a new game"""
    # Validate board size and win length
    if game.board_size < 3 or game.board_size > 10:
        raise HTTPException(status_code=400, detail="Board size must be between 3 and 10")
    if game.win_length < 3 or game.win_length > game.board_size:
        raise HTTPException(status_code=400, detail="Win length must be between 3 and board size")
    
    db_game = Game(
        player_x_id=current_user_id,
        player_o_id=game.player_o_id,
        status=GameStatus.IN_PROGRESS.value,
        board_size=game.board_size,
        win_length=game.win_length
    )
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

def get_game(db: Session, game_id: int):
    """Get game by ID"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

def get_user_games(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get games where user is player X or player O"""
    return db.query(Game).filter(
        (Game.player_x_id == user_id) | (Game.player_o_id == user_id)
    ).order_by(Game.created_at.desc()).offset(skip).limit(limit).all()

def join_game(db: Session, game_id: int, user_id: int):
    """Join an existing game as player O"""
    game = get_game(db, game_id)
    
    if game.player_o_id is not None:
        raise HTTPException(status_code=400, detail="Game already has player O")
    
    if game.player_x_id == user_id:
        raise HTTPException(status_code=400, detail="You cannot play against yourself")
    
    game.player_o_id = user_id
    db.commit()
    db.refresh(game)
    return game

def make_move(db: Session, game_id: int, user_id: int, row: int, col: int):
    """Make a move in the game"""
    game = get_game(db, game_id)
    
    # Check if game is still in progress
    if game.status != GameStatus.IN_PROGRESS.value:
        raise HTTPException(status_code=400, detail="Game is already finished")
    
    # Check if both players joined
    if game.player_o_id is None:
        raise HTTPException(status_code=400, detail="Waiting for player O to join")
    
    # Check if user is part of the game
    if user_id != game.player_x_id and user_id != game.player_o_id:
        raise HTTPException(status_code=403, detail="You are not part of this game")
    
    # Get current board state
    board_state, move_count = get_board_state(db, game_id)
    
    # Determine current player based on move count
    current_player = "X" if move_count % 2 == 0 else "O"
    expected_player_id = game.player_x_id if current_player == "X" else game.player_o_id
    
    # Check if it's the user's turn
    if user_id != expected_player_id:
        raise HTTPException(
            status_code=400, 
            detail=f"It's not your turn. Current player: {current_player}"
        )
    
    # Check if cell is empty
    if board_state[row][col] is not None:
        raise HTTPException(status_code=400, detail="Cell is already occupied")
    
    # Make the move
    new_move = Move(
        game_id=game_id,
        user_id=user_id,
        row=row,
        col=col,
        symbol=current_player,
        move_number=move_count + 1
    )
    db.add(new_move)
    db.commit()
    
    # Update board state with the new move
    board_state[row][col] = current_player
    
    # Check if the game is over
    game_status, winner_id = check_game_status(board_state, game)
    
    if game_status != GameStatus.IN_PROGRESS:
        game.status = game_status.value
        game.winner_id = winner_id
        db.commit()
    
    db.refresh(new_move)
    return new_move

def get_board_state(db: Session, game_id: int) -> Tuple[List[List[Optional[str]]], int]:
    """Get the current board state for a game"""
    game = get_game(db, game_id)
    # Create empty board with dynamic size
    board = [[None for _ in range(game.board_size)] for _ in range(game.board_size)]
    
    # Get all moves for this game ordered by move number
    moves = db.query(Move).filter(Move.game_id == game_id).order_by(Move.move_number).all()
    
    # Fill in the board with moves
    for move in moves:
        board[move.row][move.col] = move.symbol
    
    return board, len(moves)

def check_game_status(board: List[List[Optional[str]]], game: Game) -> Tuple[GameStatus, Optional[int]]:
    """Check if the game is won, drawn, or still in progress"""
    size = game.board_size
    win_length = game.win_length
    
    # Check rows
    for row in range(size):
        for col in range(size - win_length + 1):
            window = board[row][col:col + win_length]
            if all(x == "X" for x in window):
                return GameStatus.X_WON, game.player_x_id
            if all(x == "O" for x in window):
                return GameStatus.O_WON, game.player_o_id
    
    # Check columns
    for col in range(size):
        for row in range(size - win_length + 1):
            window = [board[row + i][col] for i in range(win_length)]
            if all(x == "X" for x in window):
                return GameStatus.X_WON, game.player_x_id
            if all(x == "O" for x in window):
                return GameStatus.O_WON, game.player_o_id
    
    # Check diagonals
    for row in range(size - win_length + 1):
        for col in range(size - win_length + 1):
            # Check diagonal from top-left to bottom-right
            window = [board[row + i][col + i] for i in range(win_length)]
            if all(x == "X" for x in window):
                return GameStatus.X_WON, game.player_x_id
            if all(x == "O" for x in window):
                return GameStatus.O_WON, game.player_o_id
            
            # Check diagonal from top-right to bottom-left
            window = [board[row + i][col + win_length - 1 - i] for i in range(win_length)]
            if all(x == "X" for x in window):
                return GameStatus.X_WON, game.player_x_id
            if all(x == "O" for x in window):
                return GameStatus.O_WON, game.player_o_id
    
    # Check if board is full (draw)
    is_full = all(cell is not None for row in board for cell in row)
    if is_full:
        return GameStatus.DRAW, None
    
    # Game is still in progress
    return GameStatus.IN_PROGRESS, None

def get_game_with_board(db: Session, game_id: int) -> GameBoard:
    """Get game with current board state"""
    game = get_game(db, game_id)
    board, move_count = get_board_state(db, game_id)
    
    current_player = None
    if game.status == GameStatus.IN_PROGRESS.value:
        current_player = "X" if move_count % 2 == 0 else "O"
    
    return GameBoard(
        board=board,
        status=game.status,
        current_player=current_player
    )

def create_bot_game(db: Session, current_user_id: int, board_size: int = 3, win_length: int = 3) -> Game:
    """Create a new game against the bot"""
    # Get or create bot user
    bot_user = db.query(User).filter(User.username == "bot").first()
    if not bot_user:
        bot_user = User(
            username="bot",
            email="bot@example.com",
            hashed_password="not_used",
            is_active=True,
            is_bot=True
        )
        db.add(bot_user)
        db.commit()
        db.refresh(bot_user)
    
    # Create game with bot as player O
    db_game = Game(
        player_x_id=current_user_id,
        player_o_id=bot_user.id,
        status=GameStatus.IN_PROGRESS.value,
        is_bot_game=True,
        board_size=board_size,
        win_length=win_length
    )
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

def handle_bot_move(db: Session, game_id: int) -> Optional[Move]:
    """Handle bot's move if it's a bot game"""
    game = get_game(db, game_id)
    if not game.is_bot_game:
        return None
    
    from app.controllers.bot_controller import TicTacToeBot
    bot = TicTacToeBot(db, game_id, game.player_o_id)
    return bot.make_move() 