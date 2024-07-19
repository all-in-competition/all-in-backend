from pydantic import BaseModel, Field


class ResumeUpdate(BaseModel):
  id : int
  contents : str
  public : bool

class ResumeCreate(BaseModel):
  member_id : int
  contents : str
  public : bool

class ResumeResponse(BaseModel):
  member_name : str
  contents : str
