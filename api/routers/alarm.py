import redis.asyncio as redis
import json
from api.db import get_db, get_db_async
from api.models.model import Alarm, Post
from api.schemas.alarm import AlarmCreate, AlarmSummaryResponse, Confirm
from api.cruds import alarm as crud_alarm
from api.cruds import chatroom as crud_chatroom
from api.routers.chat import broadcast
from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Depends, Request, \
    HTTPException
from fastapi_pagination.cursor import CursorParams, CursorPage
import asyncio
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
import time

router = APIRouter(prefix="/alarm", tags=["alarm"])
redis_client = redis.Redis(host='localhost', port=6379, db=0)

async def add_to_list(list_name: str, alarm: AlarmCreate):
    await redis_client.rpush(list_name, alarm.json())

async def get_from_list(list_name: str):
    return await redis_client.lpop(list_name)

async def create_alarm(alarm: AlarmCreate, db: AsyncSession):
    try:
        await asyncio.gather(
            crud_alarm.create_alarm(db, alarm),
            add_to_list(f"alarms_{alarm.receiver_id}", alarm)
        )
        return JSONResponse({"message": "Alarm created successfully"})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# 메시지 전송 함수
@router.post("/")
async def send_alarm(alarm: AlarmCreate, db: AsyncSession = Depends(get_db_async)):
    start_time = time.time()
    try:
        return await create_alarm(alarm, db)  # 데이터베이스에 알림 저장
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    finally:
        end_time = time.time()
        print(f"send_alarm took {end_time - start_time} seconds")


# 메시지 수신 함수
async def receive_alarm(websocket: WebSocket, receiver_id: int):
    list_name = f"alarms_{receiver_id}"

    while True:
        try:
            alarm_json = await get_from_list(list_name)
            if alarm_json:
                alarm = AlarmCreate.parse_raw(alarm_json)
                await websocket.send_json(alarm.dict())
        except WebSocketDisconnect:
            break
        await asyncio.sleep(1)  # Polling interval
    # async with broadcast.subscribe(channel=str(receiver_id)) as subscriber:
    #     while True:
    #         try:
    #             async for alarm in subscriber:
    #                 message_event = AlarmCreate.parse_raw(alarm.message)
    #                 await websocket.send_json(message_event.dict())  # 수신자에게 메시지 전달'
    #         except WebSocketDisconnect:
    #             break


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # 웹소켓 연결 수락
    receiver_id = websocket.session.get('user').get('id')
    receive_task = asyncio.create_task(receive_alarm(websocket, receiver_id))
    try:
        await receive_task
    except WebSocketDisconnect:
        receive_task.cancel()
        await websocket.close()


@router.get('/')
async def get_alarms(request: Request, db: Session = Depends(get_db), params: CursorParams = Depends())\
        -> CursorPage[AlarmSummaryResponse]:
    try:
        user_info = request.session.get("user")
        if user_info is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        return crud_alarm.get_alarms(db, params, user_info)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get('/{alarm_id}')
async def get_alarm(alarm_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        current_id = request.session.get('user', {}).get('id')
        if current_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        target = db.query(Alarm).filter_by(id=alarm_id).first()
        if current_id == target.receiver_id:
            return crud_alarm.get_alarm(alarm_id, db)
        else:
            return JSONResponse({"message": "no permission"})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post('/confirm')
async def confirm(confirm: Confirm, request: Request, db: Session = Depends(get_db)):
    try:
        current_id = request.session.get('user', {}).get('id')
        if current_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        target = db.query(Post).filter_by(id=confirm.post_id).first()
        if current_id == target.author_id:
            chatroom_id = int
            for chatroom in target.chatroom:
                if chatroom.chat_type == "public":
                    chatroom_id = chatroom.id
                    break
                else:
                    return JSONResponse({"message": "no public chatroom"})
            return crud_chatroom.add_member_to_chatroom(db, chatroom_id, confirm.sender_id)
        else:
            return JSONResponse({"message": "no permission"})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
