from typing import Optional, List

from api.schemas.chatroom import PrivateChatroom, PublicChatroom
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from api.models.model import Chatroom, member_chatroom, Member, Post


def get_chatroom(db: Session, chatroom_id: int) -> Optional[Chatroom]:
    return db.query(Chatroom).filter(chatroom_id == Chatroom.id).first()


def is_chatroom_member(db: Session, chatroom_id: int, member_id: int) -> bool:
    return db.query(member_chatroom).filter_by(chatroom_id=chatroom_id, member_id=member_id).first() is not None


def add_member_to_chatroom(db: Session, chatroom_id: int, member_id: int):
    chatroom = db.query(Chatroom).filter(chatroom_id == Chatroom.id).first()
    member = db.query(Member).filter(member_id == Member.id).first()
    chatroom.member.append(member)
    db.commit()


def get_private_chatrooms(db: Session, post_id: int, member_id: int) -> List[PrivateChatroom]:
    post_author_id = db.query(Post.author_id).filter(post_id == Post.id).scalar()
    is_author = member_id == post_author_id

    query = (
        db.query(
            Chatroom.id.label("chatroom_id"),
            member_chatroom.c.member_id.label("member_id"),
            Member.nickname.label("member_name"),
            Chatroom.chat_type.label("chatroom_chat_type"),
            (member_chatroom.c.member_id == Post.author_id).label("is_teammate")
        )
        .join(member_chatroom, Chatroom.id == member_chatroom.c.chatroom_id)
        .join(Member, Member.id == member_chatroom.c.member_id)
        .join(Post, Post.id == Chatroom.post_id)
        .filter(
            'private' == Chatroom.chat_type,
            post_id == Chatroom.post_id,
            member_chatroom.c.member_id != Post.author_id
        )
    )

    if not is_author:
        query = query.filter(member_chatroom.c.member_id == member_id)

    chatrooms_filtered = query.all()

    return [PrivateChatroom(
        chatroom_id=chatroom.chatroom_id,
        member_id=chatroom.member_id,
        member_name=chatroom.member_name,
        chat_type="private",
        is_teammate=chatroom.is_teammate,
    ) for chatroom in chatrooms_filtered]


def get_public_chatroom(db: Session, post_id: int, member_id: int) -> PublicChatroom:
    public_chatroom = db.query(Chatroom).filter_by(post_id=post_id, chat_type="public").first()
    if public_chatroom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Public chatroom not found")

    if not is_chatroom_member(db, public_chatroom.id, member_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Member is not teammate")

    return PublicChatroom(
        chatroom_id=public_chatroom.id,
        chat_type="public"
    )
