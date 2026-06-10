"""Agent Toolkit: deterministic board-geometry helpers.

Stateless — every function takes a FEN. Board facts only, never judgment:
no evaluation, no move recommendations, no engine. See
docs/Overall Plan/Prompt Engineering/Agent Toolkit.md for the principle.
"""
from typing import List, Optional

import chess

PIECE_NAMES = {
    chess.PAWN: "pawn", chess.KNIGHT: "knight", chess.BISHOP: "bishop",
    chess.ROOK: "rook", chess.QUEEN: "queen", chess.KING: "king",
}
PIECE_VALUES = {
    chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
    chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 99,
}


def _board(fen: str) -> chess.Board:
    try:
        return chess.Board(fen)
    except ValueError as e:
        raise ValueError(f"Invalid FEN: {e}")


def _piece_desc(board: chess.Board, square: int) -> str:
    piece = board.piece_at(square)
    color = "White" if piece.color == chess.WHITE else "Black"
    return f"{color} {PIECE_NAMES[piece.piece_type]} on {chess.square_name(square)}"


def _attackers_desc(board: chess.Board, color: chess.Color, square: int) -> List[str]:
    return [_piece_desc(board, sq) for sq in board.attackers(color, square)]


def _parse_move(board: chess.Board, move: str) -> Optional[chess.Move]:
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


def _loose_pieces(board: chess.Board, color: chess.Color) -> List[str]:
    """Pieces of `color` that are attacked & undefended, or attacked by cheaper."""
    findings = []
    for square in chess.SquareSet(board.occupied_co[color]):
        piece = board.piece_at(square)
        if piece.piece_type == chess.KING:
            continue
        attackers = board.attackers(not color, square)
        if not attackers:
            continue
        defenders = board.attackers(color, square)
        attacker_descs = [_piece_desc(board, a) for a in attackers]
        if not defenders:
            findings.append(
                f"{_piece_desc(board, square)} — attacked by {', '.join(attacker_descs)}, NO defenders"
            )
        else:
            cheapest = min(PIECE_VALUES[board.piece_at(a).piece_type] for a in attackers)
            if cheapest < PIECE_VALUES[piece.piece_type]:
                findings.append(
                    f"{_piece_desc(board, square)} — attacked by cheaper piece "
                    f"({', '.join(attacker_descs)}); defenders exist but the trade loses material"
                )
    return findings


# ── Tool implementations (plain functions, MCP wraps them) ──────────

def preview_move(fen: str, move: str) -> str:
    board = _board(fen)
    parsed = _parse_move(board, move)
    if parsed is None:
        return f"'{move}' is not legal in this position."
    san = board.san(parsed)
    mover_color = board.turn
    board.push(parsed)

    lines = [f"After {san}:"]
    rows = str(board).split("\n")
    for i, row in enumerate(rows):
        lines.append(f"  {8 - i} {row}")
    lines.append("    a b c d e f g h")
    lines.append(f"FEN: {board.fen()}")

    loose = _loose_pieces(board, mover_color)
    if loose:
        lines.append("YOUR pieces now in danger:")
        for finding in loose:
            lines.append(f"  - {finding}")
    else:
        lines.append("None of your pieces are hanging after this move.")

    checks = []
    captures = []
    for reply in board.legal_moves:
        reply_san = board.san(reply)
        if board.gives_check(reply):
            checks.append(reply_san)
        if board.is_capture(reply):
            captures.append(reply_san)
    lines.append(f"Opponent's checks in reply: {', '.join(checks) if checks else '(none)'}")
    lines.append(f"Opponent's captures in reply: {', '.join(captures) if captures else '(none)'}")
    if board.is_checkmate():
        lines.append("This move delivers CHECKMATE.")
    elif board.is_stalemate():
        lines.append("⚠ This move delivers STALEMATE — the game is drawn!")
    return "\n".join(lines)


def inspect_square(fen: str, square_name: str) -> str:
    board = _board(fen)
    try:
        square = chess.parse_square(square_name.lower())
    except ValueError:
        return f"'{square_name}' is not a square."
    piece = board.piece_at(square)
    occupant = _piece_desc(board, square) if piece else f"{square_name} is empty"
    white_attackers = _attackers_desc(board, chess.WHITE, square)
    black_attackers = _attackers_desc(board, chess.BLACK, square)
    return "\n".join([
        f"Square {square_name}: {occupant}",
        f"White pieces attacking/defending it: {', '.join(white_attackers) if white_attackers else '(none)'}",
        f"Black pieces attacking/defending it: {', '.join(black_attackers) if black_attackers else '(none)'}",
    ])


def list_loose_pieces(fen: str) -> str:
    board = _board(fen)
    lines = []
    for color, label in ((chess.WHITE, "White"), (chess.BLACK, "Black")):
        findings = _loose_pieces(board, color)
        lines.append(f"{label} loose pieces:")
        if findings:
            lines.extend(f"  - {f}" for f in findings)
        else:
            lines.append("  (none)")
    return "\n".join(lines)


def opponent_replies(fen: str) -> str:
    board = _board(fen)
    if board.is_check():
        return "You are IN CHECK — you must address the check; a 'pass' is impossible."
    board.push(chess.Move.null())  # pretend you passed
    checks = []
    captures = []
    for reply in board.legal_moves:
        san = board.san(reply)
        if board.gives_check(reply):
            checks.append(san)
        if board.is_capture(reply):
            captures.append(san)
    return "\n".join([
        "If you did NOTHING this move, the opponent could play:",
        f"Checks: {', '.join(checks) if checks else '(none)'}",
        f"Captures: {', '.join(captures) if captures else '(none)'}",
        "(Any capture of an undefended piece here is a live threat you must address.)",
    ])


def pinned_pieces(fen: str) -> str:
    board = _board(fen)
    lines = []
    for color, label in ((chess.WHITE, "White"), (chess.BLACK, "Black")):
        pins = []
        for square in chess.SquareSet(board.occupied_co[color]):
            if board.is_pinned(color, square):
                pins.append(f"{_piece_desc(board, square)} (cannot leave the king's line)")
        lines.append(f"{label} pinned pieces: {'; '.join(pins) if pins else '(none)'}")
    return "\n".join(lines)
