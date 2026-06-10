# Spectator Mode

Watch live games from the lobby — the primary use case: watching two LLM agents play each other (see [[MCP Server]]). Part of [[Chess Webpage]].

## Flow
```
Lobby ──► room list now shows PLAYING rooms too ──► "Watch" button
   ──► spectator joins the room's broadcast list
   ──► sees live board, moves, captures, game over — read-only
   ──► if players rematch, the spectator keeps watching automatically
```

## Server changes
- `Room.spectators: set[WebSocket]` — `broadcast()` reaches seats + spectators
- New message `{type: "spectate", room_id}` → reply `spectate_joined` with a full state snapshot (names, FEN, history, captured); subsequent `board_update`/`game_over`/`game_started` arrive like any player
- Room list entries gain `state` (`waiting`/`playing`) and player names — the client decides Join vs Watch
- `leave_room` and disconnects clean up spectator membership
- Spectators have no seat: `Room.color_of(ws)` returns `None`, so every game action (move/surrender/rematch) is already rejected server-side — no new validation needed

## Client changes
- Lobby: rooms in `waiting` → **Join**; rooms in `playing` → **Watch** (with both player names)
- `spectate_joined` → game view with `myColor = null` (= spectator):
  - Board: view-only (click-to-move already requires owning a color)
  - Status: "White to move" instead of "Your turn"
  - No Surrender button; GameOver overlay shows result + Analyze + Back to lobby (no rematch vote)
  - Orientation: white at bottom
- Rematch by the players → `game_started` arrives → spectator keeps watching seamlessly

## Watching two agents (the point of all this)
1. Run the chess server; open two terminals in `agent_arena/`, run `claude` in each
2. Agent A: "create a room as white and wait" → Agent B: "join room <id>"
3. Open the website → the room shows as playing → **Watch**

## Non-goals (for now)
- Spectator count display, chat, per-spectator delay (anti-cheat) — Phase 4 territory if needed
- Spectating `waiting` rooms (nothing to see)
