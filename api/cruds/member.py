from sqlalchemy.orm import Session
from sqlalchemy import and_
import api.models.model as member_model
from api.schemas import login as login_schema
from aiohttp import ClientSession

def create_member(db: Session, member_create: login_schema.SessionData):
    new_member = member_model.Member(**member_create.model_dump())
    db.add(new_member)
    db.commit()


def find_member(db: Session, user_info: login_schema.SessionData):
    return db.query(member_model.Member).filter(and_(member_model.Member.provider_type == user_info.provider_type,
                                                     member_model.Member.provider_id == user_info.provider_id))


def is_first_login(db: Session, session_data: login_schema.SessionData) -> bool:
    find_user = find_member(db=db, user_info=session_data)
    if find_user:
        return True
    else:
        return False


async def get_kakao_user_info(token):
    user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {token}"}

    async with ClientSession() as client:
        async with client.get(user_info_url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Failed to fetch user info from Kakao")
            return await response.json()