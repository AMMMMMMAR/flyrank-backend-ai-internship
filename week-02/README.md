# Week 02 — Build your first CRUD API

A to-do list REST API built with FastAPI. Supports full CRUD operations with in-memory storage.

## How to run
```bash
cd week-02
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

## API Endpoints

| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| GET | / | API info | 200 |
| GET | /health | Health check | 200 |
| GET | /tasks | List all tasks | 200 |
| GET | /tasks/{id} | Get one task | 200 / 404 |
| POST | /tasks | Create a task | 201 / 400 |
| PUT | /tasks/{id} | Update a task | 200 / 400 / 404 |
| DELETE | /tasks/{id} | Delete a task | 204 / 404 |

## Interactive Docs
Visit `http://localhost:8000/docs` after running the server.

## Sample curl output
curl -i http://localhost:8000/tasks

HTTP/1.1 200 OK
date: Mon, 17 Aug 2026 21:16:45 GMT
server: uvicorn
content-length: 141
content-type: application/json

[{"id":1,"title":"This is task 1","done":false},{"id":2,"title":"This is task 2","done":true},{"id":3,"title":"This is task 3","done":false}]

## Swagger UI Screenshot
![Alt Text](/swagger.png)
