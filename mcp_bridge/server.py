"""MCP server exposing the chess bridge as agent tools.

Run (stdio): python server.py
Target server: CHESS_SERVER_URL env (default ws://localhost:8000/ws)
"""
import chess
from mcp.server.fastmcp import FastMCP

from bridge import ChessClient

mcp = FastMCP("chess")
client = ChessClient()

COLOR_NAMES = {"w": "White", "b": "Black"}


def board_report() -> str:
    """The agent's view of the position. Phase 3 will experiment here."""
    if client.phase == "finished" and client.result:
        r = client.result
        winner = COLOR_NAMES.get(r["winner"], "nobody")
        me = "You won!" if r["winner"] == client.my_color else (
            "You lost." if r["winner"] else "Draw.")
        return (
            f"GAME OVER — {r['result']}"
            + (f" ({r['reason']})" if r.get("reason") else "")
            + f". Winner: {winner}. {me}\nFinal game: {r['pgn']}"
        )
    if client.phase != "playing":
        return f"No game in progress (state: {client.phase})."

    board = client.board()
    my_color = COLOR_NAMES.get(client.my_color, "?")
    turn_color = COLOR_NAMES[client.turn]
    yours = client.turn == client.my_color

    lines = [
        f"You are playing {my_color}. "
        + (f"It is YOUR turn (move {board.fullmove_number})."
           if yours else f"It is {turn_color}'s turn — wait."),
        "",
    ]
    # ASCII board, ranks 8→1
    rows = str(board).split("\n")
    for i, row in enumerate(rows):
        lines.append(f"  {8 - i} {row}")
    lines.append("    a b c d e f g h")
    lines.append("")
    lines.append(f"FEN: {board.fen()}")
    lines.append(f"History: {client.pgn or '(no moves yet)'}")
    lines.append(f"Check: {'YES — your king is attacked!' if client.is_check and yours else ('yes' if client.is_check else 'no')}")
    if yours:
        sans = [board.san(m) for m in board.legal_moves]
        lines.append(f"Your legal moves (SAN): {', '.join(sans)}")
    return "\n".join(lines)


@mcp.tool()
async def list_rooms() -> str:
    """List open chess rooms waiting for an opponent."""
    rooms = await client.get_rooms()
    if not rooms:
        return "No open rooms. You can create one with create_room."
    lines = ["Open rooms:"]
    for r in rooms:
        color = COLOR_NAMES.get(r["available_color"], "?")
        lines.append(f"- room_id={r['room_id']}  creator={r['creator']}  you would play {color}")
    return "\n".join(lines)


@mcp.tool()
async def create_room(player_name: str, color: str = "random") -> str:
    """Create a chess room and wait for an opponent to join.

    Args:
        player_name: Your display name.
        color: 'w', 'b', or 'random'.
    """
    if client.phase in ("waiting", "playing"):
        return f"Already in a room ({client.room_id}, state: {client.phase})."
    await client.create_room(player_name, color)
    if client.last_error:
        return f"Error: {client.last_error}"
    return (
        f"Room created: {client.room_id}. You play {COLOR_NAMES[client.my_color]}. "
        f"A human can join from the website, or another agent via join_room. "
        f"Call wait_for_my_turn to wait for the game to start."
    )


@mcp.tool()
async def join_room(room_id: str, player_name: str) -> str:
    """Join an existing room by id. The game starts immediately.

    Args:
        room_id: The room code (from list_rooms or given by the host).
        player_name: Your display name.
    """
    if client.phase in ("waiting", "playing"):
        return f"Already in a room ({client.room_id}, state: {client.phase})."
    await client.join_room(room_id, player_name)
    if client.last_error:
        return f"Error: {client.last_error}"
    return f"Joined! Opponent: vs {client.white_name} (White) / {client.black_name} (Black).\n\n{board_report()}"


@mcp.tool()
async def get_board() -> str:
    """Show the current position: board diagram, FEN, history, legal moves."""
    return board_report()


@mcp.tool()
async def make_move(move: str) -> str:
    """Play a move. Accepts SAN ('Nf3', 'exd5', 'O-O', 'e8=Q') or UCI ('g1f3').

    Args:
        move: The move to play.
    """
    if client.phase != "playing":
        return board_report()
    if client.turn != client.my_color:
        return "Not your turn — call wait_for_my_turn."
    parsed = client.parse_move(move)
    if parsed is None:
        board = client.board()
        sans = [board.san(m) for m in board.legal_moves]
        return f"'{move}' is not legal here. Legal moves: {', '.join(sans)}"
    san = client.board().san(parsed)
    ok = await client.make_move(parsed)
    if not ok:
        return f"Server rejected {san}: {client.last_error}"
    if client.phase == "finished":
        return f"You played {san}.\n\n{board_report()}"
    return f"You played {san}. Now it's the opponent's turn — call wait_for_my_turn."


@mcp.tool()
async def wait_for_my_turn(timeout_seconds: float = 55) -> str:
    """Wait until it's your turn (or the game ends). Call again if it times out.

    Args:
        timeout_seconds: Max seconds to block (keep under 60 for MCP limits).
    """
    state = await client.wait_for_my_turn(timeout_seconds)
    if state in ("your_turn", "game_over"):
        return board_report()
    if state == "waiting_for_opponent":
        return "Still waiting for an opponent to join. Call wait_for_my_turn again."
    return "Opponent is still thinking. Call wait_for_my_turn again."


@mcp.tool()
async def surrender() -> str:
    """Resign the current game."""
    if client.phase != "playing":
        return f"No game to resign (state: {client.phase})."
    await client.surrender()
    return board_report()


@mcp.tool()
async def leave_room() -> str:
    """Leave the current room (back to the lobby). Counts as resignation if a game is in progress."""
    await client.leave_room()
    return "Left the room. You can list_rooms, create_room, or join_room."


@mcp.tool()
async def game_status() -> str:
    """Quick status: connection, room, whose turn, result."""
    return (
        f"state={client.phase} room={client.room_id} color={client.my_color} "
        f"turn={client.turn} server={client.url}\n"
        + (f"result={client.result}" if client.result else "")
    )


if __name__ == "__main__":
    mcp.run()
