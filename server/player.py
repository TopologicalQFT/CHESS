"""Player abstraction.

The room's game loop awaits `request_move()` without knowing what kind
of player is behind it. HumanPlayer resolves via WebSocket input;
Phase 2 will add an LLMPlayer with the same interface.
"""
import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional


class MoveRequest:
    def __init__(self, fen: str, legal_moves_uci: List[str], turn: str):
        self.fen = fen
        self.legal_moves_uci = legal_moves_uci
        self.turn = turn


class Player(ABC):
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color  # "w" | "b"
        self.connected = True

    @abstractmethod
    async def request_move(self, request: MoveRequest) -> str:
        """Return a UCI move string. Awaited by the room's game loop."""

    @abstractmethod
    def cancel_pending_move(self) -> None:
        """Abort a pending request (surrender, disconnect, reset)."""


class HumanPlayer(Player):
    """Bridges WebSocket messages to the async game loop via a Future."""

    def __init__(self, name: str, color: str):
        super().__init__(name, color)
        self._pending: Optional[asyncio.Future] = None

    async def request_move(self, request: MoveRequest) -> str:
        self._pending = asyncio.get_event_loop().create_future()
        try:
            return await self._pending
        finally:
            self._pending = None

    def submit_move(self, uci: str) -> bool:
        """Called by the WebSocket handler. Returns False if no move was expected."""
        if self._pending is None or self._pending.done():
            return False
        self._pending.set_result(uci)
        return True

    def cancel_pending_move(self) -> None:
        if self._pending is not None and not self._pending.done():
            self._pending.cancel()
