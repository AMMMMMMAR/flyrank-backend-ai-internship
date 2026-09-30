# Week 07a — Visual AI Workflow System

A visual AI workflow editor where each node represents a YES/NO decision 
powered by an LLM. Draw your workflow, run it, and watch the AI traverse 
the graph in real time.

## What it does

- Draw decision nodes on a canvas
- Connect them with YES or NO edges
- Click ▶ Run Workflow — the AI answers each node's question
- Watch nodes light up yellow (thinking) → green (YES) / red (NO)
- Workflow auto-saves to localStorage

## Tech Stack

- React + Vite
- React Flow — visual canvas
- OpenRouter — LLM provider
- Tailwind CSS + Shadcn — styling

## How to run

```bash
cd week-07a
npm install
```

Create a `.env` file:
```
VITE_OPENROUTER_API_KEY=your_key_here
VITE_OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
VITE_OPENROUTER_MODEL=openrouter/auto
```

```bash
npm run dev
```

Visit `http://localhost:5173`

## Features

- ✅ Add nodes with custom prompts
- ✅ Connect nodes with YES/NO edges
- ✅ Edit node prompts by clicking
- ✅ AI-powered YES/NO branching
- ✅ Visual execution state (yellow/green/red)
- ✅ Execution log panel
- ✅ Auto-save to localStorage
- ✅ Reset to default workflow

## How it works

Each node sends its prompt to the LLM with the instruction to answer 
only YES or NO. The workflow follows the matching edge to the next node 
until it reaches a leaf node with no outgoing edges.

## Example workflow

```
"Is this a support request?"
├── YES → "Route to Support Team"
└── NO  → "Route to Sales Team"
```
