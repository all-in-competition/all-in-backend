from datetime import datetime

from pydantic import BaseModel, Field


class AlarmCreate(BaseModel):
      sender_id : int
      receiver_id : int
      post_id : int
      type : int

class AlarmSummaryResponse(BaseModel):
    sender_name : str
    post_title : str
    post_id : int
    alarm_id : int

class AlarmDetailResponse(BaseModel):
    sender_id : int
    sender_name : str
    reciver_name : str
    post_title : str
    post_id : int
    create_at : datetime

class Confirm(BaseModel):
    sender_id : int
    post_id : int