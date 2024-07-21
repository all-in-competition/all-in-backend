from fastapi import HTTPException
from sqlalchemy.orm import Session, InstrumentedAttribute
from sqlalchemy import and_, BIGINT
import api.models.model as member_model
from api.schemas import login as login_schema
from api.schemas import member as member_schema
from aiohttp import ClientSession
from starlette import status


def create_member(db: Session, user_info: dict) -> member_schema.MemberCreate:
    new_member = member_model.Member(
        provider_id=user_info['id'],
        provider_type="kakao",
        nickname=user_info.get('properties').get('nickname'),
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return member_schema.MemberCreate(
        id = new_member.id,
        provider_id = new_member.provider_id,
        provider_type = new_member.provider_type,
        nickname = new_member.nickname,
        status = new_member.status
    )


def find_member(db: Session, user_info):
    db_member = db.query(member_model.Member).filter_by(provider_type = "kakao", provider_id = user_info['id']).first()
    if db_member:
         return member_schema.MemberCreate(
             id = db_member.id,
             provider_id = db_member.provider_id,
             provider_type = db_member.provider_type,
             nickname = db_member.nickname,
             status = db_member.status
         )
    else:
        return None

def find_member_name(db: Session, uid: int):
    db_member = db.query(member_model.Member).filter_by(id = uid).first()
    if db_member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Member not found')
    return db_member.nickname

async def get_kakao_user_info(token):
    user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {token}"}

    async with ClientSession() as client:
        async with client.get(user_info_url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Failed to fetch user info from Kakao")
            user_info = await response.json()
            print(user_info)
            return user_info