# Implementation Order

Build sequence for [[Chess Webpage]]. Focused on getting **clean HvH** working first.

## Step 1: Project Scaffold
- **Server:** `server/` with `pyproject.toml` (FastAPI, uvicorn, python-chess), basic `main.py` with health check
- **Client:** `client/` via `npm create vite@latest` with react-ts template
- Download CBurnett piece SVGs into `client/src/assets/pieces/`
- **Checkpoint:** both `uvicorn` and `npm run dev` start without errors

## Step 2: Server — Game Engine
- `server/game_engine.py` — wrapper around `python-chess`:
  - `new_game()`, `make_move(uci)`, `get_board_state()`, `get_legal_moves()`
  - Game-over detection (checkmate, stalemate, draws)
  - Captured pieces computation
  - PGN generation
- **Checkpoint:** unit-test the engine in isolation

## Step 3: Server — Room Manager + WebSocket
- `server/models.py` — Pydantic models for all WS messages (see [[WebSocket Protocol]])
- `server/room_manager.py` — create room, join room, list rooms, leave room
- `server/player.py` — `HumanPlayer` with the asyncio.Future pattern (see [[Player Interface]])
- `server/main.py` — WebSocket endpoint, message routing, room lifecycle
- **Checkpoint:** connect via wscat/Postman, create a room, see it in room list

## Step 4: Server — Game Loop
- Wire `GameEngine` into rooms: when both players join, start the game loop
- Game loop: ask current player for move → validate → apply → broadcast `board_update`
- Handle surrender (cancel pending move, broadcast `game_over`)
- Handle disconnection (pause game, notify opponent)
- **Checkpoint:** two wscat clients can play a full game via JSON messages

## Step 5: Client — WebSocket + Lobby
- `useWebSocket` hook — connect, reconnect, send/receive JSON
- `WebSocketContext` — provide WS to all components
- `LobbyPage` — create room (choose color), browse + join rooms
- `WaitingOverlay` — "Waiting for opponent..." with room code
- **Checkpoint:** create and join rooms from the browser

## Step 6: Client — SVG Board (Static)
- `Board.tsx` — SVG 8×8 grid, light/dark squares
- `Square.tsx`, `Piece.tsx` — render pieces from FEN
- Board orientation based on player's color
- Wire to `GameContext` — board renders the server's FEN
- **Checkpoint:** board shows starting position when game starts

## Step 7: Client — Click-to-Move
- `useBoardInteraction` hook — piece selection, legal move filtering from server's `legal_moves`
- First click: select piece (only own pieces, only on your turn)
- Second click: if legal destination → send `move` via WS; if own piece → reselect; else → deselect
- `BoardOverlays` — legal move dots, last move highlight, check highlight
- `PromotionDialog` — Q/R/B/N picker when pawn reaches last rank
- **Checkpoint:** two browser tabs can play a full game of chess

## Step 8: Client — Sidebar
- `PlayerInfo` — names, colors (top = opponent, bottom = you)
- `GameStatus` — "Your turn" / "Opponent's turn" / "Check!" / result
- `MoveHistory` — scrollable PGN, auto-scroll to latest
- `CapturedPieces` — piece icons for captured material

## Step 9: Client — Game Controls + Overlays
- `SurrenderButton` — with confirmation dialog, sends `surrender` via WS
- `GameOverOverlay` — result message, rematch button, back-to-lobby button
- Rematch flow: sends `rematch` → server creates new room with swapped colors
- `LeaveButton` — exits room back to lobby

## Step 10: Polish
- Responsive CSS (board scales to viewport)
- Smooth transitions on highlights
- Clean typography, dark/light theme ready
- Error handling (invalid moves show brief toast, reconnection UI)
- **Checkpoint:** feels like a proper chess site
