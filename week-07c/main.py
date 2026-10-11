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


# ---------- Stage 2 + 3 function ----------
@inngest_client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,  # Stage 3: 1 first try + 2 retries = 3 attempts
)
async def make_report(ctx: inngest.Context) -> str:
    report_id = ctx.event.data["id"]
    topic = ctx.event.data["topic"]

    await ctx.step.sleep("do-the-slow-work", datetime.timedelta(seconds=8))

    async def build_report() -> str:
        # Stage 3: test switch to watch retries happen
        if topic == "fail":
            raise Exception("The report oven is broken!")

        result = f"Report about {topic}: cats sleep 13-16 hours a day."
        reports[report_id]["status"] = "done"
        reports[report_id]["result"] = result
        return result

    return await ctx.step.run("build-report", build_report)


app = FastAPI()

inngest.fast_api.serve(app, inngest_client, [say_hello, make_report])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reports", status_code=202)
async def create_report(body: dict):
    # Stage 3: reject bad input at the door (no report, no event)
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