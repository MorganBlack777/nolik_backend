import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, users, games, web, api
from app.database.db import Base, engine, init_db

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Крестики-нолики API",
    description="API для веб-приложения Крестики-нолики (Tic-Tac-Toe)",
    version="1.0.0"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent, "app", "static")), name="static")

# Include API routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(games.router, prefix="/api")

# Include web routers
app.include_router(web.router)
app.include_router(api.router)

# Initialize database
init_db()

# Redirect root to API docs
@app.get("/docs", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

# Redirect API root to docs
@app.get("/api", include_in_schema=False)
def redirect_api_to_docs():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 