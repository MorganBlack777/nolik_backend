from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.schemas.schemas import GameResponse, MoveCreate, MoveResponse, GameBoard
from app.controllers.game_controller import (
    create_game, get_game, get_user_games, join_game, 
    make_move, get_board_state, get_game_with_board
)
from app.controllers.auth import get_current_active_user
from app.models.models import User

router = APIRouter(
    prefix="/api",
    tags=["api"],
    dependencies=[Depends(get_current_active_user)]
)

# Games API endpoints
@router.get("/games", response_model=List[GameResponse])
def read_user_games(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """Get all games for current user"""
    return get_user_games(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/games/{game_id}", response_model=GameResponse)
def read_game(
    game_id: int, 
    db: Session = Depends(get_db)
):
    """Get game by ID"""
    return get_game(db, game_id=game_id)

@router.get("/games/{game_id}/board", response_model=GameBoard)
def read_game_board(
    game_id: int, 
    db: Session = Depends(get_db)
):
    """Get game board state"""
    return get_game_with_board(db, game_id=game_id)

@router.post("/games/{game_id}/join", response_model=GameResponse)
def join_existing_game(
    game_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """Join an existing game as player O"""
    return join_game(db, game_id=game_id, user_id=current_user.id)

@router.post("/games/{game_id}/moves", response_model=MoveResponse)
def create_move(
    game_id: int, 
    move: MoveCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """Make a move in the game"""
    return make_move(
        db, 
        game_id=game_id, 
        user_id=current_user.id, 
        row=move.row, 
        col=move.col
    ) 