import uvicorn
from fastapi import FastAPI
from api.routers import login, post, resume, alarm, websocket, chatroom
from starlette.middleware.sessions import SessionMiddleware
from api.configs.app_config import settings
from fastapi_pagination import add_pagination

app = FastAPI(root_path="/api")
app.include_router(login.router)
app.include_router(post.router)
app.include_router(resume.router)
app.include_router(alarm.router)
app.include_router(websocket.router)
app.include_router(chatroom.router)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

add_pagination(app)

if __name__ == "__main__":
  uvicorn.run(app, host="127.0.0.1", port=8000)