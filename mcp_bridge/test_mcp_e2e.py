"""End-to-end test of the MCP layer: spawn server.py over stdio exactly like
Claude Code does, call the tools as an agent would, while a plain ChessClient
plays the opponent seat.

Run: .venv/Scripts/python test_mcp_e2e.py  (chess server must be on :8000)
"""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from bridge import ChessClient

PY = sys.executable


async def call(session: ClientSession, tool: str, args: dict = None) -> str:
    result = await session.call_tool(tool, args or {})
    text = result.content[0].text
    print(f"--- {tool}({args or ''}) ->")
    print(text[:400], "\n")
    return text


async def main():
    params = StdioServerParameters(
        command=PY, args=["server.py"], env={"PYTHONUTF8": "1"}
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = [t.name for t in (await session.list_tools()).tools]
            print("tools:", tools)
            assert set(tools) >= {
                "list_rooms", "create_room", "join_room", "get_board",
                "make_move", "wait_for_my_turn", "surrender", "game_status",
            }

            # Agent creates a room as white
            out = await call(session, "create_room",
                             {"player_name": "Agent", "color": "w"})
            room_id = out.split("Room created: ")[1].split(".")[0]

            # A plain bridge client takes the opponent seat
            human = ChessClient()
            await human.connect()
            await human.join_room(room_id, "Human")
            assert human.phase == "playing"

            # Agent waits → its turn; board report must show legal moves
            out = await call(session, "wait_for_my_turn", {"timeout_seconds": 10})
            assert "YOUR turn" in out and "e4" in out

            # Illegal move → friendly error, turn not burned
            out = await call(session, "make_move", {"move": "Ke3"})
            assert "not legal" in out

            # Legal move in SAN
            out = await call(session, "make_move", {"move": "e4"})
            assert "You played e4" in out

            # Opponent replies; agent waits and sees the new position
            await human.wait_for_my_turn(5)
            await human.make_move(human.parse_move("c7c5"))
            out = await call(session, "wait_for_my_turn", {"timeout_seconds": 10})
            assert "1. e4 c5" in out

            # Status + surrender path
            out = await call(session, "game_status")
            assert "state=playing" in out
            out = await call(session, "surrender")
            assert "GAME OVER" in out and "resignation" in out

            # ── Regression: bug_report/mcp-bridge-stale-websocket.md ──
            # A second game after a finished one must work (auto leave_room)
            out = await call(session, "create_room",
                             {"player_name": "Agent", "color": "w"})
            assert "Room created" in out, out
            room2 = out.split("Room created: ")[1].split(".")[0]
            human2 = ChessClient()
            await human2.connect()
            await human2.join_room(room2, "Human2")
            out = await call(session, "wait_for_my_turn", {"timeout_seconds": 10})
            assert "YOUR turn" in out
            out = await call(session, "make_move", {"move": "d4"})
            assert "You played d4" in out
            await call(session, "leave_room")

            await human.close()
            await human2.close()

    # ── Regression 2: dead socket must self-heal on next call ──
    # (bridge-level: same code path the MCP tools use)
    probe = ChessClient()
    await probe.connect()
    await probe.create_room("Probe", "w")
    assert probe.phase == "waiting"
    await probe.ws.close()           # simulate server restart / network drop
    await asyncio.sleep(0.2)         # let the listen task notice
    assert probe.phase == "disconnected"
    rooms = await probe.get_rooms()  # must reconnect, not raise
    assert probe.phase == "lobby"
    assert isinstance(rooms, list)
    assert probe.room_id is None     # stale seat forgotten
    await probe.close()

    print("MCP E2E TEST PASSED")


if __name__ == "__main__":
    asyncio.run(main())
