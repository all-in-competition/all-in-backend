from api.schemas.like import LikeResponse
from fastapi import APIRouter, Depends, HTTPException, Request
from api.db import get_db
from api.schemas.post import PostCreate, PostDetailResponse, PostSummaryResponse, PostUpdate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from api.cruds import post as crud_post
from fastapi_pagination.cursor import CursorPage, CursorParams
from starlette.responses import JSONResponse

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("")
async def get_posts(db: Session = Depends(get_db), params: CursorParams = Depends()) -> CursorPage[PostSummaryResponse]:
    try:
        return crud_post.get_posts(db, params)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/like")
async def get_posts_like(db: Session = Depends(get_db), params: CursorParams = Depends()) -> CursorPage[PostSummaryResponse]:
    try:
        return crud_post.get_posts_like(db, params)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{post_id}")
async def get_post(post_id: int, db: Session = Depends(get_db)) -> PostDetailResponse:
    try:
        return crud_post.get_post(post_id, db)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("")
async def create_post(request: Request, post: PostCreate, db: Session = Depends(get_db)):
    try:
        user_id = request.session.get("user", {}).get("id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        return crud_post.create_post(db, post, user_id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{post_id}/like")
async def toggle_like_post(request: Request, post_id: int, db: Session = Depends(get_db)) -> LikeResponse:
    try:
        current_user_id = request.session['user']['id']
        result = crud_post.toggle_like_post(post_id, current_user_id, db)
        return result
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{post_id}/update")
async def update_post(request: Request, post: PostUpdate, db: Session = Depends(get_db)):
    try:
        user_info = request.session["user"]
        return crud_post.update_post(db, post, user_info)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
