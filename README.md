# Chess

Networked chess platform. Phase 1: Human vs Human in the browser.
Later phases: MCP server for LLM players, prompt engineering, LLM tournaments.

## Stack
- **Server:** Python, FastAPI, python-chess, WebSocket
- **Client:** React + TypeScript, Vite, custom SVG board

## Run locally

```bash
# Server (port 8000)
cd server
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # Windows
.venv/Scripts/python -m uvicorn main:app --port 8000

# Client (port 5173)
cd client
npm install
npm run dev
```

Open http://localhost:5173 in two browser windows and play.

## Tests

```bash
cd server && .venv/Scripts/python -m pytest -q   # engine + WS integration
cd client && node e2e/hvh.mjs                     # two-browser e2e (servers must be running)
```

## Deploy (Render)

The repo has a `Dockerfile` (builds client, serves it from FastAPI) and
`render.yaml`. On Render: **New → Web Service → connect this repo** —
it auto-detects both. Free tier works (sleeps when idle).

## Docs

Planning docs live in `docs/` as an Obsidian vault.
