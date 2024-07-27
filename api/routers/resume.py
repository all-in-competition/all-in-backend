from fastapi import APIRouter, Query, Depends, HTTPException, Request
from api.db import get_db
from api.models.model import Resume as ResumeModel
from api.schemas.resume import ResumeUpdate, ResumeResponse, ResumeSummaryResponse
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from api.cruds import resume as crud_resume
from starlette.responses import JSONResponse
from fastapi_pagination.cursor import CursorPage, CursorParams

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.get("")
async def get_resumes(db: Session = Depends(get_db), params: CursorParams = Depends()) \
        -> CursorPage[ResumeSummaryResponse]:
    try:
        return crud_resume.get_resumes(db, params)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{resume_id}")
async def get_resume(resume_id: int, db: Session = Depends(get_db)):
    try:
        return crud_resume.get_resume(resume_id, db)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/me")
async def update_resume(request: Request, new: ResumeUpdate, db: Session = Depends(get_db)):
    try:
        user_info = request.session["user"]
        if user_info is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        crud_resume.update_resume(new, db, user_info)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return JSONResponse({"message": "update successful"})
