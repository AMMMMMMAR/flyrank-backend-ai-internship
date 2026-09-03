# Week 03b — Containerize your stack

Same CRUD API from Week 3, now backed by PostgreSQL running in Docker.

## How to run

```bash
docker compose up --build
```

That's it. One command starts everything.

## What changed from Week 3

- SQLite → PostgreSQL (production-grade database)
- In-memory/file storage → Docker volume (survives restarts)
- Direct SQL in endpoints → Repository pattern (all SQL in repository.py)
- Manual startup → docker compose (one command runs everything)

## Service and routes unchanged

The API endpoints (`main.py`) did not change at all.
Only `repository.py` changed — proving the architecture works.

## Persistence proof

1. `docker compose up --build`
2. POST /tasks → create a task
3. `Ctrl+C` to stop
4. `docker compose up` to restart
5. GET /tasks → task still there ✅

## Architecture

Client → FastAPI (app container) → PostgreSQL (db container)
↓
Docker Volume
(data on disk)


## Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI endpoints |
| `repository.py` | All SQL operations |
| `database.py` | Database connection |
| `docker-compose.yml` | Starts app + database |
| `Dockerfile` | Builds the app image |
| `init.sql` | Creates table + seeds data |
| `.env` | Database credentials (gitignored) |
| `.env.example` | Template for credentials |