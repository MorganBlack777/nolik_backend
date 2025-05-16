from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.schemas.schemas import UserResponse
from app.controllers.user_controller import get_user, get_users, update_user_active_status
from app.controllers.auth import get_current_active_user
from app.models.models import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    """Get current logged in user"""
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = get_user(db, user_id=user_id)
    return user

@router.put("/{user_id}/activate", response_model=UserResponse)
def activate_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Activate a user"""
    # In a real application, you would check if the current user has admin privileges
    return update_user_active_status(db, user_id=user_id, is_active=True)

@router.put("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Deactivate a user"""
    # In a real application, you would check if the current user has admin privileges
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate yourself"
        )
    return update_user_active_status(db, user_id=user_id, is_active=False) 