from typing import Sequence, Union, List
from api.models.model import Post, Tag, Like, resume_tag
from api.schemas.like import LikeResponse
from api.schemas.tag import TagCreate
from fastapi import HTTPException
from fastapi_pagination.cursor import CursorParams
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from api.schemas.post import PostCreate, PostSummaryResponse, PostDetailResponse, PostResponse
from starlette import status
from fastapi_pagination.ext.sqlalchemy import paginate


def get_tags(db: Session, params: CursorParams):
    query = db.query(Tag)
    return query

def get_tag(tag_id: int, db: Session) -> Tag:
    try:
        target_tag = db.query(Tag).filter_by(id=tag_id).first()
        if target_tag is None:
            raise HTTPException(status_code=404, detail=f"Tag with id {tag_id} not found")

        db_tag = Tag(
            name=target_tag.name,
            category_id=target_tag.category_id)

        return db_tag
    except SQLAlchemyError as e:
        raise HTTPException(e)



