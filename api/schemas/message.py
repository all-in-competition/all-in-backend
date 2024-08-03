from pydantic import BaseModel


class MessageEvent(BaseModel):
    chatroom_id: int
    member_id: int
    contents: str


class MessageLog(BaseModel):
    sender_name: str
    member_id: int
    contents: str
