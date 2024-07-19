import uvicorn
from fastapi import FastAPI
from api.routers import login, post
from starlette.middleware.sessions import SessionMiddleware
from api.configs.app_config import settings

app = FastAPI(root_path="/api")
app.include_router(login.router)
app.include_router(post.router)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

if __name__ == "__main__":
  uvicorn.run(app, host="127.0.0.1", port=8000)