from api.db import get_db
from api.models.model import Alarm, Post
from api.routers.websocket import broadcast
from api.schemas.alarm import AlarmCreate, AlarmSummaryResponse, Confirm
from api.schemas.member import MemberCreate
from api.cruds import alarm as crud_alarm
from api.cruds import chatroom as crud_chatroom
from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Depends, status, WebSocketException, Request, HTTPException
from fastapi_pagination.cursor import CursorParams, CursorPage
import asyncio
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

router = APIRouter(prefix="/alarm", tags=["alarm"])


async def create_alarm(alarm: AlarmCreate, db: Session ):
    try:
        crud_alarm.create_alarm(db, alarm)
    except SQLAlchemyError as e:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return JSONResponse({"message": "Alarm created successful"})


# 메시지 전송 함수
@router.post("/")
async def send_alarm(alarm: AlarmCreate, db: Session = Depends(get_db)):
    try :
        #data = await websocket.receive_text()  # 클라이언트로부터 메시지 내용 수신
        new_alarm = AlarmCreate(sender_id=alarm.sender_id, receiver_id=alarm.receiver_id, post_id=alarm.post_id, type=alarm.type)
        await create_alarm(new_alarm, db)  # 메시지를 데이터베이스에 저장
        await broadcast.publish(channel=str(new_alarm.receiver_id), message=new_alarm.json())  # 수신자에게 메시지 방송
    except SQLAlchemyError as e:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# 메시지 수신 함수
async def receive_alarm(websocket: WebSocket, receiver_id: int):
    async with broadcast.subscribe(channel=str(receiver_id)) as subscriber:
        while True :
            try :
                async for alarm in subscriber:
                    message_event = AlarmCreate.parse_raw(alarm.message)
                    await websocket.send_json(message_event.dict())  # 수신자에게 메시지 전달'
            except WebSocketDisconnect:
                break

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,  db: Session = Depends(get_db)):
    await websocket.accept()  # 웹소켓 연결 수락
    receiver_id = websocket.session.get('user').get('id')
    receive_task = asyncio.create_task(receive_alarm(websocket, receiver_id))

    try:
        await receive_task
    except WebSocketDisconnect:
        receive_task.cancel()
        await websocket.close()

@router.get('/')
async def get_alarms(request: Request, db: Session = Depends(get_db), params: CursorParams = Depends()) -> CursorPage[AlarmSummaryResponse]:
    try:
        user_info = request.session["user"]
        return crud_alarm.get_alarms(db, params, user_info)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get('/{alarm_id}')
async def get_alarm(alarm_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        current_id = request.session['user']['id']
        target = db.query(Alarm).filter_by(id = alarm_id).first()
        if (current_id == target.receiver_id):
            return crud_alarm.get_alarm(alarm_id, db)
        else:
            return JSONResponse({"message": "no permission"})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post('/confirm')
async def confirm(confirm: Confirm, request: Request, db: Session = Depends(get_db)):
    try:
        current_id = request.session['user']['id']
        target = db.query(Post).filter_by(id=confirm.post_id).first()
        if (current_id == target.author_id):
            chatroom_id = 1
            return crud_chatroom.add_member_to_chatroom(db, chatroom_id, confirm.sender_id)
        else:
            return JSONResponse({"message": "no permission"})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))