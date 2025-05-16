from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database.db import Base

class GameStatus(enum.Enum):
    IN_PROGRESS = "in_progress"
    X_WON = "x_won"
    O_WON = "o_won"
    DRAW = "draw"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_bot = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    games_as_player_x = relationship("Game", back_populates="player_x", foreign_keys="Game.player_x_id")
    games_as_player_o = relationship("Game", back_populates="player_o", foreign_keys="Game.player_o_id")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    player_x_id = Column(Integer, ForeignKey("users.id"))
    player_o_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default=GameStatus.IN_PROGRESS.value)
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_bot_game = Column(Boolean, default=False)
    board_size = Column(Integer, default=3)
    win_length = Column(Integer, default=3)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    player_x = relationship("User", back_populates="games_as_player_x", foreign_keys=[player_x_id])
    player_o = relationship("User", back_populates="games_as_player_o", foreign_keys=[player_o_id])
    moves = relationship("Move", back_populates="game", cascade="all, delete-orphan")
    
class Move(Base):
    __tablename__ = "moves"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    row = Column(Integer)  # 0, 1, or 2
    col = Column(Integer)  # 0, 1, or 2
    symbol = Column(String(1))  # "X" or "O"
    move_number = Column(Integer)  # The sequence number of the move
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    game = relationship("Game", back_populates="moves")
    user = relationship("User") 