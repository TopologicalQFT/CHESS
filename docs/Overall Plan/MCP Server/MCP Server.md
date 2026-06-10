# Phase 2: MCP Server

Part of [[Project Overview]].

## Goal
Let any MCP-capable LLM agent (Claude Code, Claude Desktop, …) join a chess room and play — **no LLM API keys, no per-token billing on our side**. The agent brings its own intelligence; we provide the hands and eyes.

## Architecture: Bridge Pattern

The MCP server is a **bridge**: an MCP stdio server on one side, a WebSocket client of the chess server on the other. The chess server doesn't change at all — the bridge looks exactly like a browser client to it.

```
┌─────────────┐   stdio (MCP)   ┌─────────────────┐   WebSocket    ┌──────────────┐
│  LLM Agent  │ ◄─────────────► │   MCP Bridge    │ ◄────────────► │ Chess Server │
│ (Claude...) │    tool calls   │  (mcp_bridge/)  │   same proto   │  (FastAPI)   │
└─────────────┘                 └─────────────────┘   as browser   └──────────────┘
```

- One bridge process = one player seat. (AI vs AI = two agents, each with its own bridge connection.)
- Target server is configurable: `CHESS_SERVER_URL` env var, default `ws://localhost:8000/ws`, can point to `wss://chess-2qy3.onrender.com/ws`.
- Python 3.12 + official `mcp` SDK (FastMCP), `websockets`, `chess` (python-chess for board rendering + SAN).

## Tools (what the agent sees)

| Tool | Args | Returns |
|------|------|---------|
| `list_rooms` | — | Open rooms: id, creator, available color |
| `create_room` | `player_name`, `color` (w/b/random) | Room code to share; tells agent to call `wait_for_my_turn` |
| `join_room` | `room_id`, `player_name` | Confirmation + initial board if game starts |
| `get_board` | — | Full position report (see below) |
| `make_move` | `move` (SAN like "Nf3" or UCI like "g1f3") | Updated position, or error with legal moves |
| `wait_for_my_turn` | `timeout_seconds` (default 55) | Blocks until it's the agent's turn / game over / timeout (re-call on timeout) |
| `surrender` | — | Confirms resignation |
| `game_status` | — | Quick state check: phase, whose turn, result |

## Board Representation (the agent's "eyes")

`get_board` and `wait_for_my_turn` return a text report assembled by the bridge (the server only sends FEN + move dicts; the bridge enriches with python-chess):

```
You are playing Black. It is YOUR turn (move 4).

  8 r . b q k b . r
  7 p p p p . p p p
  6 . . n . . n . .
  5 . . . . p . . .
  4 . . B . P . . .
  3 . . . . . N . .
  2 P P P P . P P P
  1 R N B Q K . . R
    a b c d e f g h

FEN: r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 5 4
History: 1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6
Check: no
Your legal moves (SAN): Nxe4, Bb4, Be7, Bd6, Bc5, a6, b6, d6, ...
```

This default format is deliberately simple — **Phase 3 ([[Prompt Engineering]]) will experiment with what representation helps LLMs play best** (ASCII vs FEN-only vs natural language). The bridge is where those experiments will plug in.

## Agent Game Loop

The natural flow for the agent:

```
join_room(...)            → seated, game may start immediately
wait_for_my_turn()        → returns the board report when it's time
make_move("e5")           → move applied, opponent's turn
wait_for_my_turn()        → blocks during opponent thinking
…repeat until game over
```

`wait_for_my_turn` returns within ~55s even if nothing happened (MCP client timeouts), with a "still waiting — call again" message. The agent just re-calls.

## Move Validation Layers
1. Bridge parses SAN/UCI with python-chess against the current FEN → friendly error with legal move list if invalid (the LLM gets a second chance without burning a turn).
2. Server validates again via its own engine (never trusts any client, bridge included).

## Setup

### Claude Code (this repo)
`.mcp.json` in the repo root registers the bridge as a project MCP server. Start the chess server, open Claude Code, and the `chess` tools appear.

### Claude Desktop (later)
Same command in `claude_desktop_config.json` → `mcpServers`.

## Files
```
mcp_bridge/
├── requirements.txt    # mcp, websockets, chess
├── .venv/              # Python 3.12 (3.9 can't run the MCP SDK)
├── bridge.py           # ChessClient: WS connection, state, turn events
└── server.py           # FastMCP tool definitions, entry point
```

## Phase 4 Note
For tournaments, the orchestrator will spawn bridge connections programmatically — same `ChessClient` class, no MCP layer needed for automated runs. The `ChessClient` ↔ tool separation in the bridge exists precisely for that reuse.
