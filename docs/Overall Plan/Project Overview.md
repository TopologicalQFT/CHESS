# LLM Chess Project — Overview

## Vision
A platform for playing and watching chess — humans against humans, humans against LLMs, and LLMs against each other. Compare how different models and prompting strategies affect play quality. Built incrementally in four phases.

## Phases

### Phase 1: [[Chess Webpage]]
Networked chess game with room-based multiplayer.
- Python backend (FastAPI + python-chess) with WebSocket real-time communication
- React frontend as a thin display/input client
- Room system: create, choose color, join, ready, play, surrender
- First milestone: **clean HvH (Human vs Human)** over the network
- **Status:** HvH working — lobby, rooms, full games, surrender, rematch all verified end-to-end

### Phase 2: [[MCP Server]]
MCP server that connects LLM agents to the chess backend.
- Exposes board state, legal moves, game history to LLMs
- Accepts move decisions back
- LLM joins a room as a player — same server-side Player abstraction
- **Status:** Not started

### Phase 3: [[Prompt Engineering]]
Craft prompts and contexts that help LLMs play better chess.
- Board representation formats (FEN vs visual vs natural language)
- Strategic guidance (opening principles, tactics, positional play)
- Context window management
- **Status:** Not started

### Phase 4: [[LLM Tournament]]
Run tournaments between different models and prompting strategies.
- Multiple concurrent games
- ELO rating system
- Comparison across: models, prompt styles, context lengths
- Results dashboard
- **Status:** Not started

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, WebSocket |
| Chess Logic | python-chess |
| Frontend | React 19 + TypeScript, Vite |
| Board Rendering | Custom SVG |
| Real-time | WebSocket (bidirectional) |
| LLM Providers | Claude (initially), expand later |

## Key Design Principle
> The **server owns the game**. All chess logic, validation, and state live on the Python backend. The frontend is a view layer that sends user intents and renders server state. This makes it trivial to plug in LLM players server-side in Phase 2 — they're just another WebSocket client (or internal player) to the game engine.
