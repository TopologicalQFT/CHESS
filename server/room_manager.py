"""Room lifecycle and the per-room game loop."""
import asyncio
import secrets
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

import chess
from fastapi import WebSocket

from game_engine import GameEngine
from player import HumanPlayer, MoveRequest

CHAT_LIMIT = 100  # messages kept per room


class Room:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.state = "waiting"  # waiting | playing | finished
        self.players: Dict[str, Optional[HumanPlayer]] = {"w": None, "b": None}
        self.sockets: Dict[str, Optional[WebSocket]] = {"w": None, "b": None}
        self.spectators: Set[WebSocket] = set()
        self.chat: List[dict] = []  # last CHAT_LIMIT messages, survives rematches
        self.time_control: Optional[int] = None  # seconds per player, None = no clock
        self.clock: Dict[str, float] = {}
        self._turn_started: Optional[float] = None
        self.engine: Optional[GameEngine] = None
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.game_task: Optional[asyncio.Task] = None
        self.rematch_votes = {"w": False, "b": False}
        # Awaitable invoked when the room's lobby visibility changes
        # (start/end of games) — wired to the lobby push in main.py.
        self.on_state_change = None

    # ── Helpers ──────────────────────────────────────────────

    def creator_name(self) -> str:
        for player in self.players.values():
            if player is not None:
                return player.name
        return "?"

    def available_color(self) -> Optional[str]:
        for color in ("w", "b"):
            if self.players[color] is None:
                return color
        return None

    def opponent(self, color: str) -> str:
        return "b" if color == "w" else "w"

    def color_of(self, ws: WebSocket) -> Optional[str]:
        """Which seat this socket occupies — survives rematch color swaps."""
        for color in ("w", "b"):
            if self.sockets[color] is ws:
                return color
        return None

    def is_full(self) -> bool:
        return self.players["w"] is not None and self.players["b"] is not None

    # ── Messaging ────────────────────────────────────────────

    async def send_to(self, color: str, payload: dict) -> None:
        ws = self.sockets.get(color)
        if ws is None:
            return
        try:
            await ws.send_json(payload)
        except Exception:
            pass  # socket already closed; disconnect handler deals with it

    async def broadcast(self, payload: dict) -> None:
        await self.send_to("w", payload)
        await self.send_to("b", payload)
        for ws in list(self.spectators):
            try:
                await ws.send_json(payload)
            except Exception:
                self.spectators.discard(ws)

    # ── Game flow ────────────────────────────────────────────

    def clock_snapshot(self) -> Optional[dict]:
        """Current remaining time per color, live-adjusted for the side to move."""
        if self.time_control is None or not self.clock:
            return None
        snap = dict(self.clock)
        if (self.state == "playing" and self._turn_started is not None
                and self.engine is not None):
            turn = self.engine.turn()
            elapsed = asyncio.get_event_loop().time() - self._turn_started
            snap[turn] = max(0.0, snap[turn] - elapsed)
        return {"w": round(snap["w"], 1), "b": round(snap["b"], 1)}

    async def start_game(self) -> None:
        self.engine = GameEngine()
        self.state = "playing"
        self.rematch_votes = {"w": False, "b": False}
        if self.time_control is not None:
            self.clock = {"w": float(self.time_control), "b": float(self.time_control)}
        self._turn_started = None

        def started_payload(your_color: Optional[str]) -> dict:
            return {
                "type": "game_started",
                "fen": self.engine.board.fen(),
                "your_color": your_color,
                "white_name": self.players["w"].name,
                "black_name": self.players["b"].name,
                "legal_moves": self.engine.legal_moves(),
                "turn": "w",
                "time_control": self.time_control,
                "clock": self.clock_snapshot(),
            }

        for color in ("w", "b"):
            await self.send_to(color, started_payload(color))
        for ws in list(self.spectators):
            try:
                await ws.send_json(started_payload(None))
            except Exception:
                self.spectators.discard(ws)
        self.game_task = asyncio.create_task(self._game_loop())
        if self.on_state_change:
            await self.on_state_change()

    async def _game_loop(self) -> None:
        """Ask the current player for a move, apply, broadcast, repeat.
        With a time control, the wait is bounded by the mover's clock."""
        try:
            while True:
                turn = self.engine.turn()
                player = self.players[turn]
                request = MoveRequest(
                    fen=self.engine.board.fen(),
                    legal_moves_uci=self.engine.legal_moves_uci(),
                    turn=turn,
                )
                if self.time_control is not None:
                    loop = asyncio.get_event_loop()
                    self._turn_started = loop.time()
                    remaining = self.clock[turn]
                    try:
                        uci = await asyncio.wait_for(
                            player.request_move(request), timeout=remaining
                        )
                    except asyncio.TimeoutError:
                        await self._flag(turn)
                        return
                    self.clock[turn] = max(0.0, remaining - (loop.time() - self._turn_started))
                else:
                    uci = await player.request_move(request)

                if self.engine.make_move(uci) is None:
                    await self.send_to(turn, {"type": "error", "message": "Illegal move"})
                    continue
                await self.broadcast({
                    "type": "board_update",
                    **self.engine.board_update(),
                    "clock": self.clock_snapshot(),
                })

                result = self.engine.result()
                if result is not None:
                    await self.end_game(result)
                    return
        except asyncio.CancelledError:
            return  # surrender / leave / shutdown

    async def _flag(self, color: str) -> None:
        """`color` ran out of time. Win for the opponent — unless they cannot
        possibly mate, in which case it's a draw (standard chess rule)."""
        self.clock[color] = 0.0
        opponent = self.opponent(color)
        opp_chess_color = chess.WHITE if opponent == "w" else chess.BLACK
        if self.engine.board.has_insufficient_material(opp_chess_color):
            await self.end_game({
                "result": "draw", "winner": None,
                "reason": "timeout_vs_insufficient_material",
            })
        else:
            await self.end_game({"result": "timeout", "winner": opponent, "reason": None})

    async def end_game(self, result: dict) -> None:
        self.state = "finished"
        payload = {"type": "game_over", "pgn": self.engine.pgn() if self.engine else "", **result}
        await self.broadcast(payload)
        if self.on_state_change:
            await self.on_state_change()

    async def surrender(self, color: str) -> None:
        if self.state != "playing":
            return
        if self.game_task is not None:
            self.game_task.cancel()
        await self.end_game({
            "result": "resignation",
            "winner": self.opponent(color),
            "reason": None,
        })

    async def post_chat(self, sender: str, role: str, text: str) -> None:
        """role: 'w' | 'b' | 'spectator'. Stores and broadcasts."""
        entry = {"type": "chat", "sender": sender, "role": role, "text": text}
        self.chat.append(entry)
        if len(self.chat) > CHAT_LIMIT:
            self.chat = self.chat[-CHAT_LIMIT:]
        await self.broadcast(entry)

    async def vote_rematch(self, color: str) -> None:
        if self.state != "finished":
            return
        self.rematch_votes[color] = True
        if all(self.rematch_votes.values()):
            # Swap colors and restart
            self.players["w"], self.players["b"] = self.players["b"], self.players["w"]
            self.sockets["w"], self.sockets["b"] = self.sockets["b"], self.sockets["w"]
            for color_key in ("w", "b"):
                player = self.players[color_key]
                if player is not None:
                    player.color = color_key
            await self.start_game()
        else:
            await self.send_to(self.opponent(color), {"type": "rematch_offered"})

    def shutdown(self) -> None:
        if self.game_task is not None:
            self.game_task.cancel()
        for player in self.players.values():
            if player is not None:
                player.cancel_pending_move()


