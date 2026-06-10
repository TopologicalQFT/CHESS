"""ChessClient: a WebSocket client of the chess server holding one player seat.

Mirrors what the browser client does, but exposes the game to Python
(and through server.py, to an LLM agent via MCP). Also reused directly
by the Phase 4 tournament orchestrator — keep it MCP-free.
"""
import asyncio
import json
import os
from typing import Optional

import chess
import websockets

DEFAULT_URL = "ws://localhost:8000/ws"


class ChessClient:
    def __init__(self, url: Optional[str] = None):
        self.url = url or os.environ.get("CHESS_SERVER_URL", DEFAULT_URL)
        self.ws = None
        self._listen_task: Optional[asyncio.Task] = None

        # Game state (mirrors server broadcasts)
        self.phase = "disconnected"  # disconnected | lobby | waiting | playing | finished
        self.rooms: list = []
        self.room_id: Optional[str] = None
        self.my_color: Optional[str] = None
        self.white_name = ""
        self.black_name = ""
        self.fen = chess.STARTING_FEN
        self.turn = "w"
        self.is_check = False
        self.pgn = ""
        self.result: Optional[dict] = None
        self.last_error: Optional[str] = None
        self.opponent_connected = True

        # Pulses whenever state changes (turn changes, game start/end)
        self._state_changed = asyncio.Event()

    # ── Connection ───────────────────────────────────────────

    async def connect(self) -> None:
        if self.ws is not None:
            return
        self.ws = await websockets.connect(self.url)
        self.phase = "lobby"
        self._listen_task = asyncio.create_task(self._listen())

    async def close(self) -> None:
        if self._listen_task:
            self._listen_task.cancel()
        if self.ws:
            await self.ws.close()
        self.ws = None
        self.phase = "disconnected"

    async def _send(self, payload: dict) -> None:
        await self.connect()
        await self.ws.send(json.dumps(payload))

    async def _listen(self) -> None:
        try:
            async for raw in self.ws:
                self._handle(json.loads(raw))
        except (websockets.ConnectionClosed, asyncio.CancelledError):
            self.phase = "disconnected"
            self._pulse()

    def _handle(self, msg: dict) -> None:
        t = msg.get("type")
        if t == "room_list":
            self.rooms = msg["rooms"]
        elif t == "room_created":
            self.room_id = msg["room_id"]
            self.my_color = msg["color"]
            self.phase = "waiting"
        elif t == "game_started":
            self.my_color = msg["your_color"]
            self.white_name = msg["white_name"]
            self.black_name = msg["black_name"]
            self.fen = msg["fen"]
            self.turn = msg["turn"]
            self.pgn = ""
            self.is_check = False
            self.result = None
            self.phase = "playing"
        elif t == "board_update":
            self.fen = msg["fen"]
            self.turn = msg["turn"]
            self.is_check = msg["is_check"]
            self.pgn = msg["pgn"]
        elif t == "game_over":
            self.result = {
                "result": msg["result"],
                "winner": msg.get("winner"),
                "reason": msg.get("reason"),
                "pgn": msg.get("pgn", ""),
            }
            self.phase = "finished"
        elif t == "error":
            self.last_error = msg["message"]
        elif t == "opponent_disconnected":
            self.opponent_connected = False
        elif t == "opponent_reconnected":
            self.opponent_connected = True
        elif t == "opponent_left":
            self.opponent_connected = False
        self._pulse()

    def _pulse(self) -> None:
        self._state_changed.set()
        self._state_changed = asyncio.Event()

    # ── Lobby actions ────────────────────────────────────────

    async def get_rooms(self) -> list:
        await self._send({"type": "get_rooms"})
        await self._wait_change(2)
        return self.rooms

    async def create_room(self, player_name: str, color: str = "random") -> None:
        self.last_error = None
        await self._send({"type": "create_room", "player_name": player_name, "color": color})
        await self._wait_for(lambda: self.phase == "waiting" or self.last_error, timeout=5)

    async def join_room(self, room_id: str, player_name: str) -> None:
        self.last_error = None
        await self._send({"type": "join_room", "room_id": room_id, "player_name": player_name})
        await self._wait_for(lambda: self.phase == "playing" or self.last_error, timeout=5)

    # ── Game actions ─────────────────────────────────────────

    def board(self) -> chess.Board:
        return chess.Board(self.fen)

    def parse_move(self, move: str) -> Optional[chess.Move]:
        """Accept SAN ('Nf3') or UCI ('g1f3'); None if not legal here."""
        board = self.board()
        try:
            return board.parse_san(move)
        except ValueError:
            pass
        try:
            parsed = chess.Move.from_uci(move.lower())
            if parsed in board.legal_moves:
                return parsed
        except ValueError:
            pass
        return None

    async def make_move(self, move: chess.Move) -> bool:
        """Send a pre-validated move. True once the server confirms."""
        self.last_error = None
        fen_before = self.fen
        payload = {
            "type": "move",
            "from": chess.square_name(move.from_square),
            "to": chess.square_name(move.to_square),
        }
        if move.promotion:
            payload["promotion"] = chess.piece_symbol(move.promotion)
        await self._send(payload)
        await self._wait_for(
            lambda: self.fen != fen_before or self.last_error or self.phase == "finished",
            timeout=5,
        )
        return self.last_error is None

    async def surrender(self) -> None:
        await self._send({"type": "surrender"})
        await self._wait_for(lambda: self.phase == "finished", timeout=5)

    async def wait_for_my_turn(self, timeout: float) -> str:
        """Block until it's our move, the game ends, or timeout.

        Returns: 'your_turn' | 'game_over' | 'timeout' | 'waiting_for_opponent'
        """
        def ready():
            if self.phase == "finished":
                return "game_over"
            if self.phase == "playing" and self.turn == self.my_color:
                return "your_turn"
            return None

        state = ready()
        if state:
            return state
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                return "timeout" if self.phase == "playing" else "waiting_for_opponent"
            await self._wait_change(remaining)
            state = ready()
            if state:
                return state

    # ── Internals ────────────────────────────────────────────

    async def _wait_change(self, timeout: float) -> None:
        event = self._state_changed
        try:
            await asyncio.wait_for(event.wait(), timeout)
        except asyncio.TimeoutError:
            pass

    async def _wait_for(self, predicate, timeout: float) -> None:
        deadline = asyncio.get_running_loop().time() + timeout
        while not predicate():
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                return
            await self._wait_change(remaining)
