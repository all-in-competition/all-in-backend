from typing import List

from api.cruds.message import get_messages
from api.cruds.post import is_post_author
from api.db import get_db
from api.schemas.chatroom import PrivateChatroom, PublicChatroom
from api.schemas.message import MessageLog
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi_pagination.cursor import CursorParams, CursorPage
from sqlalchemy.orm import Session
from api.cruds.chatroom import get_private_chatrooms, get_public_chatroom, get_chatroom, create_chatroom

router = APIRouter(prefix="/chatrooms", tags=["chatrooms"])


@router.get("/private")
async def read_private_chatrooms(post_id: int, request: Request, db: Session = Depends(get_db))\
        -> List[PrivateChatroom]:
    user_id = request.session.get('user', {}).get('id')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    personal_chatrooms = get_private_chatrooms(db, post_id, user_id)
    return personal_chatrooms


@router.post("/private")
async def post_private_chatroom(post_id: int, request: Request, db: Session = Depends(get_db)) -> PrivateChatroom:
    user_id = request.session.get('user', {}).get('id')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if is_post_author(db, post_id, user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author can't create chatroom")

    private_chatroom = create_chatroom(db, post_id, "private", user_id)
    return private_chatroom


@router.get("/public")
async def read_public_chatroom(post_id: int, request: Request, db: Session = Depends(get_db)) -> PublicChatroom:
    user_id = request.session.get('user', {}).get('id')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    public_chatroom = get_public_chatroom(db, post_id, user_id)
    return public_chatroom


@router.get("/{chatroom_id}/messages")
async def read_messages(chatroom_id: int, request: Request, db: Session = Depends(get_db),
                        params: CursorParams = Depends()) -> CursorPage[MessageLog]:
    chatroom = get_chatroom(db, chatroom_id)
    if chatroom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatroom not found")

    user_id = request.session.get('user', {}).get('id')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return get_messages(db, chatroom_id, user_id, params)
