import uvicorn
from fastapi import FastAPI
from api.routers import task, done, login
from starlette.middleware.sessions import SessionMiddleware
from api.configs.app_config import settings

app = FastAPI(root_path="/api")
app.include_router(task.router)
app.include_router(done.router)
app.include_router(login.router)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

@app.get("/hello")
async def hello():
  return {"message": "hello world!"}

if __name__ == "__main__":
  uvicorn.run(app, host="127.0.0.1", port=8000)