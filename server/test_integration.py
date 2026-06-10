"""Integration tests against a real uvicorn server with real WebSocket clients.

(Starlette's TestClient runs each WebSocket on its own event loop, which
deadlocks cross-socket broadcasts — so we test the real thing instead.)

Run: .venv/Scripts/python -m pytest test_integration.py -q
"""
import asyncio
import json
import threading
import time

import pytest
import uvicorn
from websockets.asyncio.client import connect

import main

PORT = 8765
URL = f"ws://127.0.0.1:{PORT}/ws"


@pytest.fixture(scope="module")
def server():
    config = uvicorn.Config(main.app, host="127.0.0.1", port=PORT, log_level="error")
    srv = uvicorn.Server(config)
    thread = threading.Thread(target=srv.run, daemon=True)
    thread.start()
    deadline = time.time() + 10
    while not srv.started:
        if time.time() > deadline:
            raise RuntimeError("server failed to start")
        time.sleep(0.05)
    yield srv
    srv.should_exit = True
    thread.join(timeout=5)


@pytest.fixture(autouse=True)
def fresh_state():
    main.manager.rooms.clear()
    main.lobby_sockets.clear()


async def send(ws, payload: dict):
    await ws.send(json.dumps(payload))


async def recv_until(ws, msg_type: str, limit: int = 20) -> dict:
    for _ in range(limit):
        msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        if msg["type"] == msg_type:
            return msg
    raise AssertionError(f"never received {msg_type}")


async def start_game(alice, bob, alice_color="w"):
    """Create a room as alice, join as bob; both consume game_started."""
    await recv_until(alice, "room_list")
    await recv_until(bob, "room_list")
    await send(alice, {"type": "create_room", "player_name": "Alice", "color": alice_color})
    created = await recv_until(alice, "room_created")
    await send(bob, {"type": "join_room", "room_id": created["room_id"], "player_name": "Bob"})
    start_a = await recv_until(alice, "game_started")
    start_b = await recv_until(bob, "game_started")
    return created["room_id"], start_a, start_b


def test_full_game_flow(server):
    async def scenario():
        async with connect(URL) as alice, connect(URL) as bob:
            _, start_a, start_b = await start_game(alice, bob)
            assert start_a["your_color"] == "w"
            assert start_b["your_color"] == "b"
            assert start_a["white_name"] == "Alice"

            # Bob tries to move out of turn → error
            await send(bob, {"type": "move", "from": "e7", "to": "e5"})
            err = await recv_until(bob, "error")
            assert err["message"] == "Not your turn"

            # Alice plays e4 → both get board updates
            await send(alice, {"type": "move", "from": "e2", "to": "e4"})
            up_a = await recv_until(alice, "board_update")
            up_b = await recv_until(bob, "board_update")
            assert up_a["move_san"] == "e4"
            assert up_b["turn"] == "b"
            assert up_b["last_move"] == {"from": "e2", "to": "e4"}

            # Scholar's mate
            moves = [
                (bob, "e7", "e5"), (alice, "d1", "h5"), (bob, "b8", "c6"),
                (alice, "f1", "c4"), (bob, "g8", "f6"), (alice, "h5", "f7"),
            ]
            for sock, frm, to in moves:
                await send(sock, {"type": "move", "from": frm, "to": to})
                await recv_until(alice, "board_update")
                await recv_until(bob, "board_update")

            over_a = await recv_until(alice, "game_over")
            over_b = await recv_until(bob, "game_over")
            assert over_a["result"] == "checkmate"
            assert over_a["winner"] == "w"
            assert "Qxf7#" in over_b["pgn"]

    asyncio.run(scenario())


