from pydantic import BaseModel, Field
from api.models.model import Tag

class ResumeUpdate(BaseModel):
  contents : str
  public : bool = False

class ResumeCreate(BaseModel):
  member_id : int
  contents : str
  public : bool

class ResumeResponse(BaseModel):
  member_name : str
  contents : str
  #tag :

class ResumeDitailResponse(BaseModel):
  member_name: str
  contents: str
  #tag :
