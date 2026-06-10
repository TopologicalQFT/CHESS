"""chess-toolkit MCP: the agent's own analysis equipment.

Stateless board-geometry tools (FEN in, facts out). Part of the AGENT,
not the table — see docs/Overall Plan/Prompt Engineering/Agent Toolkit.md.

Run (stdio): python server.py
"""
from mcp.server.fastmcp import FastMCP

import toolkit

mcp = FastMCP("chess-toolkit")


@mcp.tool()
async def preview_move(fen: str, move: str) -> str:
    """Dry-run a candidate move: resulting position, which of YOUR pieces end up
    attacked-and-undefended, and the opponent's checks/captures in reply.
    Use before committing any capture, pawn push, or 'trade'.

    Args:
        fen: The current position (from the board report).
        move: Candidate move in SAN ('Nf3') or UCI ('g1f3').
    """
    return toolkit.preview_move(fen, move)


@mcp.tool()
async def inspect_square(fen: str, square: str) -> str:
    """Who attacks and defends a square, by piece. The answer to 'is that
    capture target actually defended?' and 'can I safely land here?'.

    Args:
        fen: The current position.
        square: Square name, e.g. 'b5'.
    """
    return toolkit.inspect_square(fen, square)


@mcp.tool()
async def hanging_report(fen: str) -> str:
    """The complete attacked/undefended picture, both sides, in one call:
    every attacked piece with attacker-vs-defender counts, every undefended
    piece (even if not attacked yet — those are future targets), and check
    status. Call once per move in Step 1 — it replaces manual
    attacked/undefended bookkeeping.

    Args:
        fen: The current position (from the board report).
    """
    return toolkit.hanging_report(fen)


@mcp.tool()
async def list_loose_pieces(fen: str) -> str:
    """Both sides' hanging pieces: attacked with no defenders, or attacked by
    something cheaper. Your list = urgent problems; theirs = candidate targets.

    Args:
        fen: The current position.
    """
    return toolkit.list_loose_pieces(fen)


@mcp.tool()
async def opponent_replies(fen: str) -> str:
    """Every check and capture the opponent could play if you passed.
    The concrete answer to 'what is their threat?'.

    Args:
        fen: The current position (your turn).
    """
    return toolkit.opponent_replies(fen)


@mcp.tool()
async def imagine_start(fen: str) -> str:
    """Set up your imagination board — the board in your head, as a tool.
    Start it from the CURRENT game position (the FEN in the board report)
    at the beginning of each calculation. Then explore with imagine_move /
    imagine_undo. It never touches the real game.

    Args:
        fen: Position to imagine from (use the current report's FEN).
    """
    return toolkit.VIRTUAL.start(fen)


@mcp.tool()
async def imagine_move(moves: list[str]) -> str:
    """Play one or more moves on the imagination board (both sides' moves,
    alternating). Each move is validated — an illegal move stops the line
    right there, which is exactly how broken combinations get caught.
    Returns the resulting position with danger facts (hanging pieces,
    available captures/checks).

    Args:
        moves: Moves in SAN or UCI, in order, e.g. ["exd4", "Bxd1", "Nxf6+"].
    """
    return toolkit.VIRTUAL.push(moves)


@mcp.tool()
async def imagine_undo(count: int = 1) -> str:
    """Take back moves on the imagination board to try a different branch.

    Args:
        count: How many plies to take back (default 1).
    """
    return toolkit.VIRTUAL.undo(count)


@mcp.tool()
async def imagine_show() -> str:
    """Show the imagination board's current position and the line that led here."""
    return toolkit.VIRTUAL.show()


@mcp.tool()
async def pinned_pieces(fen: str) -> str:
    """KING pins only (absolute pins) — pieces that cannot legally leave the
    king's line, for both colors. A king-pinned piece may not really defend
    what you think it defends. (Relative pins — against queens/rooks — are
    NOT reported: those are tactical judgments, yours to make.)

    Args:
        fen: The current position.
    """
    return toolkit.pinned_pieces(fen)


if __name__ == "__main__":
    mcp.run()
