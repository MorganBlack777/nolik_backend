from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import User
from app.schemas.schemas import UserCreate
from app.controllers.auth import get_password_hash, get_user_by_username

def create_user(db: Session, user: UserCreate):
    """
    Create a new user
    """
    # Check if username already exists
    existing_user = get_user_by_username(db, username=user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_user_email = db.query(User).filter(User.email == user.email).first()
    if db_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    """
    Get user by ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Get all users with pagination
    """
    return db.query(User).offset(skip).limit(limit).all()

def update_user_active_status(db: Session, user_id: int, is_active: bool):
    """
    Activate or deactivate a user
    """
    user = get_user(db, user_id)
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user 