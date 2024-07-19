from api.models.model import Resume, Tag
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

def update_resume(db: Session, new: ResumeUpdate):
    db.execute(
    update(Resume).
    where(new.id == Resume.id).
    values(content=new.contents, public=new.public)
    )
def get_resumes(db: Session):
    db_resume_list = db.query(Resume).all()

    return [ResumeResponse(member_name=db_resume.member,
                         content=db_resume.contents) for db_resume in db_resume_list]

def get_resume(db: Session, id: int):
    return db.query(Resume).filter(id == Resume.id)
