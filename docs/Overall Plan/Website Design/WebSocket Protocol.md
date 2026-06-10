# WebSocket Protocol

Communication protocol between React frontend and Python backend for [[Chess Webpage]].

## Connection
- Endpoint: `ws://localhost:8000/ws`
- Single WebSocket per client session
- All messages are JSON with a `type` field

## Client → Server Messages

### Lobby
```json
{ "type": "get_rooms" }

{ "type": "create_room", "player_name": "Alice", "color": "w" }
// color: "w" | "b" | "random"

{ "type": "join_room", "room_id": "abc123", "player_name": "Bob" }

{ "type": "spectate", "room_id": "abc123" }
```
See [[Spectator Mode]] — spectators get a `spectate_joined` snapshot, then the same
broadcasts as players (`board_update`, `game_over`, `game_started` with `your_color: null`).
A `room_closed` message means both players abandoned the room.

### In-Game
```json
{ "type": "move", "from": "e2", "to": "e4" }

{ "type": "move", "from": "e7", "to": "e8", "promotion": "q" }

{ "type": "surrender" }

{ "type": "leave_room" }

{ "type": "rematch" }
```

## Server → Client Messages

### Lobby Responses
```json
{ "type": "room_created", "room_id": "abc123", "color": "w" }

{ "type": "room_list", "rooms": [
    { "room_id": "abc123", "creator": "Alice", "available_color": "b", "created_at": "..." }
  ]
}
```

### Game Events
```json
{ "type": "room_joined", "opponent_name": "Bob" }

{ "type": "game_started",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "your_color": "w",
  "white_name": "Alice",
  "black_name": "Bob" }

{ "type": "board_update",
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "last_move": { "from": "e2", "to": "e4" },
  "legal_moves": [ { "from": "a7", "to": "a6" }, ... ],
  "turn": "b",
  "is_check": false,
  "pgn": "1. e4",
  "captured": { "w": [], "b": [] },
  "move_san": "e4" }

{ "type": "game_over",
  "result": "checkmate",
  "winner": "w",
  "pgn": "1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#" }
// result: "checkmate" | "stalemate" | "resignation" | "draw"
// winner: "w" | "b" | null (for draws)

{ "type": "opponent_disconnected" }
{ "type": "opponent_reconnected" }
```

### Errors
```json
{ "type": "error", "message": "Not your turn" }
{ "type": "error", "message": "Illegal move" }
{ "type": "error", "message": "Room not found" }
{ "type": "error", "message": "Room is full" }
```

## State Transitions (Server-Side)

```
Client connects → can send get_rooms, create_room, join_room
       │
  create/join → enters a room
       │
  both players in room → server sends game_started to both
       │
  game in progress → clients send moves, server validates + broadcasts
       │
  game ends → server sends game_over → clients can send rematch or leave_room
```

## Reconnection
- If a WebSocket drops, the client reconnects and sends `{ "type": "reconnect", "room_id": "..." }`
- Server restores the player's seat and sends current game state
- Opponent receives `opponent_reconnected`

## Design Notes
- The server **never trusts** the client's board state — python-chess is the source of truth
- `legal_moves` is sent with every `board_update` so the frontend can show move hints without any chess logic
- `captured` is computed server-side from the move history
