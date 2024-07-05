from pydantic import BaseModel, Field


class ResuemUpdate(BaseModel):
  member_id : int
  contents : str
  public : bool
