from pydantic import BaseModel, Field


class PostCreate(BaseModel):
  author_id : int
  category_id : int
  title : str
  contents : str
  create_at : datetime
  deadLine : datetime
  max_member : int
  tag


class PostUpdate(BaseModel):
  category_id : int
  title : str
  contents : str
  update_at : datetime
  deadLine : datetime
  max_member : int
