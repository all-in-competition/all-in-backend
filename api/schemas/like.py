from pydantic import BaseModel, Field


class LikeCreate(BaseModel):
  post_id : int
  user_id : int
