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
    return {"raw": raw}

