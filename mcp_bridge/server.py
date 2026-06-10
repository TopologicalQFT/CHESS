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


PIECE_VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}


def material_line(board: chess.Board) -> str:
    """One-line material balance from the agent's perspective."""
    diff = 0
    for piece_type, value in PIECE_VALUES.items():
        diff += value * (len(board.pieces(piece_type, chess.WHITE))
                         - len(board.pieces(piece_type, chess.BLACK)))
    mine = diff if client.my_color == "w" else -diff
    if mine == 0:
        return "Material: even"
    side = "up" if mine > 0 else "down"
    return f"Material: you are {side} {abs(mine)} (P=1 N=B=3 R=5 Q=9)"


def short_history(pgn: str, plies: int = 8) -> str:
    """Last few plies of the movetext (full PGN stays available via get_board)."""
    tokens = pgn.split()
    # ~1.5 tokens per ply (move numbers every 2 plies)
    keep = plies + (plies // 2) + 1
    if len(tokens) <= keep:
        return pgn
    return "… " + " ".join(tokens[-keep:])


def board_report(full: bool = False) -> str:
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
    ]
    # The opponent's last move, impossible to miss (their move = it's our turn now)
    if yours and client.last_san:
        notes = []
        if "x" in client.last_san:
            notes.append("a CAPTURE")
        if client.last_san.endswith("+"):
            notes.append("CHECK on you")
        suffix = f" — {', '.join(notes)}!" if notes else ""
        lines.append(f"Opponent played: {client.last_san}{suffix}")
    lines.append("")

    # ASCII board, ranks 8→1
    rows = str(board).split("\n")
    for i, row in enumerate(rows):
        lines.append(f"  {8 - i} {row}")
    lines.append("    a b c d e f g h")
    lines.append("")
    lines.append(f"FEN: {board.fen()}")
    lines.append(material_line(board))
    if client.clock:
        mine = client.clock.get(client.my_color, 0)
        theirs = client.clock.get("b" if client.my_color == "w" else "w", 0)
        def fmt(s: float) -> str:
            s = max(0, int(s))
            return f"{s // 60}:{s % 60:02d}"
        lines.append(f"Clock: you {fmt(mine)} — opponent {fmt(theirs)}. Flag = loss; budget accordingly.")
    history = client.pgn or "(no moves yet)"
    if not full:
        history = short_history(client.pgn) or "(no moves yet)"
    lines.append(f"History{'' if full else ' (recent)'}: {history}")
    lines.append(f"Check: {'YES — your king is attacked!' if client.is_check and yours else ('yes' if client.is_check else 'no')}")
    if yours:
        sans = [board.san(m) for m in board.legal_moves]
        captures = [s for s in sans if "x" in s]
        checks = [s for s in sans if s.endswith("+") or s.endswith("#")]
        quiet = [s for s in sans if s not in captures and s not in checks]
        lines.append("Your legal moves (SAN):")
        if captures:
            lines.append(f"  Captures: {', '.join(captures)}")
        if checks:
            lines.append(f"  Checks: {', '.join(checks)}")
        lines.append(f"  Quiet: {', '.join(quiet) if quiet else '(none)'}")
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
async def create_room(player_name: str, color: str = "random", time_minutes: int = 0) -> str:
    """Create a chess room and wait for an opponent to join.

    Args:
        player_name: Your display name.
        color: 'w', 'b', or 'random'.
        time_minutes: Clock per player in minutes (5 or 10 typical); 0 = no clock.
    """
    if client.phase in ("waiting", "playing"):
        return f"Already in a room ({client.room_id}, state: {client.phase})."
    await client.create_room(player_name, color, time_control=time_minutes * 60 or None)
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
    """Show the current position with FULL move history. For recovery — the report
    from wait_for_my_turn is authoritative; you don't need this after every wait."""
    return board_report(full=True)


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
    # Compact echo of the resulting position — catches a misimagined board
    # one move sooner (rules-state only; agents verify details themselves).
    return (
        f"You played {san}.\n"
        f"Position now (opponent to move): {client.fen}\n"
        f"{material_line(client.board())}\n"
        f"Call wait_for_my_turn."
    )


def chat_section() -> str:
    """Unseen chat from opponent/spectators, appended to turn reports."""
    inbox = client.drain_chat()
    if not inbox:
        return ""
    lines = ["", "Chat received:"]
    for msg in inbox:
        role = COLOR_NAMES.get(msg.get("role"), "spectator")
        lines.append(f"  [{msg.get('sender', '?')} ({role})]: {msg.get('text', '')}")
    return "\n".join(lines)


@mcp.tool()
async def wait_for_my_turn(timeout_seconds: float = 55) -> str:
    """Wait until it's your turn (or the game ends). Call again if it times out.

    Args:
        timeout_seconds: Max seconds to block (keep under 60 for MCP limits).
    """
    state = await client.wait_for_my_turn(timeout_seconds)
    if state in ("your_turn", "game_over"):
        return board_report() + chat_section()
    if state == "waiting_for_opponent":
        return "Still waiting for an opponent to join. Call wait_for_my_turn again." + chat_section()
    return "Opponent is still thinking. Call wait_for_my_turn again." + chat_section()


@mcp.tool()
async def send_chat(message: str) -> str:
    """Send a chat message to the room (opponent + spectators see it on the website).
    Use it to briefly explain each move you play — one or two sentences.

    Args:
        message: The chat text (max 500 chars).
    """
    if client.phase not in ("waiting", "playing", "finished"):
        return "Not in a room — nothing to chat to."
    await client.send_chat(message[:500])
    return "Sent."


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
