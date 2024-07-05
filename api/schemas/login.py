from typing import Dict

from pydantic import BaseModel, Field


class SessionData(BaseModel):
    provider_type: str
    provider_id: str
    nickname: str


def to_session_data(kakao_user_info: Dict) -> SessionData:
    try:
        return SessionData(
            provider_type="kakao",
            provider_id=str(kakao_user_info['id']),
            nickname=kakao_user_info['properties']['nickname']
        )
    except KeyError as e:
        raise ValueError(f"Missing required field in kakao_user_info: {e}")
