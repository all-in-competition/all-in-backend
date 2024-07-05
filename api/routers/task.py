from fastapi import APIRouter

import api.schemas.task as task_schema


router = APIRouter()

@router.get("/tasks",response_model=list[task_schema.Task]) #응답 모델의 스키마
async def list_task():
  return [task_schema.Task(id = 1, title="첫 번째 ToDo 작업")]

@router.post("/tasks", response_model=task_schema.TaskCreateResponse) #TaskCreateResponse 유형으로 응답
async def create_task(task_body: task_schema.TaskCreate): #TaskCreate 유형으로 받고
  return task_schema.TaskCreateResponse(id=1, title=task_body.title) #요청 Body의 title을 응답에 사용
  

@router.put("/tasks/{task_id}", response_model=task_schema.TaskCreateResponse)
async def update_task(task_id: int, task_body:task_schema.TaskCreate):
  return task_schema.TaskCreateResponse(id=task_id, **task_body.dict())
  

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
  return