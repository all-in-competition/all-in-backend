import asyncio

from api.models.model import Member
from api.routers.chatroom import get_chat_history
from redis.asyncio import Redis
from api.configs.app_config import settings
from api.schemas.message import MessageEvent, MessageLog
from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Depends, status, WebSocketException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from broadcaster import Broadcast
from api.db import get_db, get_db_async
from api.cruds.chatroom import get_chatroom, is_chatroom_member, add_member_to_chatroom
from api.cruds.post import is_post_author
from api.cruds.message import save_message

broadcast = Broadcast(settings.REDIS_URL)
router = APIRouter(tags=["chat"])

redis_client = Redis.from_url("redis://localhost:6379/0")


async def save_message_to_redis(chatroom_id: int, message: MessageLog, ttl: int = 600):
    key = f"chatroom:{chatroom_id}:messages"
    async with redis_client.pipeline(transaction=True) as pipe:
        await pipe.rpush(key, message.json())
        await pipe.expire(key, ttl)  # TTL 설정
        await pipe.execute()

async def receive_message(websocket: WebSocket, member_id: int, chatroom_id: int):
    async with broadcast.subscribe(channel=str(chatroom_id)) as subscriber:
        async for event in subscriber:
            print(event.message)
            message_event = MessageEvent.parse_raw(event.message)
            if message_event.member_id != member_id:
                await websocket.send_json(message_event.dict())


async def send_message(websocket: WebSocket, member_id: int, chatroom_id: int, db: Session):
    data = await websocket.receive_text()
    event = MessageEvent(chatroom_id=chatroom_id, member_id=member_id, contents=data)
    log = MessageLog(sender_name= db.query(Member).filter(Member.id == member_id).first().nickname,
                     member_id= member_id,
                     contents=data)
    key = f"chatroom:{chatroom_id}:messages"

    save_message(db, event)
    if not await redis_client.exists(key):
        await get_chat_history(chatroom_id, db)
    await save_message_to_redis(chatroom_id, log)  # Redis에 메시지 저장

    await broadcast.publish(channel=str(chatroom_id), message=event.json())

@router.websocket("/ws/{chatroom_id}")
async def websocket_endpoint(websocket: WebSocket, chatroom_id: int, db: Session = Depends(get_db)):
    await websocket.accept()

    # 사용자 로그인 상태 확인
    member_id = websocket.session.get('user', {}).get('id')
    if member_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Not authenticated")
        return

    # chatroom_id 확인
    db_chatroom = get_chatroom(db, chatroom_id)
    if db_chatroom is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Chatroom not found")
        return

    chat_type = db_chatroom.chat_type
    is_author = is_post_author(db, db_chatroom.post_id, member_id)
    is_member = is_chatroom_member(db, chatroom_id, member_id)

    if not is_member:
        if chat_type == "private":
            if is_author:
                # 게시글 작성자이지만 채팅방 멤버가 아닌 경우 에러 발생
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="Author of the post but not a member of the chat room")
            else:
                # 게시글 질문자인 경우 채팅방 인원 검사 후 추가
                # 채팅방 인원 검사 로직 추가 필요 (예: 채팅방 인원 제한 등)
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="Create private chatroom before chat"
                )
        elif chat_type == "public":
            if is_author:
                # 리더이지만 멤버가 아닌 경우 에러 발생
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="Author of the post but not a member of the chat room")
            else:
                # 팀원인 경우 채팅방에 추가
                add_member_to_chatroom(db, chatroom_id, member_id)
        else:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Unknown chat type")

    try:
        while True:
            receive_message_task = asyncio.create_task(
                receive_message(websocket, member_id, chatroom_id)
            )
            send_message_task = asyncio.create_task(send_message(websocket, member_id, chatroom_id, db))
            done, pending = await asyncio.wait(
                {receive_message_task, send_message_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            for task in done:
                task.result()
    except WebSocketDisconnect:
        pass


@router.on_event("startup")
async def startup():
    await broadcast.connect()


@router.on_event("shutdown")
async def shutdown():
    await broadcast.disconnect()
