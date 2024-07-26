from typing import Union, Sequence
from api.models.model import Message
from api.schemas.message import MessageEvent, MessageLog
from fastapi_pagination.cursor import CursorParams
from sqlalchemy.orm import Session
from fastapi_pagination.ext.sqlalchemy import paginate


def save_message(db: Session, event: MessageEvent):
    db_message = Message(**event.model_dump())
    db.add(db_message)
    db.commit()


def get_messages(db: Session, chatroom_id: int, user_id: int, params: CursorParams):
    query = db.query(Message).filter(chatroom_id == Message.chatroom_id).order_by(Message.create_at.desc())
    return paginate(query, params, transformer=lambda messages: message_to_message_log(messages, user_id))


def message_to_message_log(messages: Sequence[Message], user_id: int) -> Union[Sequence[MessageLog], None]:
    return [MessageLog(
        sender_name=message.member.nickname,
        is_mine=message.member_id == user_id,
        contents=message.contents
    ) for message in messages]
