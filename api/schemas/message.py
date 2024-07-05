from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
  chatroom_id : int
  member_id : int
  content : str
  create_at : datetime