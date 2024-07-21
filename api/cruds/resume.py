from typing import Sequence, Union, List

from api.cruds.member import find_member_name
from api.cruds.tag import get_tag
from api.models.model import Resume, Member, Tag, resume_tag
from fastapi import HTTPException
from fastapi_pagination.cursor import CursorParams
from requests import session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from api.schemas import member as member_schema
from api.schemas.resume import ResumeCreate, ResumeUpdate, ResumeResponse, ResumeDetailResponse, ResumeSummaryResponse
from sqlalchemy import update
from starlette import status
from fastapi_pagination.ext.sqlalchemy import paginate



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

def update_resume(new: ResumeUpdate, db: Session, user_info: member_schema.MemberCreate):
    try:
        db_resume = db.query(Resume).filter_by(member_id=user_info["id"]).first()
        if db_resume:
            db_resume.contents = new.contents
            db_resume.public = new.public

        db.query(resume_tag).filter_by(resume_id=db_resume.id).delete()

        tags = []
        for tag_name in new.tag_name:
            tag_name = tag_name.lower()
            if tag_name not in tags:
                tags.append(tag_name)

        for tag_name in tags:
            db_tag = db.query(Tag).filter(tag_name == Tag.name, new.category_id == Tag.category_id).first()
            if db_tag is None:
                db_tag = Tag(name=tag_name, category_id=new.category_id)
                db.add(db_tag)

            db_resume.tag.append(db_tag)

        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        raise e



def get_resumes(db: Session, params: CursorParams):
    db_resume_list = db.query(Resume).all()

    resume_to_summary_response = [ResumeSummaryResponse(
        member_name=find_member_name(resume.member_id),
        tag_id=resume.tag.id,
        contents=resume.contents
        ) for resume in db_resume_list]
    return paginate(db_resume_list, params, transformer=resume_to_summary_response)


def get_resume(id: int, db: Session):
    try:
        db_resume = db.query(Resume).filter(id == Resume.id).first()
        if db_resume is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resume not found')

        tags = []
        tag_id = db.query(resume_tag).filter_by(resume_id=db_resume.id).all()
        for id in tag_id:
            tags.append(get_tag(id[0], db).name)

        resume_detail = ResumeDetailResponse(
            member_name=find_member_name(db=db, uid=db_resume.member_id),
            contents=db_resume.contents,
            tags=tags
        )
        return resume_detail
    except SQLAlchemyError as e:
        raise HTTPException(e)