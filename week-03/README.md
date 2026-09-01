# Week 03 — Connecting CRUD to a Database

The same CRUD API from Week 2, now backed by a real SQLite database. 
Data survives server restarts.

## Why SQLite?

SQLite was chosen because:
- No separate database server required
- Stored in a single file (tasks.db) on disk
- Built into Python — no extra installation needed
- Perfect for learning SQL fundamentals before moving to larger databases

## Where is the database file?

The database is stored in `week-03/tasks.db`. 
This file is excluded from Git (see .gitignore) because it is auto-generated.

## How to run

```bash
cd week-03
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

The database and table are created automatically on first run.
The 3 example tasks are inserted only once.

## API Endpoints

| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| GET | /tasks | List all tasks | 200 |
| GET | /tasks/{id} | Get one task | 200 / 404 |
| POST | /tasks | Create a task | 201 / 400 |
| PUT | /tasks/{id} | Update a task | 200 / 400 / 404 |
| DELETE | /tasks/{id} | Delete a task | 204 / 404 |

## Example SQL queries

```sql
-- List every task
SELECT * FROM tasks;

-- Show only completed tasks
SELECT * FROM tasks WHERE done = 1;

-- Count all tasks
SELECT COUNT(*) FROM tasks;

-- Mark every task as completed
UPDATE tasks SET done = 1;

-- Delete all completed tasks
DELETE FROM tasks WHERE done = 1;
```

## Database screenshot

![DB Browser](db_browser.png)

## Interactive Docs
Visit `http://localhost:8000/docs` after running the server.