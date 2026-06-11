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

def _xray_pieces(board: chess.Board, color: chess.Color, square: int) -> List[str]:
    """Sliders of `color` that bear on `square` THROUGH a friendly direct
    attacker on the same line (a battery: Q behind R, R behind R, Q behind B).
    They join the capture sequence back-to-front — full attackers for
    exchange counting, invisible to plain attackers() (game 093d86: an
    uncounted Qe2 behind Re3 hid a winning capture for two moves)."""
    findings = []
    direct = set(board.attackers(color, square))
    for sq in chess.SquareSet(board.occupied_co[color]):
        piece = board.piece_at(sq)
        if piece.piece_type not in (chess.BISHOP, chess.ROOK, chess.QUEEN) or sq in direct:
            continue
        # movement-type compatibility with the line to the target square
        same_line = (chess.square_file(sq) == chess.square_file(square)
                     or chess.square_rank(sq) == chess.square_rank(square))
        same_diag = abs(chess.square_file(sq) - chess.square_file(square)) == \
            abs(chess.square_rank(sq) - chess.square_rank(square))
        if piece.piece_type == chess.ROOK and not same_line:
            continue
        if piece.piece_type == chess.BISHOP and not same_diag:
            continue
        if piece.piece_type == chess.QUEEN and not (same_line or same_diag):
            continue
        blockers = [b for b in chess.SquareSet(chess.between(sq, square))
                    if board.piece_at(b) is not None]
        if len(blockers) == 1 and blockers[0] in direct:
            findings.append(
                f"{_piece_desc(board, sq)} — X-RAY through {_piece_desc(board, blockers[0])} "
                f"(battery: a full attacker for exchange counting, capture order front-to-back)"
            )
    return findings


def inspect_square(fen: str, square_name: str) -> str:
    board = _board(fen)
    try:
        square = chess.parse_square(square_name.lower())
    except ValueError:
        return f"'{square_name}' is not a square."
    piece = board.piece_at(square)
    occupant = _piece_desc(board, square) if piece else f"{square_name} is empty"
    lines = [f"Square {square_name}: {occupant}"]
    for color, label in ((chess.WHITE, "White"), (chess.BLACK, "Black")):
        direct = _attackers_desc(board, color, square)
        lines.append(f"{label} pieces attacking/defending it: {', '.join(direct) if direct else '(none)'}")
        for xray in _xray_pieces(board, color, square):
            lines.append(f"  + {xray}")
    return "\n".join(lines)


def hanging_report(fen: str) -> str:
    """The full attacked/undefended picture, both sides — automates the
    notebook's attacked/undefended bookkeeping in one call."""
    board = _board(fen)
    lines = []
    for color, label in ((chess.WHITE, "White"), (chess.BLACK, "Black")):
        attacked = []
        undefended = []
        for square in chess.SquareSet(board.occupied_co[color]):
            piece = board.piece_at(square)
            if piece.piece_type == chess.KING:
                continue
            attackers = board.attackers(not color, square)
            defenders = board.attackers(color, square)
            desc = _piece_desc(board, square)
            if attackers:
                attacker_descs = ", ".join(_piece_desc(board, a) for a in attackers)
                state = "NO defenders" if not defenders else (
                    f"{len(defenders)} defender(s)")
                attacked.append(
                    f"{desc} — attacked by {attacker_descs} ({len(attackers)}v{len(defenders)}, {state})"
                )
            elif not defenders:
                undefended.append(f"{desc} — zero defenders (not attacked yet, but targetable)")
        lines.append(f"=== {label} ===")
        lines.append("Attacked:")
        if attacked:
            lines.extend(f"  - {a}" for a in attacked)
        else:
            lines.append("  (none)")
        lines.append("Undefended (quiet but loose):")
        if undefended:
            lines.extend(f"  - {u}" for u in undefended)
        else:
            lines.append("  (none)")
    if board.is_check():
        turn = "White" if board.turn == chess.WHITE else "Black"
        lines.append(f"⚠ {turn} is IN CHECK.")
    return "\n".join(lines)


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


# ── Imagination board: a stateful virtual board for line exploration ──
# Humans calculate on the board in their head; this is that board.
# Geometry facts only — it never judges whether a line is GOOD.

