import os
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.db import Base
from app.models.models import User, Game, Move
from app.controllers.auth import get_password_hash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection string
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost/tictactoe")

def init_db():
    """Initialize database and create tables"""
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if we already have any users
        user_count = db.query(User).count()
        
        # Add test users if no users exist
        if user_count == 0:
            create_test_data(db)
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    finally:
        db.close()

def create_test_data(db):
    """Create test data for the database"""
    # Create test users
    user1 = User(
        username="player1",
        email="player1@example.com",
        hashed_password=get_password_hash("Password1"),
        is_active=True
    )
    
    user2 = User(
        username="player2",
        email="player2@example.com",
        hashed_password=get_password_hash("Password2"),
        is_active=True
    )
    
    # Add users to database
    db.add(user1)
    db.add(user2)
    db.flush()  # Flush to get user IDs
    
    # Create a test game
    game = Game(
        player_x_id=user1.id,
        player_o_id=user2.id,
        status="in_progress"
    )
    
    db.add(game)
    db.flush()  # Flush to get game ID
    
    # Add some moves to the game
    moves = [
        Move(game_id=game.id, user_id=user1.id, row=0, col=0, symbol="X", move_number=1),
        Move(game_id=game.id, user_id=user2.id, row=1, col=1, symbol="O", move_number=2),
        Move(game_id=game.id, user_id=user1.id, row=0, col=1, symbol="X", move_number=3),
    ]
    
    for move in moves:
        db.add(move)

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully.") 