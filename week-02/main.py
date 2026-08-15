from fastapi import FastAPI, HTTPException

app = FastAPI()

tasks = [
    {"id": 1, "title": "This is task 1", "done": False},
    {"id": 2, "title": "This is task 2", "done": True},
    {"id": 3, "title": "This is task 3", "done": False}
]

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



@app.get("/tasks")
async def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")





