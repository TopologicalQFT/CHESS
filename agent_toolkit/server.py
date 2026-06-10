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
async def pinned_pieces(fen: str) -> str:
    """Absolutely pinned pieces for both colors. A pinned piece cannot leave
    the king's line — it may not really defend what you think it defends.

    Args:
        fen: The current position.
    """
    return toolkit.pinned_pieces(fen)


if __name__ == "__main__":
    mcp.run()
