# Week 7c: Your first background job (FastAPI + Inngest)

A small API where the slow work (an 8-second report) runs in a background job.
The API answers instantly with 202, a status endpoint reports progress,
and one cron job runs on the clock alone.

## How to run

Terminal 1 (API):
```powershell
pip install -r requirements.txt
uvicorn main:app --reload
```

Terminal 2 (Inngest Dev Server):
```powershell
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest
```

Dashboard: http://127.0.0.1:8288

## Endpoints and functions

| Name | Type | What it does |
|------|------|--------------|
| GET /health | endpoint | returns {"status":"ok"} |
| POST /reports | endpoint | validates topic (400 if missing), saves pending report, sends event, returns 202 |
| GET /reports/{id} | endpoint | returns the report (pending, done or failed); unknown id gives 404 |
| say-hello | function (event test/hello) | sleeps 5s, returns a greeting |
| make-report | function (event report/requested) | sleeps 8s, then builds the report; retries=2 |
| heartbeat | function (cron * * * * *) | logs how many reports are pending, done and failed |

## Proof: 202 then the polls

The POST answered with 202 in about a fifth of a second:

```
HTTP/1.1 202 Accepted
date: Sun, 11 Oct 2026 19:59:53 GMT
server: uvicorn
content-length: 64
content-type: application/json

{"id":"f4208e88-147a-4d76-9b6f-52e6f24a31c0","status":"pending"}
Time: 0.219725s
```

A poll right after a second POST shows pending:

```
{"id":"6097a547-5722-46c2-8d2d-62e401550f0f","topic":"cats","status":"pending"}
```

The same id about 10 seconds later shows done:

```
{"id":"6097a547-5722-46c2-8d2d-62e401550f0f","topic":"cats","status":"done","result":"Report about cats: cats sleep 13-16 hours a day."}
```

## Stage 3: retries vs bad input

A retry fixes a wrong moment (a network drop), but bad input like a missing topic will fail every time, so it is rejected at the door with a 400 and no job is created.

## Stage 4: cron

- Every day at 08:00: `0 8 * * *`
- Every Sunday at 22:00: `0 22 * * 0`

## Dashboard screenshot

![dashboard](dashboard.png)