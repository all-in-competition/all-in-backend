from pydantic import BaseModel, Field


#Title을 가지고 있는 스키마
class TaskBase(BaseModel):
  title: str | None = Field(default=None)


class TaskCreate(TaskBase):
  pass

class TaskCreateResponse(TaskCreate):
  id: int

  class Config:
    from_attributes = True

    
class Task(TaskBase):
  id: int
  done: bool = Field(False, description="완료 플래그")