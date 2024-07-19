from fastapi import APIRouter, Query, Depends, HTTPException, Request
from api.db import get_db
from api.models.model import Resume as ResumeModel
from api.schemas.resume import ResumeUpdate, ResumeResponse
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from api.cruds import resume as crud_resume
from starlette.responses import JSONResponse

router = APIRouter(prefix="/resumes", tags=["resumes"])

# @router.get("")
# async def get_posts(db: Session = Depends(get_db)):
#     try:
#         return crud_resume.get_posts(db)
#     except SQLAlchemyError as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/update/{resume_id}")
async def update_resume(id: int=1, content: str = "test", public: bool = True, db: Session = Depends(get_db)):
    try:
        crud_resume.update_resume(id, content, public, db)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return JSONResponse({"message": "update successful"})

