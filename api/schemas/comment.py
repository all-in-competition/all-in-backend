from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
  post_id : int
  user_id : int
  content : str
  status : str
  create_at : datetime

class CommentUpdate(BaseModel):
  content : str
  status : str
  update_at : datetime
