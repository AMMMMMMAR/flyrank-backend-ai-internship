from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
import repository

app = FastAPI(
    title="Task API",
    description="CRUD API backed by PostgreSQL running in Docker",
    version="1.0"
)


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/tasks", summary="Get all tasks")
async def get_tasks():
    return repository.get_all_tasks()


@app.get("/tasks/{task_id}", summary="Get a single task by ID")
async def get_task(task_id: int):
    task = repository.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks", status_code=201, summary="Create a new task")
async def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    return repository.create_task(task.title)


@app.put("/tasks/{task_id}", summary="Update a task by ID")
async def update_task(task_id: int, task: TaskUpdate):
    if task.title is not None and not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    updated = repository.update_task(task_id, task.title, task.done)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task by ID")
async def delete_task(task_id: int):
    deleted = repository.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=204)