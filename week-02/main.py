from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi import Response


app = FastAPI(
    title="Task API",
    description="A simple CRUD API to manage your to-do tasks",
    version="1.0"
)

tasks = [
    {"id": 1, "title": "This is task 1", "done": False},
    {"id": 2, "title": "This is task 2", "done": True},
    {"id": 3, "title": "This is task 3", "done": False}
]

# Pydantic model to parse and validate the request body
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/")
async def get_api_info():
    
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
async def health_check():

    return {"status": "ok"}



@app.get("/tasks", summary="Get tasks with filtering")              
async def get_tasks(done: Optional[bool] = None):  
    if done is None:            
        return tasks
    return [task for task in tasks if task["done"] == done]  

@app.get("/tasks/{task_id}", summary="Get a single task by ID")
async def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")





# Stage 3: Create a new task
@app.post("/tasks", status_code=201, summary="Create a new task")
async def create_task(task: TaskCreate):
    # 1. Validate: check for empty or whitespace-only string
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    # 2. Generate next ID: take the last item's id + 1, or start at 1 if list is empty
    next_id = tasks[-1]["id"] + 1 if tasks else 1

    # 3. Create the new task object
    new_task = {"id": next_id, "title": task.title, "done": False}

    # 4. Save and return the new task
    tasks.append(new_task)
    return new_task


@app.put("/tasks/{task_id}", summary="Update an existing task")
async def update_task(task_id: int, task: TaskUpdate):
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            if task.title is not None:
                t["title"] = task.title
            if task.done is not None:
                t["done"] = task.done
            return t 
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            del tasks[i]
            return Response(status_code=204)
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


