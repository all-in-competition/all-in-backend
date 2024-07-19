from api.models.model import Resume, Member, Tag
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from api.schemas import member as member_schema
from api.schemas.resume import ResumeCreate, ResumeUpdate, ResumeResponse
from sqlalchemy import update
from starlette import status


def create_resume(db: Session, uid: member_schema.MemberCreate):
    try:
        db_resume = Resume(
            member_id=uid.id,
            contents="",
            public=False
        )
        db.add(db_resume)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def update_resume(content: str, public: bool, db: Session, user_info: member_schema.MemberCreate):
    try:
        db_resume = db.query(Resume).filter_by(member_id=user_info["id"]).first()
        if db_resume:
            db_resume.contents = content
            db_resume.public = public
            db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def get_resumes(db: Session):
    db_resume_list = db.query(Resume).all()
    return [ResumeResponse(
        member_name=db.query(Member).filter_by(id=db_resume.member_id).first().nickname,
        content=db_resume.contents) for db_resume in db_resume_list]

def get_resume(id: int, db: Session):
    try:
        db_resume = db.query(Resume).filter_by(id = id).first()
        if db_resume is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
        resume_detail = ResumeDetailResponse(
            contents=db_resume.contents
        )
        return resume_detail
    except SQLAlchemyError as e:
        raise HTTPException(e)