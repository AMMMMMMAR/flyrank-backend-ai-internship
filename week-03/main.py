import sqlite3
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

def row_to_dict(row):
    return {"id": row[0], "title": row[1], "done": bool(row[2])}

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

def init_db():
    # 1. Connect to the database (creates 'tasks.db' if it doesn't exist)
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    # 2. Create the tasks table if it doesn't already exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    # 3. Check if the table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    # 4. Insert 3 default tasks only if the table is empty
    if count == 0:
        example_tasks = [
            ("This is task 1", 0),
            ("This is task 2", 1),
            ("This is task 3", 0)
        ]
        # executemany binds each tuple in the list to the placeholders (?, ?)
        cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", example_tasks)
        
    # Commit the transaction to save changes to disk
    conn.commit()

    # 5. Clean up by closing the connection
    conn.close()


init_db()


@app.get("/tasks", summary="Get all tasks")              
async def get_tasks():  
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a list of dictionaries
    result = [row_to_dict(row) for row in rows]  # in get_tasks
    return result   
                   




@app.get("/tasks/{task_id}", summary="Get a single task by ID")
async def get_task(task_id: int):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return row_to_dict(row) 
    else:
        raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks", status_code=201, summary="Create a new task")
async def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, 0))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    
    return {"id": task_id, "title": task.title, "done": False}


@app.put("/tasks/{task_id}", summary="Update a task by ID")
async def update_task(task_id: int, task: TaskUpdate):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    
    # 1. Check task exists first
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 2. Update only provided fields
    new_title = task.title if task.title is not None else existing[1]
    new_done = task.done if task.done is not None else bool(existing[2])
    
    # 3. Run the update
    cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", 
                   (new_title, new_done, task_id))
    conn.commit()
    conn.close()
    
    return {"id": task_id, "title": new_title, "done": new_done}

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task by ID")
async def delete_task(task_id: int):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    deleted_rows = cursor.rowcount
    conn.close()

    if deleted_rows == 0:                    # ← check BEFORE return
        raise HTTPException(status_code=404, detail="Task not found")
    
    return Response(status_code=204)         # ← return AFTER check