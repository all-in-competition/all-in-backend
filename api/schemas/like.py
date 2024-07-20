from pydantic import BaseModel, Field


class LikeResponse(BaseModel):
    post_id: int
    user_id: int
    is_liked: bool
