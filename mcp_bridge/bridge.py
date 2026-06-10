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
        self.last_san: Optional[str] = None
        self.chat_inbox: list = []  # messages from others since last drain
        self.clock: Optional[dict] = None  # {"w": sec, "b": sec} when timed
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

    def _reset_room_state(self) -> None:
        """Forget the seat — after leaving a room or losing the connection
        (a fresh WebSocket is a fresh server session; old seats are gone)."""
        self.room_id = None
        self.my_color = None
        self.result = None
        self.last_error = None

    async def _reconnect(self) -> None:
        """Fresh socket; then try to reclaim a live seat instead of
        discarding it (a mid-game drop must not forfeit the game)."""
        had_seat = self.room_id is not None and self.my_color is not None
        await self.connect()
        if had_seat:
            await self.ws.send(json.dumps({
                "type": "reconnect", "room_id": self.room_id, "color": self.my_color,
            }))
            # game_restored re-seats us; reconnect_failed resets room state
            await self._wait_for(
                lambda: self.phase in ("playing", "finished") or self.room_id is None,
                timeout=5,
            )
            if self.phase == "lobby" and self.room_id is not None:
                self._reset_room_state()  # no verdict from server — assume seat lost
        else:
            self._reset_room_state()

    async def _send(self, payload: dict) -> None:
        if self.ws is None:
            await self._reconnect()
        try:
            await self.ws.send(json.dumps(payload))
        except websockets.ConnectionClosed:
            # Socket died since the last call — one clean reconnect + retry
            self.ws = None
            await self._reconnect()
            await self.ws.send(json.dumps(payload))

    async def _listen(self) -> None:
        ws = self.ws
        try:
            async for raw in ws:
                self._handle(json.loads(raw))
        except (websockets.ConnectionClosed, asyncio.CancelledError):
            pass
        finally:
            # Only clear if a reconnect hasn't already replaced the socket
            if self.ws is ws:
                self.ws = None
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
            self.last_san = None
            self.clock = msg.get("clock")
            self.phase = "playing"
        elif t == "board_update":
            self.fen = msg["fen"]
            self.turn = msg["turn"]
            self.is_check = msg["is_check"]
            self.pgn = msg["pgn"]
            self.last_san = msg.get("move_san")
            self.clock = msg.get("clock")
        elif t == "game_over":
            self.result = {
                "result": msg["result"],
                "winner": msg.get("winner"),
                "reason": msg.get("reason"),
                "pgn": msg.get("pgn", ""),
            }
            self.phase = "finished"
        elif t == "game_restored":
            # Seat reclaimed after a mid-game reconnect
            self.my_color = msg.get("your_color", self.my_color)
            self.white_name = msg.get("white_name", self.white_name)
            self.black_name = msg.get("black_name", self.black_name)
            if "fen" in msg:
                self.fen = msg["fen"]
                self.turn = msg.get("turn", "w")
                self.is_check = msg.get("is_check", False)
                self.pgn = msg.get("pgn", "")
                self.last_san = msg.get("move_san")
                self.clock = msg.get("clock")
            self.phase = msg.get("room_state", "playing")
        elif t == "reconnect_failed":
            self._reset_room_state()
            self.phase = "lobby" if self.ws is not None else "disconnected"
        elif t == "chat":
            # Keep only others' messages (our own echo back is just confirmation)
            if msg.get("role") != self.my_color:
                self.chat_inbox.append(msg)
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

    async def create_room(self, player_name: str, color: str = "random",
                          time_control: Optional[int] = None) -> None:
        if self.phase == "finished":
            await self.leave_room()
        self.last_error = None
        payload = {"type": "create_room", "player_name": player_name, "color": color}
        if time_control:
            payload["time_control"] = time_control
        await self._send(payload)
        await self._wait_for(lambda: self.phase == "waiting" or self.last_error, timeout=5)

    async def join_room(self, room_id: str, player_name: str) -> None:
        if self.phase == "finished":
            await self.leave_room()
        self.last_error = None
        await self._send({"type": "join_room", "room_id": room_id, "player_name": player_name})
        await self._wait_for(lambda: self.phase == "playing" or self.last_error, timeout=5)

    async def leave_room(self) -> None:
        """Leave the current room (resigns first if a game is running).

        ALWAYS tells the server, even if local state says we're in the lobby —
        local and server state can desync (ghost-room bug report), and the
        server ignores a leave from a session that isn't seated anyway."""
        await self._send({"type": "leave_room"})
        self._reset_room_state()
        if self.phase != "disconnected":
            self.phase = "lobby"

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

    async def send_chat(self, text: str) -> None:
        await self._send({"type": "chat", "text": text})

    def drain_chat(self) -> list:
        """Return and clear unseen messages from others."""
        inbox, self.chat_inbox = self.chat_inbox, []
        return inbox

    async def surrender(self) -> None:
        await self._send({"type": "surrender"})
        await self._wait_for(lambda: self.phase == "finished", timeout=5)

    async def wait_for_my_turn(self, timeout: float) -> str:
        """Block until it's our move, the game ends, or timeout.

        Returns: 'your_turn' | 'game_over' | 'timeout' |
                 'waiting_for_opponent' | 'disconnected'
        """
        def ready():
            if self.phase == "finished":
                return "game_over"
            if self.phase == "playing" and self.turn == self.my_color:
                return "your_turn"
            return None

        async def resurrect() -> bool:
            """Socket died mid-wait: reconnect and reclaim the seat."""
            try:
                self.ws = None
                await self._reconnect()
                return self.phase in ("playing", "finished", "waiting")
            except Exception:
                return False

        if self.phase == "disconnected" and not await resurrect():
            return "disconnected"
        state = ready()
        if state:
            return state
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                return "timeout" if self.phase == "playing" else "waiting_for_opponent"
            await self._wait_change(remaining)
            if self.phase == "disconnected" and not await resurrect():
                return "disconnected"
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
