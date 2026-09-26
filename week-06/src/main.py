from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
from src.schema import NormalizeOutput, CanonicalTitle
import os
import json
import time
from openai import OpenAI

load_dotenv()

LLM_STUB = os.getenv("LLM_STUB", "0") == "1"
LLM_ENABLED = os.getenv("LLM_ENABLED", "true").lower() == "true"

# --- Client ---
client = OpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
    timeout=30.0
)

# --- App ---
app = FastAPI(
    title="Normalize API",
    description="Normalizes messy job titles into canonical titles using an LLM",
    version="1.0"
)

# --- Input ---
class NormalizeInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)


# --- Helpers ---
def load_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "normalize-v1.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def parse_and_validate(raw: str):
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        data = json.loads(cleaned)
        return NormalizeOutput(**data)
    except (json.JSONDecodeError, ValidationError, Exception):
        return None


def quarantine(input_title: str, raw_output: str, reason: str):
    os.makedirs("logs", exist_ok=True)
    entry = {
        "input": input_title,
        "raw_output": raw_output,
        "reason": reason,
        "prompt_version": "normalize-v1"
    }
    with open("logs/quarantine.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def log_cost(input_tokens: int, output_tokens: int, duration_ms: float, repaired: bool):
    os.makedirs("logs", exist_ok=True)
    entry = {
        "prompt_version": "normalize-v1",
        "model": os.environ["LLM_MODEL"],
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "duration_ms": round(duration_ms, 2),
        "repaired": repaired
    }
    with open("logs/cost.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def call_model_with_retry(messages: list, max_retries: int = 2):
    delays = [1, 2, 4]
    for attempt in range(max_retries + 1):
        try:
            return client.chat.completions.create(
                model=os.environ["LLM_MODEL"],
                messages=messages,
                temperature=0.1
            )
        except Exception as e:
            error_str = str(e)
            # never retry on auth or bad request errors
            if "401" in error_str or "403" in error_str or "400" in error_str:
                raise
            # retry on timeout, 429, 5xx
            if attempt < max_retries:
                wait = delays[attempt] + (0.1 * attempt)
                print(f"Retry {attempt + 1} after {wait}s — {error_str}")
                time.sleep(wait)
            else:
                raise


# --- Endpoint ---
@app.post("/normalize")
async def normalize_title(body: NormalizeInput):
    # Stub mode
    if LLM_STUB:
        return NormalizeOutput(
            canonical_title=CanonicalTitle.SOFTWARE_ENGINEER,
            confidence=0.9,
            reason="Stubbed response for testing"
        )

    # Kill switch
    if not LLM_ENABLED:
        raise HTTPException(status_code=503, detail="LLM is currently disabled")

    system_prompt = load_prompt()

    # First attempt
    start = time.time()
    try:
        response = call_model_with_retry([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": body.title}
        ])
    except Exception as e:
        if "timed out" in str(e).lower():
            raise HTTPException(status_code=504, detail="LLM request timed out")
        raise HTTPException(status_code=502, detail=f"LLM error: {str(e)}")

    duration_ms = (time.time() - start) * 1000
    raw = response.choices[0].message.content
    result = parse_and_validate(raw)

    if result:
        log_cost(
            response.usage.prompt_tokens,
            response.usage.completion_tokens,
            duration_ms,
            repaired=False
        )
        return result

    # Repair once
    print(f"First attempt failed, trying repair...")
    try:
        repair_response = call_model_with_retry([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": body.title},
            {"role": "assistant", "content": raw},
            {"role": "user", "content": "Your previous answer was rejected. Return only corrected JSON matching the schema. Error: invalid or missing fields."}
        ])
    except Exception as e:
        quarantine(body.title, raw, f"repair call failed: {str(e)}")
        raise HTTPException(status_code=422, detail="Model output could not be validated and repair failed")

    raw2 = repair_response.choices[0].message.content
    result = parse_and_validate(raw2)

    if result:
        log_cost(
            repair_response.usage.prompt_tokens,
            repair_response.usage.completion_tokens,
            duration_ms,
            repaired=True
        )
        return result

    # Give up
    quarantine(body.title, raw, "failed after repair")
    raise HTTPException(status_code=422, detail="Model output could not be validated after repair")