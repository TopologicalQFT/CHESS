"""Room lifecycle and the per-room game loop."""
import asyncio
import secrets
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import WebSocket

from game_engine import GameEngine
from player import HumanPlayer, MoveRequest


class Room:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.state = "waiting"  # waiting | playing | finished
        self.players: Dict[str, Optional[HumanPlayer]] = {"w": None, "b": None}
        self.sockets: Dict[str, Optional[WebSocket]] = {"w": None, "b": None}
        self.engine: Optional[GameEngine] = None
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.game_task: Optional[asyncio.Task] = None
        self.rematch_votes = {"w": False, "b": False}

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

    # ── Game flow ────────────────────────────────────────────

    async def start_game(self) -> None:
        self.engine = GameEngine()
        self.state = "playing"
        self.rematch_votes = {"w": False, "b": False}
        for color in ("w", "b"):
            await self.send_to(color, {
                "type": "game_started",
                "fen": self.engine.board.fen(),
                "your_color": color,
                "white_name": self.players["w"].name,
                "black_name": self.players["b"].name,
                "legal_moves": self.engine.legal_moves(),
                "turn": "w",
            })
        self.game_task = asyncio.create_task(self._game_loop())

    async def _game_loop(self) -> None:
        """Ask the current player for a move, apply, broadcast, repeat."""
        try:
            while True:
                turn = self.engine.turn()
                player = self.players[turn]
                request = MoveRequest(
                    fen=self.engine.board.fen(),
                    legal_moves_uci=self.engine.legal_moves_uci(),
                    turn=turn,
                )
                uci = await player.request_move(request)
                if self.engine.make_move(uci) is None:
                    await self.send_to(turn, {"type": "error", "message": "Illegal move"})
                    continue
                await self.broadcast({"type": "board_update", **self.engine.board_update()})

                result = self.engine.result()
                if result is not None:
                    await self.end_game(result)
                    return
        except asyncio.CancelledError:
            return  # surrender / leave / shutdown

    async def end_game(self, result: dict) -> None:
        self.state = "finished"
        payload = {"type": "game_over", "pgn": self.engine.pgn() if self.engine else "", **result}
        await self.broadcast(payload)

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

    def create_room(self) -> Room:
        room_id = secrets.token_hex(3)  # 6-char id
        while room_id in self.rooms:
            room_id = secrets.token_hex(3)
        room = Room(room_id)
        self.rooms[room_id] = room
        return room

    def get(self, room_id: str) -> Optional[Room]:
        return self.rooms.get(room_id)

    def remove(self, room_id: str) -> None:
        room = self.rooms.pop(room_id, None)
        if room is not None:
            room.shutdown()

    def open_rooms(self) -> List[dict]:
        return [
            {
                "room_id": room.room_id,
                "creator": room.creator_name(),
                "available_color": room.available_color(),
                "created_at": room.created_at,
            }
            for room in self.rooms.values()
            if room.state == "waiting" and not room.is_full()
        ]
