from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import api.models.member as member_model
import api.schemas.member as member_schema


def create_member(db: Session, member_create: member_schema) -> member_model.Member:
  pass