def test_surrender_and_rematch(server):
    async def scenario():
        async with connect(URL) as alice, connect(URL) as bob:
            await start_game(alice, bob)

            # Alice surrenders → Bob wins
            await send(alice, {"type": "surrender"})
            over = await recv_until(bob, "game_over")
            assert over["result"] == "resignation"
            assert over["winner"] == "b"

            # Both vote rematch → colors swap, new game starts
            await send(alice, {"type": "rematch"})
            await recv_until(bob, "rematch_offered")
            await send(bob, {"type": "rematch"})
            start_a = await recv_until(alice, "game_started")
            start_b = await recv_until(bob, "game_started")
            assert start_a["your_color"] == "b"  # swapped
            assert start_b["your_color"] == "w"

            # Post-rematch the seats are swapped: Bob moves first now,
            # and his surrender must award the win to Alice.
            await send(bob, {"type": "move", "from": "e2", "to": "e4"})
            up = await recv_until(alice, "board_update")
            assert up["move_san"] == "e4"
            await send(bob, {"type": "surrender"})
            over = await recv_until(alice, "game_over")
            assert over["result"] == "resignation"
            assert over["winner"] == "b"  # Alice holds black after the swap

    asyncio.run(scenario())


def test_illegal_move_rejected(server):
    async def scenario():
        async with connect(URL) as alice, connect(URL) as bob:
            await start_game(alice, bob)

            await send(alice, {"type": "move", "from": "e2", "to": "e5"})  # illegal
            err = await recv_until(alice, "error")
            assert err["message"] == "Illegal move"

            await send(alice, {"type": "move", "from": "e2", "to": "e4"})  # legal
            up = await recv_until(alice, "board_update")
            assert up["move_san"] == "e4"

    asyncio.run(scenario())


def test_spectator_flow(server):
    async def scenario():
        async with connect(URL) as alice, connect(URL) as bob, connect(URL) as carol:
            room_id, _, _ = await start_game(alice, bob)

            # Carol (in lobby) gets room_list pushes as the room is created,
            # joined, and started — wait for the one showing it as playing
            playing = None
            for _ in range(10):
                rooms = (await recv_until(carol, "room_list"))["rooms"]
                match = [r for r in rooms if r["room_id"] == room_id]
                if match and match[0]["state"] == "playing":
                    playing = match[0]
                    break
            assert playing is not None, "never saw the room as playing"
            assert playing["white_name"] == "Alice"

            # Carol spectates: snapshot, then live updates
            await send(carol, {"type": "spectate", "room_id": room_id})
            snap = await recv_until(carol, "spectate_joined")
            assert snap["white_name"] == "Alice" and snap["black_name"] == "Bob"
            assert snap["fen"].startswith("rnbqkbnr")

            await send(alice, {"type": "move", "from": "e2", "to": "e4"})
            up = await recv_until(carol, "board_update")
            assert up["move_san"] == "e4"

            # Spectator cannot act
            await send(carol, {"type": "move", "from": "e7", "to": "e5"})
            err = await recv_until(carol, "error")
            assert err["message"] == "No active game"
            await send(carol, {"type": "surrender"})  # silently ignored (no seat)

            # Game over reaches the spectator; rematch restarts her view
            await send(bob, {"type": "surrender"})
            over = await recv_until(carol, "game_over")
            assert over["result"] == "resignation"
            await send(alice, {"type": "rematch"})
            await send(bob, {"type": "rematch"})
            restart = await recv_until(carol, "game_started")
            assert restart["your_color"] is None  # spectator stays colorless

            # Leave back to lobby
            await send(carol, {"type": "leave_room"})
            rooms = (await recv_until(carol, "room_list"))["rooms"]
            assert isinstance(rooms, list)

    asyncio.run(scenario())


def test_room_listing_and_full_room(server):
    async def scenario():
        async with connect(URL) as alice, connect(URL) as bob, connect(URL) as carol:
            room_id, _, _ = await start_game(alice, bob)

            # Carol arrived before the game started; her initial list may
            # contain the room, but joining a full room must fail.
            await recv_until(carol, "room_list")
            await send(carol, {"type": "join_room", "room_id": room_id, "player_name": "Carol"})
            err = await recv_until(carol, "error")
            assert err["message"] in ("Room is full", "Room not found")

    asyncio.run(scenario())
