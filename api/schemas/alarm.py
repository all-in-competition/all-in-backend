from pydantic import BaseModel, Field


class AlarmCreate(BaseModel):
  sender_id : int
  receiver_id : int
  post_id : int
  type : int