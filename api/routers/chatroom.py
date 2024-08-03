from typing import List, Dict

from redis.asyncio import Redis
from api.cruds.message import get_messages, get_messages_cache
from api.cruds.post import is_post_author
from api.db import get_db, get_db_async
from api.models.model import Message, Member
from api.schemas.chatroom import PrivateChatroom, PublicChatroom, ExitChatroom
from api.schemas.message import MessageLog, MessageEvent
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi_pagination.cursor import CursorParams, CursorPage
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from api.cruds.chatroom import get_private_chatrooms, get_public_chatroom, get_chatroom, create_chatroom, \
    exit_member_to_chatroom

redis_client = Redis.from_url("redis://localhost:6379/0")

router = APIRouter(prefix="/chatrooms", tags=["chatrooms"])



async def get_messages_from_db(chatroom_id: int, db: Session) -> List[MessageLog]:
    messages = db.query(Message).filter(Message.chatroom_id == chatroom_id).all()
    return [MessageLog(
                    sender_name= message.member.nickname,  # 예시로 사용자 이름을 설정
                    member_id=message.member_id,
                    contents=message.contents
                ) for message in messages]

async def cache_messages(chatroom_id: int, messages: List[MessageLog]):
    key = f"chatroom:{chatroom_id}:messages"
    serialized_messages = [message.json() for message in messages]
    await redis_client.rpush(key, *serialized_messages)
    await redis_client.expire(key, 60)  # 캐시 만료 시간 설정 (예: 1시간)

async def get_chat_history(chatroom_id: int, db: Session):
    messages_from_db = await get_messages_from_db(chatroom_id, db)
    if messages_from_db:
        await cache_messages(chatroom_id, messages_from_db)

async def get_chat_history_from_redis(chatroom_id: int, limit: int = 100) -> List[MessageLog]:
    key = f"chatroom:{chatroom_id}:messages"
    messages = await redis_client.lrange(key, -limit, -1)
    if not messages:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="noting")
    else:
        return [MessageLog.parse_raw(message) for message in reversed(messages)]


@router.get("/private")
async def read_private_chatrooms(post_id: int, request: Request, db: Session = Depends(get_db)) \
        -> List[PrivateChatroom]:
    user_id = request.session.get('user', {}).get('id')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    personal_chatrooms = get_private_chatrooms(db, post_id, user_id)
    return personal_chatrooms


@router.post("/private")
async def post_private_chatroom(post_id: int, request: Request, db: Session = Depends(get_db)) -> PrivateChatroom:
    user_id = request.session.get('user', {}).get('id')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if is_post_author(db, post_id, user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author can't create chatroom")

    private_chatroom = create_chatroom(db, post_id, "private", user_id)
    return private_chatroom


@router.get("/public")
async def read_public_chatroom(post_id: int, request: Request, db: Session = Depends(get_db)) -> PublicChatroom:
    user_id = request.session.get('user', {}).get('id')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    public_chatroom = get_public_chatroom(db, post_id, user_id)
    return public_chatroom


@router.get("/{chatroom_id}/messages")
async def read_messages(chatroom_id: int, request: Request, db: Session = Depends(get_db),
                        params: CursorParams = Depends()) -> CursorPage[MessageLog]:
    chatroom = get_chatroom(db, chatroom_id)
    if chatroom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatroom not found")

    user_id = request.session.get('user', {}).get('id')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return get_messages(db, chatroom_id, user_id, params)

@router.post("/exit")
async def exit(request: Request, exit: ExitChatroom, db: Session = Depends(get_db)):
    current_id = request.session.get('user', {}).get('id')
    if current_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return exit_member_to_chatroom(db, exit.chatroom_id, exit.member_id, current_id)

@router.get("/cached-messages")
async def read_cached_messages(request: Request, chatroom_id: int,db: Session = Depends(get_db), params: CursorParams = Depends()) -> CursorPage[MessageLog]:
    user_id = request.session.get('user', {}).get('id')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        key = f"chatroom:{chatroom_id}:messages"
        print(key)
        if not await redis_client.exists(key):
            await get_chat_history(chatroom_id, db)
        chat_history = await get_chat_history_from_redis(chatroom_id)
        return CursorPage(items=chat_history, total=len(chat_history), params=params)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving messages: {str(e)}")