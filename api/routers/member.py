from api.cruds.post import get_likes_posts
from api.schemas.post import PostSummaryResponse
from fastapi import APIRouter, Depends, HTTPException, Request
from api.db import get_db
from fastapi_pagination.cursor import CursorParams, CursorPage
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from api.cruds import member as crud_member

router = APIRouter(prefix="/members", tags=["member"])


@router.put("me/nickname")
async def update_nickname(request: Request, new_name: str, db: Session = Depends(get_db)):
    try:
        user_id = request.session.get("user", {}).get("id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        return crud_member.update_nickname(db, new_name, user_id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me/likes")
async def read_likes_posts(request: Request, db: Session = Depends(get_db), params: CursorParams = Depends())\
        -> CursorPage[PostSummaryResponse]:
    user_id = request.session.get("user", {}).get("id")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return get_likes_posts(db, user_id, params)
