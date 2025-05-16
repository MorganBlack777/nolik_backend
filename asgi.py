from main import app as fastapi_app

app = fastapi_app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("asgi:app", host="0.0.0.0", port=8000, reload=False) 