class RoomManager:
    def __init__(self) -> None:
        self.rooms: Dict[str, Room] = {}
        self.on_rooms_changed = None  # set by main.py → lobby push

    def create_room(self) -> Room:
        room_id = secrets.token_hex(3)  # 6-char id
        while room_id in self.rooms:
            room_id = secrets.token_hex(3)
        room = Room(room_id)
        room.on_state_change = self.on_rooms_changed
        self.rooms[room_id] = room
        return room

    def get(self, room_id: str) -> Optional[Room]:
        return self.rooms.get(room_id)

    def remove(self, room_id: str) -> None:
        room = self.rooms.pop(room_id, None)
        if room is not None:
            room.shutdown()

    def open_rooms(self) -> List[dict]:
        """Rooms shown in the lobby: joinable (waiting) and watchable (playing)."""
        entries = []
        for room in self.rooms.values():
            if room.state == "waiting" and not room.is_full():
                entries.append({
                    "room_id": room.room_id,
                    "state": "waiting",
                    "creator": room.creator_name(),
                    "available_color": room.available_color(),
                    "created_at": room.created_at,
                    "time_control": room.time_control,
                })
            elif room.state == "playing":
                entries.append({
                    "room_id": room.room_id,
                    "state": "playing",
                    "creator": room.creator_name(),
                    "white_name": room.players["w"].name if room.players["w"] else "?",
                    "black_name": room.players["b"].name if room.players["b"] else "?",
                    "available_color": None,
                    "created_at": room.created_at,
                    "time_control": room.time_control,
                })
        return entries
