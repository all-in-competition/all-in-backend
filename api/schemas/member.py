from pydantic import BaseModel, Field


class MemberCreate(BaseModel):
  id : int
  provider_id : str
  provider_type: str
  nickname: str
  status: str
