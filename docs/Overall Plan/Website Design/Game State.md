# Game State

Server-side state model for [[Chess Webpage]]. The server is the single source of truth; the client receives snapshots via [[WebSocket Protocol]].

## Server-Side: Room + Game

```python
class RoomState(str, Enum):
    WAITING = "waiting"      # Creator in room, awaiting opponent
    PLAYING = "playing"      # Game in progress
    FINISHED = "finished"    # Game over

class Room:
    room_id: str
    state: RoomState
    white: Player | None
    black: Player | None
    game: GameEngine | None  # Created when both players are in
    created_at: datetime

class GameResult(BaseModel):
    result: str      # "checkmate" | "stalemate" | "resignation" | "draw"
    winner: str | None  # "w" | "b" | None (for draws)
    reason: str | None  # "insufficient_material" | "threefold_repetition" | ...
```

## Server-Side: GameEngine State

Derived from the `python-chess` board on every update:

```python
class BoardUpdate(BaseModel):
    fen: str
    last_move: dict | None        # { "from": "e2", "to": "e4" }
    legal_moves: list[dict]       # [{ "from": "e7", "to": "e5" }, ...]
    turn: str                     # "w" | "b"
    is_check: bool
    pgn: str
    captured: dict                # { "w": ["p", "n"], "b": ["p"] }
    move_san: str | None          # SAN of the last move: "e4"
    fullmove_number: int
```

## Client-Side: React State

The client maintains a local mirror of the server's game state, updated on each WebSocket event:

```typescript
interface ClientGameState {
  // Connection
  connected: boolean;
  roomId: string | null;
  roomState: 'lobby' | 'waiting' | 'playing' | 'finished';

  // Players
  myColor: 'w' | 'b' | null;
  whiteName: string;
  blackName: string;

  // Board (from server's board_update)
  fen: string;
  lastMove: { from: string; to: string } | null;
  legalMoves: { from: string; to: string; promotion?: string }[];
  turn: 'w' | 'b';
  isCheck: boolean;
  pgn: string;
  captured: { w: string[]; b: string[] };

  // UI-only state (not from server)
  selectedSquare: string | null;
  highlightedSquares: string[];
  showPromotionDialog: boolean;
  pendingPromotion: { from: string; to: string } | null;

  // Game result
  result: GameResult | null;
}
```

## State Source of Truth
- **python-chess** board on the server is the single source of truth
- Server sends `board_update` after every move — client replaces its board state
- Client never computes legal moves, check status, or game-over conditions
- UI-only state (selection, highlights) lives purely in React
