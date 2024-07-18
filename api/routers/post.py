from api.models.member import Post
from fastapi import APIRouter, Query, Depends, HTTPException
from api.db import get_db
from api.models.model import Post as PostModel, Tag
from api.schemas.post import PostCreate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from api.cruds import post as crud_post

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("")
async def get_posts(db: Session = Depends(get_db)):
    try:
        return crud_post.get_posts(db)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("")
async def create_post(post:PostCreate, db: Session = Depends(get_db)):
    try:
        return crud_post.create_post(db, post)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))