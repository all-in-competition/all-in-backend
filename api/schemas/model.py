from pydantic import BaseModel, Field


class MemberCreate(BaseModel):
  id : int
  provider_id : int
  provider_type: str
  nickname: str
  status: str

class ResuemUpdate(BaseModel):
  member_id : int
  contents : str
  public : bool

class PostCreate(BaseModel):
  author_id : int
  category_id : int
  title : str
  contents : str
  create_at : datetime
  deadLine : datetime
  max_member : int

class PostUpdate(BaseModel):
  category_id : int
  title : str
  contents : str
  update_at : datetime
  deadLine : datetime
  max_member : int

class LikeCreate(BaseModel):
  post_id : int
  user_id : int

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

class AlarmCreate(BaseModel):
  sender_id : int
  receiver_id : int
  post_id : int
  type : int

class MessageCreate(BaseModel):
  chatroom_id : int
  member_id : int
  content : str
  create_at : datetime