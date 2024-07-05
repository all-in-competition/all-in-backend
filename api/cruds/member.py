from sqlalchemy.orm import Session
from sqlalchemy import and_
import api.models.model as member_model
from api.schemas.login import SessionData


def create_member(db: Session, member_create: SessionData):
    db.add(member_model.Member(**member_create.model_dump()))


def find_member(db: Session, user_info: SessionData):
    return db.query(member_model.Member).filter(and_(member_model.Member.provider_type == user_info.provider_type,
                                                     member_model.Member.provider_id == user_info.provider_id))
