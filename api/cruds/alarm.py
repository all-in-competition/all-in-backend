from typing import Union, Sequence

from api.schemas.member import MemberCreate
from fastapi import HTTPException
from api.models.model import Alarm
from api.schemas.alarm import AlarmCreate, AlarmSummaryResponse, AlarmDetailResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.cursor import CursorParams
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status


def create_alarm(db: Session, alarm: AlarmCreate):
    try:
        new_alarm = Alarm(
            sender_id= alarm.sender_id,
            receiver_id = alarm.receiver_id,
            post_id = alarm.post_id,
            type =  alarm.type
        )
        db.add(new_alarm)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e
        
def alarm_to_summary_response(alarms: Sequence[Alarm]) -> Union[Sequence[AlarmSummaryResponse], None]:
    return [AlarmSummaryResponse(
        sender_name= alarm.sender.nickname,
        post_title= alarm.post.title,
        post_id= alarm.post.id,
        alarm_id = alarm.id
    )for alarm in alarms]

def get_alarms(db: Session, params: CursorParams, user_info: MemberCreate):
    db_alarm_list = db.query(Alarm).filter(Alarm.receiver_id == user_info['id']).order_by(Alarm.create_at.desc())
    return paginate(db_alarm_list, params, transformer=alarm_to_summary_response)

def get_alarm(id: int, db: Session):
    try:
        db_alarm = db.query(Alarm).filter(id == Alarm.id).first()
        if db_alarm is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='alarm not found')
        AlarmDetail = AlarmDetailResponse(
            sender_id=db_alarm.sender_id,
            sender_name=db_alarm.sender.nickname,
            reciver_name=db_alarm.receiver.nickname,
            post_title=db_alarm.post.title,
            post_id=db_alarm.post.id,
            create_at=db_alarm.create_at
        )

        return AlarmDetail
    except SQLAlchemyError as e:
        raise HTTPException(e)