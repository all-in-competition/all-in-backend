from pydantic import BaseModel


class PrivateChatroom(BaseModel):
    chatroom_id: int
    member_id: int
    member_name: str
    chat_type: str
    is_teammate: bool


class PublicChatroom(BaseModel):
    chatroom_id: int
    chat_type: str