class VirtualBoard:
    def __init__(self) -> None:
        self.start_fen: Optional[str] = None
        self.board: Optional[chess.Board] = None
        self.line: List[str] = []  # SAN moves pushed since start

    def start(self, fen: str) -> str:
        self.board = _board(fen)
        self.start_fen = fen
        self.line = []
        return f"Virtual board set.\n{self._position_report()}"

    def push(self, moves: List[str]) -> str:
        if self.board is None:
            return "No virtual board — call imagine_start(fen) first."
        applied = []
        for move in moves:
            parsed = _parse_move(self.board, move)
            if parsed is None:
                prefix = f"Applied: {' '.join(applied)}\n" if applied else ""
                return (
                    f"{prefix}'{move}' is ILLEGAL in this imagined position — the line "
                    f"breaks here. (Line so far: {self._line_str()})\n"
                    f"{self._position_report()}"
                )
            san = self.board.san(parsed)
            self.board.push(parsed)
            self.line.append(san)
            applied.append(san)
        return f"Imagined: {' '.join(applied)}\n{self._position_report()}"

    def undo(self, count: int = 1) -> str:
        if self.board is None:
            return "No virtual board — call imagine_start(fen) first."
        taken = 0
        while taken < count and self.line:
            self.board.pop()
            self.line.pop()
            taken += 1
        return f"Took back {taken} move(s).\n{self._position_report()}"

    def show(self) -> str:
        if self.board is None:
            return "No virtual board — call imagine_start(fen) first."
        return self._position_report()

    def _line_str(self) -> str:
        return " ".join(self.line) if self.line else "(at start position)"

    def _position_report(self) -> str:
        board = self.board
        lines = [f"Imagined line: {self._line_str()}"]
        rows = str(board).split("\n")
        for i, row in enumerate(rows):
            lines.append(f"  {8 - i} {row}")
        lines.append("    a b c d e f g h")
        lines.append(f"FEN: {board.fen()}")
        # ABSOLUTE material count — incremental ledgers across overlapping
        # trades double-count recaptures (cost a knight in game 093d86);
        # the final position's total is the only trustworthy number.
        diff = 0
        for piece_type, value in PIECE_VALUES.items():
            if piece_type == chess.KING:
                continue
            diff += value * (len(board.pieces(piece_type, chess.WHITE))
                             - len(board.pieces(piece_type, chess.BLACK)))
        verdict = "even" if diff == 0 else (f"White +{diff}" if diff > 0 else f"Black +{-diff}")
        lines.append(f"Material HERE (absolute): {verdict}")
        turn = "White" if board.turn == chess.WHITE else "Black"
        check = " — IN CHECK" if board.is_check() else ""
        if board.is_checkmate():
            lines.append(f"CHECKMATE — {turn} is mated here.")
            return "\n".join(lines)
        if board.is_stalemate():
            lines.append("STALEMATE — this line ends in a draw.")
            return "\n".join(lines)
        lines.append(f"{turn} to move{check}.")
        for color, label in ((chess.WHITE, "White"), (chess.BLACK, "Black")):
            findings = _loose_pieces(board, color)
            if findings:
                lines.append(f"{label} pieces in danger here:")
                lines.extend(f"  - {f}" for f in findings)
        captures = [board.san(m) for m in board.legal_moves if board.is_capture(m)]
        checks = [board.san(m) for m in board.legal_moves if board.gives_check(m)]
        lines.append(f"{turn}'s captures here: {', '.join(captures) if captures else '(none)'}")
        lines.append(f"{turn}'s checks here: {', '.join(checks) if checks else '(none)'}")
        return "\n".join(lines)


VIRTUAL = VirtualBoard()


def pinned_pieces(fen: str) -> str:
    """King pins ONLY (absolute pins) — the rule-level fact that the piece
    cannot legally leave the king's line. Relative pins are deliberately NOT
    reported: they're tactical suggestions, not facts (zwischenzugs and
    counter-tactics routinely break them), and the agent must judge those."""
    board = _board(fen)
    lines = []
    for color, label in ((chess.WHITE, "White"), (chess.BLACK, "Black")):
        pins = []
        for square in chess.SquareSet(board.occupied_co[color]):
            if board.is_pinned(color, square):
                pins.append(f"{_piece_desc(board, square)} (cannot leave the king's line)")
        lines.append(f"{label} pinned pieces: {'; '.join(pins) if pins else '(none)'}")
    return "\n".join(lines)
