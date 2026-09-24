from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.schema import NormalizeOutput, CanonicalTitle
import sys
import os




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

@app.post("/normalize")
async def normalize_title(body: NormalizeInput):
    # Input validation handled by Pydantic automatically

    # Stub mode — no model call
    if LLM_STUB:
        return NormalizeOutput(
            canonical_title=CanonicalTitle.SOFTWARE_ENGINEER,
            confidence=0.9,
            reason="Stubbed response for testing"
        )

    # Kill switch
    if not LLM_ENABLED:
        raise HTTPException(status_code=503, detail="LLM is currently disabled")

    # Real LLM call comes in Stage 2
    return {"message": "LLM not connected yet"}