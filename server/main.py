"""FastAPI app: WebSocket endpoint, message routing, static file serving.

Run (dev):  .venv/Scripts/uvicorn main:app --reload --port 8000
"""
import secrets
from pathlib import Path
from typing import Optional, Set

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError

import analysis

from models import CreateRoomMsg, JoinRoomMsg, MoveMsg, ReconnectMsg
from player import HumanPlayer
from room_manager import Room, RoomManager

app = FastAPI(title="Chess Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = RoomManager()
lobby_sockets: Set[WebSocket] = set()


@app.get("/health")
async def health():
    return {"status": "ok", "rooms": len(manager.rooms)}


class AnalyzeRequest(BaseModel):
    pgn: str


@app.post("/analyze")
def analyze_game(req: AnalyzeRequest):
    """Stockfish post-game analysis. Sync endpoint → FastAPI's threadpool,
    so the engine never blocks live games on the event loop."""
    try:
        return analysis.analyze_pgn(req.pgn)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def push_room_list() -> None:
    """Notify everyone in the lobby that the room list changed."""
    payload = {"type": "room_list", "rooms": manager.open_rooms()}
    for ws in list(lobby_sockets):
        try:
            await ws.send_json(payload)
        except Exception:
            lobby_sockets.discard(ws)


manager.on_rooms_changed = push_room_list  # lobby sees games start/end live


class Session:
    """Per-connection state.

    The color is NOT cached here: rematches swap seat colors, so it is
    always derived from which seat the socket currently occupies.
    """

    def __init__(self, ws: WebSocket) -> None:
        self.ws = ws
        self.room: Optional[Room] = None
        self.spectator_name = "Spectator"

    @property
    def color(self) -> Optional[str]:
        if self.room is None:
            return None
        return self.room.color_of(self.ws)

    @property
    def player(self) -> Optional[HumanPlayer]:
        color = self.color
        if self.room is None or color is None:
            return None
        return self.room.players[color]


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    lobby_sockets.add(ws)
    session = Session(ws)
    try:
        await ws.send_json({"type": "room_list", "rooms": manager.open_rooms()})
        while True:
            data = await ws.receive_json()
            await handle_message(ws, session, data)
    except WebSocketDisconnect:
        await handle_disconnect(ws, session)
    except Exception:
        await handle_disconnect(ws, session)


async def handle_message(ws: WebSocket, session: Session, data: dict) -> None:
    msg_type = data.get("type")

    if msg_type == "get_rooms":
        await ws.send_json({"type": "room_list", "rooms": manager.open_rooms()})

    elif msg_type == "create_room":
        await on_create_room(ws, session, data)

    elif msg_type == "join_room":
        await on_join_room(ws, session, data)

    elif msg_type == "move":
        await on_move(ws, session, data)

    elif msg_type == "surrender":
        if session.room is not None and session.color is not None:
            await session.room.surrender(session.color)

    elif msg_type == "rematch":
        if session.room is not None and session.color is not None:
            await session.room.vote_rematch(session.color)

    elif msg_type == "leave_room":
        await on_leave_room(ws, session)

    elif msg_type == "chat":
        await on_chat(ws, session, data)

    elif msg_type == "spectate":
        await on_spectate(ws, session, data)

    elif msg_type == "reconnect":
        await on_reconnect(ws, session, data)

    else:
        await ws.send_json({"type": "error", "message": f"Unknown message type: {msg_type}"})


async def on_create_room(ws: WebSocket, session: Session, data: dict) -> None:
    if session.room is not None:
        await ws.send_json({"type": "error", "message": "Already in a room"})
        return
    try:
        msg = CreateRoomMsg(**data)
    except ValidationError as e:
        await ws.send_json({"type": "error", "message": f"Invalid message: {e.errors()[0]['msg']}"})
        return

    color = msg.color if msg.color in ("w", "b") else secrets.choice(["w", "b"])
    room = manager.create_room()
    room.players[color] = HumanPlayer(msg.player_name, color)
    room.sockets[color] = ws

    session.room = room
    lobby_sockets.discard(ws)

    await ws.send_json({"type": "room_created", "room_id": room.room_id, "color": color})
    await push_room_list()


async def on_join_room(ws: WebSocket, session: Session, data: dict) -> None:
    if session.room is not None:
        await ws.send_json({"type": "error", "message": "Already in a room"})
        return
    try:
        msg = JoinRoomMsg(**data)
    except ValidationError as e:
        await ws.send_json({"type": "error", "message": f"Invalid message: {e.errors()[0]['msg']}"})
        return

    room = manager.get(msg.room_id)
    if room is None:
        await ws.send_json({"type": "error", "message": "Room not found"})
        return
    color = room.available_color()
    if color is None or room.state != "waiting":
        await ws.send_json({"type": "error", "message": "Room is full"})
        return

    room.players[color] = HumanPlayer(msg.player_name, color)
    room.sockets[color] = ws
    session.room = room
    lobby_sockets.discard(ws)

    await room.send_to(room.opponent(color), {"type": "room_joined", "opponent_name": msg.player_name})
    await push_room_list()
    await room.start_game()


async def on_move(ws: WebSocket, session: Session, data: dict) -> None:
    room, player = session.room, session.player
    if room is None or player is None or room.state != "playing":
        await ws.send_json({"type": "error", "message": "No active game"})
        return
    try:
        msg = MoveMsg(**data)
    except ValidationError:
        await ws.send_json({"type": "error", "message": "Invalid move format"})
        return
    if room.engine.turn() != session.color:
        await ws.send_json({"type": "error", "message": "Not your turn"})
        return
    if not player.submit_move(msg.uci()):
        await ws.send_json({"type": "error", "message": "No move expected"})


async def on_chat(ws: WebSocket, session: Session, data: dict) -> None:
    room = session.room
    text = str(data.get("text", "")).strip()[:500]
    if room is None or not text:
        return
    color = session.color
    if color is not None:
        player = room.players[color]
        sender, role = (player.name if player else "?"), color
    else:
        sender, role = session.spectator_name, "spectator"
    await room.post_chat(sender, role, text)


async def on_spectate(ws: WebSocket, session: Session, data: dict) -> None:
    if session.room is not None:
        await ws.send_json({"type": "error", "message": "Already in a room"})
        return
    session.spectator_name = str(data.get("player_name", "")).strip()[:30] or "Spectator"
    room = manager.get(str(data.get("room_id", "")))
    if room is None:
        await ws.send_json({"type": "error", "message": "Room not found"})
        return
    if room.state not in ("playing", "finished"):
        await ws.send_json({"type": "error", "message": "Nothing to watch yet"})
        return

    room.spectators.add(ws)
    session.room = room
    lobby_sockets.discard(ws)

    snapshot = {
        "type": "spectate_joined",
        "room_id": room.room_id,
        "room_state": room.state,
        "white_name": room.players["w"].name if room.players["w"] else "?",
        "black_name": room.players["b"].name if room.players["b"] else "?",
        "chat": room.chat,
    }
    if room.engine is not None:
        snapshot.update(room.engine.board_update())
    await ws.send_json(snapshot)


async def on_leave_room(ws: WebSocket, session: Session) -> None:
    room, color = session.room, session.color
    if room is not None and color is None:
        # Spectator leaving
        room.spectators.discard(ws)
        session.room = None
        lobby_sockets.add(ws)
        await ws.send_json({"type": "room_list", "rooms": manager.open_rooms()})
        return
    if room is None or color is None:
        return
    opponent_color = room.opponent(color)

    if room.state == "playing":
        # Leaving mid-game counts as resignation
        await room.surrender(color)

    room.players[color] = None
    room.sockets[color] = None
    session.room = None
    lobby_sockets.add(ws)

    if room.players[opponent_color] is None:
        manager.remove(room.room_id)
    else:
        await room.send_to(opponent_color, {"type": "opponent_left"})
        if room.state == "finished":
            # Opponent stays; room returns to waiting for a new challenger
            room.state = "waiting"
            await push_room_list()
    await push_room_list()
    await ws.send_json({"type": "room_list", "rooms": manager.open_rooms()})


async def on_reconnect(ws: WebSocket, session: Session, data: dict) -> None:
    try:
        msg = ReconnectMsg(**data)
    except ValidationError:
        await ws.send_json({"type": "error", "message": "Invalid reconnect message"})
        return
    room = manager.get(msg.room_id)
    if room is None or room.players[msg.color] is None:
        await ws.send_json({"type": "reconnect_failed"})
        return
    if room.sockets[msg.color] is not None:
        await ws.send_json({"type": "error", "message": "Seat is still connected"})
        return

    room.sockets[msg.color] = ws
    room.players[msg.color].connected = True
    session.room = room
    lobby_sockets.discard(ws)

    state = {
        "type": "game_restored",
        "room_state": room.state,
        "your_color": msg.color,
        "white_name": room.players["w"].name if room.players["w"] else "?",
        "black_name": room.players["b"].name if room.players["b"] else "?",
    }
    if room.engine is not None:
        state.update(room.engine.board_update())
    await ws.send_json(state)
    await room.send_to(room.opponent(msg.color), {"type": "opponent_reconnected"})


async def handle_disconnect(ws: WebSocket, session: Session) -> None:
    lobby_sockets.discard(ws)
    room, color = session.room, session.color
    if room is not None and color is None:
        room.spectators.discard(ws)  # spectator dropped
        return
    if room is None or color is None:
        return
    room.sockets[color] = None
    player = room.players[color]
    if player is not None:
        player.connected = False

    if room.state == "waiting":
        # Creator left before anyone joined → drop the room
        room.players[color] = None
        if not room.is_full() and room.available_color() is not None:
            other = room.opponent(color)
            if room.players[other] is None:
                manager.remove(room.room_id)
        await push_room_list()
    elif room.sockets[room.opponent(color)] is None:
        # Both players gone → the game can never continue; close the room
        # so it doesn't haunt the lobby as a zombie "live" game.
        await room.broadcast({"type": "room_closed"})  # reaches spectators
        manager.remove(room.room_id)
        await push_room_list()
    else:
        await room.send_to(room.opponent(color), {"type": "opponent_disconnected"})


# ── Static files (production: serve the built React app) ─────
client_dist = Path(__file__).resolve().parent.parent / "client" / "dist"
if client_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(client_dist), html=True), name="client")
