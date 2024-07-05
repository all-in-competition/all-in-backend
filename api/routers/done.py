from fastapi import APIRouter

router = APIRouter()


@router.put("/task/{task_id}/done")
async def mark_task_as_done(task_id: int):
  return

@router.delete("/tasks/{task_id}/done")
async def unmark_task_as_done(task_id: int):
  return