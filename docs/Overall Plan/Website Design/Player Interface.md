# Player Interface

Server-side abstraction from [[Chess Webpage]]. Lives in `server/player.py`.

## The Abstraction

The game engine doesn't know what kind of player it's dealing with — human or AI. It just asks for a move and awaits the response.

```python
from abc import ABC, abstractmethod
from models import MoveRequest, MoveResponse

class Player(ABC):
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color  # "w" or "b"

    @abstractmethod
    async def request_move(self, request: MoveRequest) -> MoveResponse:
        """Ask the player for a move. Resolves when they decide."""
        ...

    @abstractmethod
    async def cancel_pending_move(self) -> None:
        """Cancel a pending move request (game reset/surrender)."""
        ...
```

## MoveRequest (what the player receives)
```python
class MoveRequest(BaseModel):
    fen: str               # Current position
    legal_moves: list[str] # UCI strings: ["e2e4", "d2d4", ...]
    legal_moves_san: list[str]  # SAN strings: ["e4", "d4", ...]
    history: list[str]     # Moves so far (SAN)
    turn: str              # "w" or "b"
```

## MoveResponse (what the player returns)
```python
class MoveResponse(BaseModel):
    uci: str  # UCI move string, e.g. "e2e4", "e7e8q" (with promotion)
```

## Phase 1 Implementation: HumanPlayer

```python
class HumanPlayer(Player):
    """Bridges WebSocket input to the game engine's async interface."""

    def __init__(self, name: str, color: str):
        super().__init__(name, color)
        self._pending: asyncio.Future | None = None

    async def request_move(self, request: MoveRequest) -> MoveResponse:
        # Creates a Future; resolved when WebSocket handler calls submit_move()
        self._pending = asyncio.get_event_loop().create_future()
        return await self._pending

    def submit_move(self, uci: str) -> None:
        """Called by WebSocket message handler when player sends a move."""
        if self._pending and not self._pending.done():
            self._pending.set_result(MoveResponse(uci=uci))

    async def cancel_pending_move(self) -> None:
        if self._pending and not self._pending.done():
            self._pending.cancel()
        self._pending = None
```

## Phase 2 (future): LLMPlayer
```python
class LLMPlayer(Player):
    """Sends position to LLM via MCP, awaits move decision."""

    async def request_move(self, request: MoveRequest) -> MoveResponse:
        # Send board state + legal moves to LLM
        # Await LLM's chosen move
        # Validate it's in legal_moves
        # Return MoveResponse
        ...
```

Same `Player` interface, zero engine changes.
