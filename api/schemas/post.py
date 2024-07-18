from typing import List

from pydantic import BaseModel, Field
from datetime import datetime

class PostCreate(BaseModel):
  author_id : int
  category_id : int
  title : str
  contents : str
  deadline : datetime
  max_member : int
  tags : List[str]

class PostResponse(BaseModel):
  post_id : int
  title : str
  tags : List[str]
  author_id : int
  create_at : datetime
  like_count : int
  current_member : int

class PostUpdate(BaseModel):
  category_id : int
  title : str
  contents : str
  update_at : datetime
  deadLine : datetime
  max_member : int
