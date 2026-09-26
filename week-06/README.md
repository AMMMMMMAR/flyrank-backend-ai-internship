# Week 06 — Put an LLM Behind Your API

A FastAPI endpoint that normalizes messy job titles into canonical titles
using an LLM. One title in, one clean validated JSON out.

## What it does

`POST /normalize` takes a messy job title like "Sr. SWE II" or "Full Stack JS Dev"
and returns a canonical title from a fixed list, a confidence score, and a reason.
The model's output is validated against a Pydantic schema before anything is returned.

## Job Card

**Input:** `{ "title": "string, 1-500 characters" }`

**Output:**
```json
{
  "canonical_title": "Senior Software Engineer",
  "confidence": 0.97,
  "reason": "Sr. Software Engineer is a common abbreviation for Senior Software Engineer."
}
```

**Allowed canonical titles:** Software Engineer, Senior Software Engineer,
Frontend Developer, Backend Developer, Full Stack Developer, Data Scientist,
Data Engineer, Product Manager, DevOps Engineer, QA Engineer, Other

**It must never:** invent a title outside the list, return free text, add extra fields

**When unsure:** return "Other" with confidence below 0.5

## How to run

```bash
cd week-06
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file (see `.env.example`):
```
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=your_key_here
LLM_MODEL=openrouter/auto
LLM_STUB=0
LLM_ENABLED=true
```

```bash
uvicorn src.main:app --reload
```

## Test it

Valid request:
```bash
curl -X POST http://localhost:8000/normalize \
  -H "Content-Type: application/json" \
  -d '{"title": "Sr. Software Engineer"}'
```

Expected response:
```json
{
  "canonical_title": "Senior Software Engineer",
  "confidence": 0.97,
  "reason": "Sr. Software Engineer is a common abbreviation for Senior Software Engineer."
}
```

Missing field (returns 400):
```bash
curl -X POST http://localhost:8000/normalize \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Provider and model

- **Provider:** OpenRouter
- **Model:** openrouter/auto
- **Three env vars to swap provider:** `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`

Changing those three values is the only difference between a model running
locally and one running in a datacentre. Never hardcode a provider.

## Eval results

- **Score:** 7/8 (88%)
- **Date:** 2026-09-24
- **Prompt version:** normalize-v1
- **Failed case:** "ML Engineer" → got "Other", expected "Data Scientist"
  This is a legitimate ambiguity — ML Engineers overlap with both
  Software Engineers and Data Scientists.

## Cost log (one call)

```json
{"prompt_version": "normalize-v1", "model": "openrouter/auto", "input_tokens": 493, "output_tokens": 79, "duration_ms": 3289.25, "repaired": false}
```

At 10,000 requests/day:
- Input: 493 × 10,000 = 4.93M tokens
- Output: 79 × 10,000 = 0.79M tokens
- Estimated cost varies by model — check openrouter.ai/models for pricing

## Kill switch

Set `LLM_ENABLED=false` in `.env` to disable the model entirely.
The endpoint returns 503 immediately with zero model calls.

## Stub mode

Set `LLM_STUB=1` to return a hardcoded valid response without calling the model.
Use this during development to avoid spending quota.

## What I'd fix with another day

Add "Machine Learning Engineer" as a canonical title — the current list
doesn't distinguish ML Engineers from Data Scientists, causing the one
failed eval case.

## Reliability

- 30 second timeout on every model call
- Retries on timeout, 429, 5xx — never on 400, 401, 403
- One repair attempt if model output fails schema validation
- Failed repairs go to `logs/quarantine.jsonl`
- Cost logged to `logs/cost.jsonl` per call