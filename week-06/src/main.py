from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.schema import NormalizeOutput, CanonicalTitle
import os
from openai import OpenAI




load_dotenv()

LLM_STUB = os.getenv("LLM_STUB", "0") == "1"
LLM_ENABLED = os.getenv("LLM_ENABLED", "true").lower() == "true"

app = FastAPI(
    title="Normalize API",
    description="Normalizes messy job titles into canonical titles using an LLM",
    version="1.0"
)

class NormalizeInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)

def load_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "normalize-v1.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

client = OpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
    timeout=30.0
)

import json
from pydantic import ValidationError

def parse_and_validate(raw: str):
    try:
        # strip code fences if model added them
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

        
@app.post("/normalize")
async def normalize_title(body: NormalizeInput):
    if LLM_STUB:
        return NormalizeOutput(
            canonical_title=CanonicalTitle.SOFTWARE_ENGINEER,
            confidence=0.9,
            reason="Stubbed response for testing"
        )

    if not LLM_ENABLED:
        raise HTTPException(status_code=503, detail="LLM is currently disabled")

    # Load prompt
    system_prompt = load_prompt()

    # Call model
    response = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": body.title}
        ],
        temperature=0.1
    )

    raw = response.choices[0].message.content

    # 1. Parse and validate
    result = parse_and_validate(raw)
    if result:
        return result

    # 2. Repair once
    print(f"First attempt failed, trying repair...")
    repair_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": body.title},
        {"role": "assistant", "content": raw},
        {"role": "user", "content": f"Your previous answer was rejected. Return only corrected JSON matching the schema. Error: invalid or missing fields."}
    ]
    repair_response = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        messages=repair_messages,
        temperature=0.1
    )
    raw2 = repair_response.choices[0].message.content
    result = parse_and_validate(raw2)
    if result:
        return result

    # 3. Quarantine and give up
    quarantine(body.title, raw, "failed after repair")
    raise HTTPException(status_code=422, detail="Model output could not be validated after repair")

