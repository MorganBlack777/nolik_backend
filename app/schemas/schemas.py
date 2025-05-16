from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class MoveBase(BaseModel):
    row: int = Field(..., ge=0)
    col: int = Field(..., ge=0)

    @field_validator('row', 'col')
    @classmethod
    def validate_position(cls, v: int) -> int:
        if v < 0:
            raise ValueError('Position must be non-negative')
        return v

class MoveCreate(MoveBase):
    pass

class MoveResponse(MoveBase):
    id: int
    game_id: int
    user_id: int
    symbol: str
    move_number: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class GameBase(BaseModel):
    player_o_id: Optional[int] = None
    board_size: int = Field(default=3, ge=3, le=10)
    win_length: int = Field(default=3, ge=3, le=5)
    is_bot_game: bool = False

class GameCreate(GameBase):
    pass

class GameResponse(GameBase):
    id: int
    player_x_id: int
    status: str
    winner_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    moves: List[MoveResponse] = []
    
    class Config:
        from_attributes = True

class GameBoard(BaseModel):
    board: List[List[Optional[str]]]
    status: str
    current_player: Optional[str] = None 