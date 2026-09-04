# Week 3b — Study Notes
## Docker + PostgreSQL + Repository Pattern

---

## The Big Picture

Week 2: Client → FastAPI → List in RAM (dies on restart)
Week 3: Client → FastAPI → SQLite file (survives restart)
Week 3b: Client → FastAPI (container) → PostgreSQL (container)
↓
Docker Volume
(data on disk forever)


---

## Key Concepts

### Docker
A tool that runs applications in isolated boxes called **containers**.
No more "it works on my machine" problems — the container has everything it needs.

### Container
A lightweight isolated environment. Like a mini computer inside your computer.
Your FastAPI app runs in one container, PostgreSQL runs in another.

### Docker Volume
A folder that lives **outside** the container on your real machine.
Even if you delete the container, the data in the volume stays safe.
This is how PostgreSQL data survives restarts.

### docker-compose
A tool that starts **multiple containers together** with one command:
```bash
docker compose up --build
```

### `.env` file
Stores secrets like database passwords.
**Never committed to Git.**
You commit `.env.example` instead — a safe template with no real values.

### Repository Pattern
A code pattern that separates "how you store data" from "what your API does."
All SQL lives in `repository.py`.
Your endpoints just call functions — they never touch SQL directly.

---

## Project Structure

week-03b/
├── main.py ← FastAPI endpoints (no SQL here)
├── repository.py ← All database operations (SQL lives here)
├── database.py ← Database connection
├── docker-compose.yml ← Starts app + database together
├── Dockerfile ← Tells Docker how to build your app
├── init.sql ← Creates table + seeds data on first run
├── .env ← Secrets (gitignored)
├── .env.example ← Template (committed to Git)
├── requirements.txt ← Python packages
├── NOTES.md ← This file
└── .gitignore ← venv/, .env, pycache/


---

## File by File

### `.env`

DATABASE_URL=postgresql://taskuser:taskpass@db:5432/taskdb


Connection string format:

postgresql://USERNAME:PASSWORD@HOSTNAME:PORT/DATABASE_NAME

- `db` = the Docker service name (not localhost!)
- `5432` = PostgreSQL default port

### `.env.example`

DATABASE_URL=postgresql://user:password@db:5432/dbname

Safe to commit — no real secrets, just a template.

---

### `init.sql`
Runs automatically when PostgreSQL container starts for the first time.

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);
```

#### SQLite vs PostgreSQL differences

| SQLite | PostgreSQL |
|--------|-----------|
| `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` |
| `DEFAULT 0` for boolean | `DEFAULT FALSE` |
| `?` placeholder | `%s` placeholder |
| `cursor.lastrowid` | `RETURNING id` in query |

---

### `database.py`
```python
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env file into environment

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))
```

---

### `repository.py`
All SQL lives here. Endpoints never touch SQL directly.

```python
from database import get_connection

def get_all_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "done": r[2]} for r in rows]

def create_task(title: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id",
        (title, False)
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return {"id": new_id, "title": title, "done": False}

def update_task(task_id: int, title: str = None, done: bool = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        return None
    new_title = title if title is not None else existing[1]
    new_done = done if done is not None else existing[2]
    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
        (new_title, new_done, task_id)
    )
    conn.commit()
    conn.close()
    return {"id": task_id, "title": new_title, "done": new_done}

def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0
```

Key points:
- `RETURNING id` → PostgreSQL returns the new row's id directly from INSERT
- `cursor.rowcount` → how many rows were affected by DELETE or UPDATE
- `conn.commit()` → always commit after INSERT, UPDATE, DELETE
- `conn.close()` → always close the connection when done

---

### `main.py`
Clean endpoints — no SQL, just repository calls:

```python
import repository

@app.get("/tasks")
async def get_tasks():
    return repository.get_all_tasks()

@app.post("/tasks", status_code=201)
async def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    return repository.create_task(task.title)

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate):
    updated = repository.update_task(task_id, task.title, task.done)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    deleted = repository.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=204)
```

---

### `Dockerfile`
Tells Docker how to build your app image:

```dockerfile
FROM python:3.12-slim       # start from official Python image
WORKDIR /app                # all commands run inside /app
COPY requirements.txt .     # copy requirements first (Docker caches this layer)
RUN pip install --no-cache-dir -r requirements.txt
COPY . .                    # copy all your code
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`--host 0.0.0.0` → accept connections from outside the container.
Requirements are copied before code so Docker only reinstalls packages when `requirements.txt` changes — not every time you change your code.

---

### `docker-compose.yml`

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: taskpass
      POSTGRES_DB: taskdb
    volumes:
      - postgres_data:/var/lib/postgresql/data  # persist data on disk
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql  # run on first start
    ports:
      - "5432:5432"

  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db  # app starts only after database is ready

volumes:
  postgres_data:  # named volume — survives container deletion
```

---

## Commands to Remember

```bash
# Start everything (first time — builds the image)
docker compose up --build

# Start everything (after first time)
docker compose up

# Stop everything
Ctrl+C

# Stop and remove containers
docker compose down

# Stop, remove containers AND delete volume (full reset)
docker compose down -v
```

---

## The Repository Pattern — Why It Matters

### Before (SQL directly in endpoints)
```python
@app.get("/tasks")
async def get_tasks():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return rows
```

### After (Repository pattern)
```python
@app.get("/tasks")
async def get_tasks():
    return repository.get_all_tasks()
```

### The benefit
If you switch from PostgreSQL to MySQL or MongoDB — you only change `repository.py`.
Your endpoints (`main.py`) never change.
That's the architecture proving itself.

---

## Persistence Proof
docker compose up --build ← start everything
POST /tasks → "Buy milk" ← create a task
Ctrl+C ← stop everything
docker compose up ← restart
GET /tasks → "Buy milk" ✅ ← data still there!

Data survives because it lives in a Docker volume, not inside the container.

---

## Storage Comparison

| | In-Memory (W2) | SQLite (W3) | PostgreSQL (W3b) |
|--|:-:|:-:|:-:|
| Survives restart | ❌ | ✅ | ✅ |
| Needs Docker | ❌ | ❌ | ✅ |
| Production ready | ❌ | ⚠️ | ✅ |
| Setup complexity | Easy | Easy | Medium |

---

## New Libraries

| Library | What it does |
|---------|-------------|
| `psycopg2-binary` | Connects Python to PostgreSQL |
| `python-dotenv` | Reads `.env` file into environment variables |

---

## Rules to Never Forget

1. Never commit `.env` to Git — secrets stay local
2. Always `conn.commit()` after INSERT, UPDATE, DELETE
3. Always `conn.close()` when done with a connection
4. SQL goes in `repository.py` — never in `main.py`
5. `db` in the connection string = Docker service name, not `localhost`
6. `docker compose down -v` deletes your data — use with caution