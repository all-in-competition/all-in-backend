from api.models.model import Message
from api.schemas.message import MessageEvent
from sqlalchemy.orm import Session


def save_message(db: Session, event: MessageEvent):
    db_message = Message(**event.model_dump())
    db.add(db_message)
    db.commit()