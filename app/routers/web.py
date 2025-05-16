from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.database.db import get_db
from app.views.templates import render_template
from app.controllers.auth import authenticate_user, create_access_token, get_current_user
from app.controllers.user_controller import create_user
from app.controllers.game_controller import (
    create_game, get_game, get_user_games, join_game, 
    make_move, get_board_state, get_game_with_board, create_bot_game, handle_bot_move
)
from app.schemas.schemas import UserCreate, GameCreate
from app.models.models import User, Move, Game, GameStatus

router = APIRouter(tags=["web"])

# Функция для получения или создания специального пользователя
def get_or_create_special_user(db: Session, username: str) -> User:
    """Get or create a special user (bot, player1, player2)"""
    special_user = db.query(User).filter(User.username == username).first()
    if not special_user:
        special_user = User(
            username=username,
            email=f"{username}@example.com",
            hashed_password="not_used",
            is_active=True,
            is_bot=username == "bot"  # только бот имеет флаг is_bot=True
        )
        db.add(special_user)
        db.commit()
        db.refresh(special_user)
    return special_user

# Home page
@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page"""
    # Try to get current user
    user = None
    try:
        user = await get_current_user(db, request.cookies.get("access_token"))
    except:
        pass
    
    # Get latest games for display
    latest_games = []
    if user:
        latest_games = get_user_games(db, user.id, limit=5)
    
    return render_template(
        request, 
        "index.html", 
        {
            "user": user,
            "latest_games": latest_games
        }
    )

# Registration page
@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    """Register form page"""
    return render_template(request, "register.html")

@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Register new user"""
    errors = {}
    
    # Validate password match
    if password != confirm_password:
        errors["password"] = "Passwords do not match"
    
    # Create user if no errors
    if not errors:
        try:
            user_create = UserCreate(username=username, email=email, password=password)
            user = create_user(db, user_create)
            
            # Create JWT token and set cookie
            access_token = create_access_token(data={"sub": user.username})
            response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
            response.set_cookie(key="access_token", value=access_token, httponly=True)
            
            return response
        except HTTPException as e:
            errors["general"] = e.detail
        except Exception as e:
            errors["general"] = str(e)
    
    # If there are errors, return to form with errors
    return render_template(
        request, 
        "register.html", 
        {
            "errors": errors,
            "username": username,
            "email": email
        }
    )

# Login page
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    """Login form page"""
    return render_template(request, "login.html")

