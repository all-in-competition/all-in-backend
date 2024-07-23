from typing import Optional

from sqlalchemy.orm import Session
from api.models.model import Chatroom, member_chatroom, Member


def get_chatroom(db: Session, chatroom_id: int) -> Optional[Chatroom]:
    return db.query(Chatroom).filter(chatroom_id == Chatroom.id).first()


def is_chatroom_member(db: Session, chatroom_id: int, member_id: int) -> bool:
    return db.query(member_chatroom).filter_by(chatroom_id=chatroom_id, member_id=member_id).first() is not None


def add_member_to_chatroom(db: Session, chatroom_id: int, member_id: int):
    chatroom = db.query(Chatroom).filter(chatroom_id == Chatroom.id).first()
    member = db.query(Member).filter(member_id == Member.id).first()
    chatroom.member.append(member)
    db.commit()
