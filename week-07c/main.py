import datetime
import uuid

import inngest
import inngest.fast_api
from fastapi import FastAPI, HTTPException

inngest_client = inngest.Inngest(
    app_id="report-api",
    is_production=False,
    event_api_base_url="http://127.0.0.1:8288",
)

# In-memory "database": report id -> report dict.
reports: dict[str, dict] = {}


# ---------- Stage 1 function ----------
@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context) -> str:
    await ctx.step.sleep("wait-a-moment", datetime.timedelta(seconds=5))
    return "Hello from the background!"


# ---------- Stage 4: runs once after the LAST attempt fails ----------
async def mark_failed(ctx: inngest.Context) -> None:
    report_id = ctx.event.data["event"]["data"]["id"]
    if report_id in reports:
        reports[report_id]["status"] = "failed"


# ---------- Stage 2 + 3 + 4 function ----------
@inngest_client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,
    on_failure=mark_failed,
)
async def make_report(ctx: inngest.Context) -> str:
    report_id = ctx.event.data["id"]
    topic = ctx.event.data["topic"]

    await ctx.step.sleep("do-the-slow-work", datetime.timedelta(seconds=8))

    async def build_report() -> str:
        if topic == "fail":
            raise Exception("The report oven is broken!")

        result = f"Report about {topic}: cats sleep 13-16 hours a day."
        reports[report_id]["status"] = "done"
        reports[report_id]["result"] = result
        return result

    return await ctx.step.run("build-report", build_report)


# ---------- Stage 4: cron heartbeat ----------
@inngest_client.create_function(
    fn_id="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),  # every minute (testing only)
)
async def heartbeat(ctx: inngest.Context) -> str:
    pending = sum(1 for r in reports.values() if r["status"] == "pending")
    done = sum(1 for r in reports.values() if r["status"] == "done")
    failed = sum(1 for r in reports.values() if r["status"] == "failed")
    summary = f"Heartbeat: {pending} pending, {done} done, {failed} failed"
    print(summary)
    return summary


app = FastAPI()

inngest.fast_api.serve(app, inngest_client, [say_hello, make_report, heartbeat])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reports", status_code=202)
async def create_report(body: dict):
    topic = body.get("topic")
    if not topic or not isinstance(topic, str):
        raise HTTPException(status_code=400, detail="topic is required")

    report_id = str(uuid.uuid4())
    reports[report_id] = {
        "id": report_id,
        "topic": topic,
        "status": "pending",
    }

    await inngest_client.send(
        inngest.Event(
            name="report/requested",
            data={"id": report_id, "topic": topic},
        )
    )

    return {"id": report_id, "status": "pending"}


@app.get("/reports/{report_id}")
def get_report(report_id: str):
    report = reports.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report