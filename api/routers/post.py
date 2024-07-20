from fastapi import APIRouter, Depends, HTTPException, Request
from api.db import get_db
from api.schemas.post import PostCreate, PostDetailResponse, PostSummaryResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from api.cruds import post as crud_post
from fastapi_pagination.cursor import CursorPage, CursorParams

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("")
async def get_posts(db: Session = Depends(get_db), params: CursorParams = Depends()) -> CursorPage[PostSummaryResponse]:
    try:
        return crud_post.get_posts(db, params)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{post_id}")
async def get_post(post_id: int, db: Session = Depends(get_db)) -> PostDetailResponse:
    try:
        return crud_post.get_post(post_id, db)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("")
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    try:
        return crud_post.create_post(db, post)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{post_id}/like")
async def like_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    try:
        current_user_id = request.session['user']
        crud_post.like_post(post_id, current_user_id, db)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
