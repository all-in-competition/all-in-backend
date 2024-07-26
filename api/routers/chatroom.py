from typing import List

from api.db import get_db
from api.schemas.chatroom import PrivateChatroom, PublicChatroom
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from api.cruds.chatroom import get_private_chatrooms, get_public_chatroom, is_chatroom_member

router = APIRouter(prefix="/chatrooms", tags=["chatrooms"])


@router.get("/private")
async def read_private_chatrooms(post_id: int, request: Request, db: Session = Depends(get_db)) -> List[PrivateChatroom]:
    user_id = request.session.get('user', {}).get('id')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    personal_chatrooms = get_private_chatrooms(db, post_id, user_id)
    return personal_chatrooms


@router.get("/public")
async def read_public_chatroom(post_id: int, request: Request, db: Session = Depends(get_db)) -> PublicChatroom:
    user_id = request.session.get('user', {}).get('id')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not authenticated")

    public_chatroom = get_public_chatroom(db, post_id, user_id)
    return public_chatroom