@router.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Login user"""
    user = authenticate_user(db, username, password)
    if not user:
        return render_template(
            request, 
            "login.html", 
            {
                "error": "Invalid username or password",
                "username": username
            }
        )
    
    if not user.is_active:
        return render_template(
            request, 
            "login.html", 
            {
                "error": "User is inactive",
                "username": username
            }
        )
    
    # Create JWT token and set cookie
    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    
    return response

# Logout
@router.get("/logout")
async def logout():
    """Logout user"""
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response

# Game list page
@router.get("/games", response_class=HTMLResponse)
async def games_list(
    request: Request,
    db: Session = Depends(get_db)
):
    """Game list page"""
    try:
        user = await get_current_user(db, request.cookies.get("access_token"))
        games = get_user_games(db, user.id)
        
        # Получаем список открытых игр, к которым можно присоединиться
        open_games = db.query(Game).filter(
            Game.player_o_id == None,  # Игры без второго игрока
            Game.player_x_id != user.id,  # Не созданные текущим пользователем
            Game.status == GameStatus.IN_PROGRESS.value  # Только активные игры
        ).order_by(Game.created_at.desc()).all()
        
        return render_template(
            request, 
            "games.html", 
            {
                "user": user,
                "games": games,
                "open_games": open_games
            }
        )
    except:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

# New game page
@router.get("/games/new", response_class=HTMLResponse)
async def new_game_form(
    request: Request,
    db: Session = Depends(get_db)
):
    """New game form page"""
    try:
        user = await get_current_user(db, request.cookies.get("access_token"))
        
        # Get list of users for opponent selection, исключая бота и специальных пользователей
        users = db.query(User).filter(
            User.id != user.id,
            User.username != "bot",
            User.username != "player1",
            User.username != "player2"
        ).all()
        
        return render_template(
            request, 
            "new_game.html", 
            {
                "user": user,
                "users": users
            }
        )
    except:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/games/new", response_class=HTMLResponse)
async def create_new_game(
    request: Request,
    player_o_id: Optional[str] = Form(None),
    board_size: int = Form(3),
    win_length: int = Form(3),
    db: Session = Depends(get_db)
):
    """Create new game"""
    try:
        user = await get_current_user(db, request.cookies.get("access_token"))
        
        # Проверяем, выбран ли бот в качестве оппонента
        is_bot = player_o_id == "bot"
        
        # Обработка специальных значений player_o_id
        numeric_player_o_id = None
        if player_o_id:
            if player_o_id == "player1":
                # Создаем игру с Player 1
                special_user = get_or_create_special_user(db, "player1")
                numeric_player_o_id = special_user.id
                is_bot = False
            elif player_o_id == "player2":
                # Создаем игру с Player 2
                special_user = get_or_create_special_user(db, "player2")
                numeric_player_o_id = special_user.id
                is_bot = False
            elif player_o_id == "bot":
                # Создаем игру с ботом
                is_bot = True
            else:
                # Для обычных пользователей преобразуем ID в число
                try:
                    numeric_player_o_id = int(player_o_id)
                except ValueError:
                    numeric_player_o_id = None
        
        # Create game
        game_create = GameCreate(
            player_o_id=numeric_player_o_id,
            board_size=board_size,
            win_length=win_length,
            is_bot_game=is_bot
        )
        
        if is_bot:
            game = create_bot_game(db, user.id, board_size=board_size, win_length=win_length)
            print(f"Created bot game with ID {game.id}, is_bot_game={game.is_bot_game}, board_size={game.board_size}, win_length={game.win_length}")
        else:
            game = create_game(db=db, game=game_create, current_user_id=user.id)
        
        return RedirectResponse(
            url=f"/games/{game.id}", 
            status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as e:
        return render_template(
            request,
            "new_game.html",
            {
                "user": user,
                "error": str(e)
            }
        )

# Game page
@router.get("/games/{game_id}", response_class=HTMLResponse)
async def game_detail(
    request: Request,
    game_id: int,
    db: Session = Depends(get_db)
):
    """Game detail page"""
    try:
        user = await get_current_user(db, request.cookies.get("access_token"))
        
        # Get game and board state
        game = get_game(db, game_id)
        gameboard = get_game_with_board(db, game_id)
        
        # Проверяем, играет ли пользователь против специального игрока (Player 1 или Player 2)
        is_special_opponent = False
        if game.player_o_id:
            opponent = db.query(User).filter(User.id == game.player_o_id).first()
            if opponent and opponent.username in ["player1", "player2"]:
                is_special_opponent = True
        
        # Determine if current user can play
        can_play = False
        if game.status == "in_progress":
            if is_special_opponent:
                # Если игра против Player 1 или Player 2, пользователь может ходить за обоих
                can_play = True
            elif gameboard.current_player == "X" and game.player_x_id == user.id:
                can_play = True
            elif gameboard.current_player == "O" and game.player_o_id == user.id:
                can_play = True
        
        # Используем стандартный шаблон игры
        return render_template(
            request, 
            "game.html",  # Возвращаем оригинальный шаблон
            {
                "user": user,
                "game": game,
                "board": gameboard.board,
                "current_player": gameboard.current_player,
                "can_play": can_play,
                "is_special_opponent": is_special_opponent
            }
        )
    except:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

# Join game
@router.get("/games/{game_id}/join", response_class=HTMLResponse)
async def join_existing_game(
    request: Request,
    game_id: int,
    db: Session = Depends(get_db)
):
    """Join existing game"""
    try:
        user = await get_current_user(db, request.cookies.get("access_token"))
        
        # Join game
        game = join_game(db, game_id, user.id)
        
        return RedirectResponse(url=f"/games/{game.id}", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException as e:
        # If there's an error, redirect to game page with error
        return RedirectResponse(
            url=f"/games/{game_id}?error={e.detail}", 
            status_code=status.HTTP_303_SEE_OTHER
        )
    except:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

# User profile page
@router.get("/users/me", response_class=HTMLResponse)
async def user_profile(request: Request, db: Session = Depends(get_db)):
    """User profile page"""
    try:
        user = await get_current_user(db, request.cookies.get("access_token"))
        
        # Get user's game statistics
        games = get_user_games(db, user.id)
        total_games = len(games)
        wins = len([g for g in games if g.winner_id == user.id])
        draws = len([g for g in games if g.status == "draw"])
        losses = len([g for g in games if g.status in ["x_won", "o_won"] and g.winner_id != user.id])
        
        return render_template(
            request, 
            "profile.html", 
            {
                "user": user,
                "total_games": total_games,
                "wins": wins,
                "draws": draws,
                "losses": losses
            }
        )
    except:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/games/{game_id}/delete")
async def delete_game(
    request: Request,
    game_id: int,
    db: Session = Depends(get_db)
):
    """Delete a game and its moves"""
    try:
        user = await get_current_user(db, request.cookies.get("access_token"))
        game = get_game(db, game_id)
        
        # Check if user is part of the game
        if user.id != game.player_x_id and user.id != game.player_o_id:
            raise HTTPException(status_code=403, detail="You are not part of this game")
        
        # Delete all moves
        db.query(Move).filter(Move.game_id == game_id).delete()
        
        # Delete the game
        db.delete(game)
        db.commit()
        
        # Get referer to return to the page from which the delete was initiated
        referer = request.headers.get("referer", "/games")
        
        # If the referrer is the game page itself, redirect to the games list
        if f"/games/{game_id}" in referer:
            return RedirectResponse(url="/games", status_code=status.HTTP_303_SEE_OTHER)
        
        # Otherwise return to the referring page (either home page or games list)
        return RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)
    except:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

# Make move in game
@router.post("/games/{game_id}/moves", response_class=HTMLResponse)
async def make_game_move(
    request: Request,
    game_id: int,
    db: Session = Depends(get_db)
):
    """Make a move in the game from web interface"""
    try:
        user = await get_current_user(db, request.cookies.get("access_token"))
        
        # Parse the move data from form
        form_data = await request.form()
        row = int(form_data.get("row"))
        col = int(form_data.get("col"))
        
        # Получаем игру и текущее состояние доски
        game = get_game(db, game_id)
        board, move_count = get_board_state(db, game_id)
        current_player = "X" if move_count % 2 == 0 else "O"
        
        # Проверяем, играет ли пользователь против специального игрока (Player 1 или Player 2)
        is_special_opponent = False
        if game.player_o_id:
            opponent = db.query(User).filter(User.id == game.player_o_id).first()
            if opponent and opponent.username in ["player1", "player2"]:
                is_special_opponent = True
        
        # Определяем, кто делает ход
        move_user_id = user.id
        if is_special_opponent:
            # Если игра против Player 1 или Player 2, пользователь может ходить за обоих
            if current_player == "X":
                move_user_id = game.player_x_id
            else:
                move_user_id = game.player_o_id
        
        # Make the move
        move = make_move(db, game_id, move_user_id, row, col)
        
        # If it's a bot game, let the bot make a move
        game = get_game(db, game_id)
        if game.is_bot_game and game.status == "in_progress":
            try:
                bot_move = handle_bot_move(db, game_id)
                # Commit changes to ensure bot move is saved
                if bot_move:
                    db.commit()
            except Exception as bot_error:
                print(f"Bot move error: {str(bot_error)}")
                # Continue game flow even if bot move failed
        
        return RedirectResponse(
            url=f"/games/{game_id}", 
            status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as e:
        # Get game and board state for rendering with error
        game = get_game(db, game_id)
        gameboard = get_game_with_board(db, game_id)
        
        # Проверяем, играет ли пользователь против специального игрока (Player 1 или Player 2)
        is_special_opponent = False
        if game.player_o_id:
            opponent = db.query(User).filter(User.id == game.player_o_id).first()
            if opponent and opponent.username in ["player1", "player2"]:
                is_special_opponent = True
        
        # Determine if current user can play
        can_play = False
        if game.status == "in_progress":
            if is_special_opponent:
                # Если игра против Player 1 или Player 2, пользователь может ходить за обоих
                can_play = True
            elif gameboard.current_player == "X" and game.player_x_id == user.id:
                can_play = True
            elif gameboard.current_player == "O" and game.player_o_id == user.id:
                can_play = True
        
        return render_template(
            request, 
            "game.html", 
            {
                "user": user,
                "game": game,
                "board": gameboard.board,
                "current_player": gameboard.current_player,
                "can_play": can_play,
                "is_special_opponent": is_special_opponent,
                "error": str(e)
            }
        )