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


class PostUpdate(BaseModel):
  category_id : int
  title : str
  contents : str
  update_at : datetime
  deadLine : datetime
  max_member : int
