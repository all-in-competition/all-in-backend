from datetime import datetime
from typing import List

from pydantic import BaseModel, Field
from api.models.model import Tag

class ResumeUpdate(BaseModel):
  contents : str
  public : bool = False
  category_id : int
  tag_name : List[str]
  update_at: datetime

class ResumeCreate(BaseModel):
  member_id : int
  contents : str
  public : bool

class ResumeSummaryResponse(BaseModel):
  member_name : str
  tag_name: List[str]

class ResumeResponse(BaseModel):
  member_name : str
  contents : str
  #tag :

class ResumeDetailResponse(BaseModel):
  member_name: str
  contents: str
  tags: List[str]
