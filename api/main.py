import uvicorn
from fastapi import FastAPI
from api.routers import task, done, login
# from .models.model import Comment

# print(Comment())

app = FastAPI()
app.include_router(task.router)
app.include_router(done.router)
app.include_router(login.router)


@app.get("/hello")
async def hello():
  return {"message": "hello world!"}

if __name__ == "__main__":
  uvicorn.run(app, host="127.0.0.1", port=8000)