from api.db import get_db
from api.schemas.alarm import AlarmCreate, AlarmSummaryResponse
from api.schemas.member import MemberCreate
from api.cruds import alarm as crud_alarm
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi_pagination.cursor import CursorParams, CursorPage
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

router = APIRouter(prefix="/alarm", tags=["alarm"])

@router.post('/')
async def create_alarm(alarm: AlarmCreate, db: Session = Depends(get_db)):
    try:
        crud_alarm.create_alarm(db, alarm)
    except SQLAlchemyError as e:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return JSONResponse({"message": "Alarm created successful"})


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
        return crud_alarm.get_alarm(alarm_id, db    )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
