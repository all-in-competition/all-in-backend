from fastapi import APIRouter, Query, Depends, HTTPException, Request
from api.db import get_db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from api.cruds import member as crud_member
router = APIRouter(prefix="/member", tags=["member"])

@router.put("/nickname")
async def update_nickname(request: Request, new_name: str, db: Session = Depends(get_db)):
    try:
        user_id = request.session["user"]["id"]
        return crud_member.update_nickname(db, new_name, user_id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

