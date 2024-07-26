from typing import Optional, List

from api.schemas.chatroom import PrivateChatroom, PublicChatroom
from fastapi import HTTPException, status
from sqlalchemy import exists, and_, or_, case
from sqlalchemy.orm import Session, aliased
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
    post_info = db.query(Post.author_id, Chatroom.id.label('public_chatroom_id')).join(
        Chatroom, (Post.id == Chatroom.post_id) & (Chatroom.chat_type == 'public')
    ).filter(Post.id == post_id).first()

    post_author_id = post_info.author_id
    public_chatroom_id = post_info.public_chatroom_id

    # 팀원 여부를 확인하는 서브쿼리
    is_teammate_subquery = (
        # member_chatroom 테이블을 쿼리함
        db.query(member_chatroom)
        # chatroom_id가 public_chatroom_id와 일치하는 행을 필터링
        .filter_by(chatroom_id=public_chatroom_id)
        # member_id가 현재 쿼리에서 사용 중인 Member 테이블의 id와 일치하는 행을 필터링
        .filter_by(member_id=Member.id)
        # Member 테이블과 상관되도록 설정
        .correlate(Member)
        # 조건을 만족하는 행이 존재하는지 확인
        .exists()
    )

    query = (
        db.query(
            Chatroom.id.label("chatroom_id"),
            member_chatroom.c.member_id.label("member_id"),
            Member.nickname.label("member_name"),
            is_teammate_subquery.label("is_teammate")
        )
        .join(member_chatroom, Chatroom.id == member_chatroom.c.chatroom_id)
        .join(Member, Member.id == member_chatroom.c.member_id)
        .filter('private' == Chatroom.chat_type, post_id == Chatroom.post_id)
    )

    query = query.filter(
        or_(
            # 작성자인 경우 작성자를 제외하고 다른 팀원들의 채팅방을 가져오기 위한 조건
            and_(member_id == post_author_id, member_chatroom.c.member_id != member_id),
            # 작성자가 아닌 경우, 본인의 채팅방만 가져오기 위한 조건
            and_(member_id != post_author_id, member_chatroom.c.member_id == member_id)
        )
    )

    chatrooms_filtered = query.all()

    return [
        PrivateChatroom(
            chatroom_id=chatroom.chatroom_id,
            member_id=chatroom.member_id,
            member_name=chatroom.member_name,
            chat_type="private",
            is_teammate=chatroom.is_teammate,
        )
        for chatroom in chatrooms_filtered
    ]


def get_public_chatroom(db: Session, post_id: int, member_id: int) -> PublicChatroom:
    public_chatroom = db.query(Chatroom).filter_by(post_id=post_id, chat_type="public").first()
    if public_chatroom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Public chatroom not found")

    if not is_chatroom_member(db, public_chatroom.id, member_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member is not teammate")

    return PublicChatroom(
        chatroom_id=public_chatroom.id,
        chat_type="public"
    )


def create_chatroom(db: Session, post_id: int, chat_type: str, user_id: Optional[int]):
    # 채팅방 만들고
    chatroom = Chatroom(post_id=post_id, chat_type=chat_type)
    db.add(chatroom)
    db.flush()
    db.refresh(chatroom)

    # 작성자를 추가한다
    author = db.query(Member).join(Post, post_id == Post.id).filter(Member.id == Post.author_id).first()
    if author is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    if is_chatroom_member(db, chatroom.id, author.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Author already participated")
    chatroom.member.append(author)

    # 채팅 타입이 private 인 경우, 질문자도 추가한다
    if chatroom.chat_type == "private":
        questioner = db.query(Member).filter(Member.id == user_id).first()
        if questioner is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        if is_chatroom_member(db, chatroom.id, questioner.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Member already participated")

        # public chatroom 찾기
        public_chatroom = db.query(Chatroom).filter_by(post_id=post_id, chat_type="public").first()
        if public_chatroom is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Public chatroom not found")

        # 사용자가 public chatroom의 멤버인지 확인
        is_teammate = db.query(member_chatroom).filter_by(
            chatroom_id=public_chatroom.id,
            member_id=user_id
        ).first() is not None

        chatroom.member.append(questioner)
        db.commit()
        return PrivateChatroom(
            chatroom_id=chatroom.id,
            member_id=questioner.id,
            member_name=questioner.nickname,
            chat_type=chatroom.chat_type,
            is_teammate=is_teammate
        )
    elif chatroom.chat_type == "public":
        db.commit()
        return PublicChatroom(
            chatroom_id=chatroom.id,
            chat_type=chatroom.chat_type
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid chatroom type")