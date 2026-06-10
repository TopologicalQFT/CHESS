"""Chess game logic wrapper around python-chess.

The single source of truth for board state. The frontend never
validates moves; it renders what this engine reports.
"""
from typing import Dict, List, Optional

import chess
import chess.pgn


class GameEngine:
    def __init__(self) -> None:
        self.board = chess.Board()

    # ── Moves ────────────────────────────────────────────────

    def make_move(self, uci: str) -> Optional[chess.Move]:
        """Apply a UCI move ("e2e4", "e7e8q"). Returns the Move, or None if illegal."""
        try:
            move = chess.Move.from_uci(uci)
        except ValueError:
            return None
        if move not in self.board.legal_moves:
            return None
        self.board.push(move)
        return move

    def legal_moves(self) -> List[Dict[str, str]]:
        """All legal moves as {from, to, promotion?} dicts for the frontend."""
        moves = []
        for move in self.board.legal_moves:
            entry = {
                "from": chess.square_name(move.from_square),
                "to": chess.square_name(move.to_square),
            }
            if move.promotion:
                entry["promotion"] = chess.piece_symbol(move.promotion)
            moves.append(entry)
        return moves

    def legal_moves_uci(self) -> List[str]:
        return [move.uci() for move in self.board.legal_moves]

    # ── State ────────────────────────────────────────────────

    def turn(self) -> str:
        return "w" if self.board.turn == chess.WHITE else "b"

    def last_move(self) -> Optional[Dict[str, str]]:
        if not self.board.move_stack:
            return None
        move = self.board.move_stack[-1]
        return {
            "from": chess.square_name(move.from_square),
            "to": chess.square_name(move.to_square),
        }

    def last_move_san(self) -> Optional[str]:
        if not self.board.move_stack:
            return None
        move = self.board.pop()
        san = self.board.san(move)
        self.board.push(move)
        return san

    def pgn(self) -> str:
        """Movetext like '1. e4 e5 2. Nf3' (no headers)."""
        game = chess.pgn.Game.from_board(self.board)
        exporter = chess.pgn.StringExporter(
            headers=False, variations=False, comments=False, columns=None
        )
        text = game.accept(exporter)
        # Strip the result marker ("*", "1-0", ...) from the end
        for marker in ("*", "1-0", "0-1", "1/2-1/2"):
            if text.endswith(marker):
                text = text[: -len(marker)].strip()
        return text

    def captured_pieces(self) -> Dict[str, List[str]]:
        """Material diff vs the starting position.

        Returns {"w": [...], "b": [...]} where "w" lists the white pieces
        that have been captured (lowercase symbols), handling promotions
        by never reporting negative counts.
        """
        start = {
            chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2,
            chess.ROOK: 2, chess.QUEEN: 1, chess.KING: 1,
        }
        captured: Dict[str, List[str]] = {"w": [], "b": []}
        for color, key in ((chess.WHITE, "w"), (chess.BLACK, "b")):
            for piece_type, count in start.items():
                remaining = len(self.board.pieces(piece_type, color))
                for _ in range(max(0, count - remaining)):
                    captured[key].append(chess.piece_symbol(piece_type))
        return captured

    def board_update(self) -> Dict:
        """Full board snapshot sent to clients after every move."""
        return {
            "fen": self.board.fen(),
            "last_move": self.last_move(),
            "legal_moves": self.legal_moves(),
            "turn": self.turn(),
            "is_check": self.board.is_check(),
            "pgn": self.pgn(),
            "captured": self.captured_pieces(),
            "move_san": self.last_move_san(),
            "fullmove_number": self.board.fullmove_number,
        }

    # ── Game over ────────────────────────────────────────────

    def result(self) -> Optional[Dict]:
        """None while the game is live, else {result, winner, reason}."""
        if self.board.is_checkmate():
            # Side to move is checkmated; the other side wins
            winner = "b" if self.board.turn == chess.WHITE else "w"
            return {"result": "checkmate", "winner": winner, "reason": None}
        if self.board.is_stalemate():
            return {"result": "stalemate", "winner": None, "reason": None}
        if self.board.is_insufficient_material():
            return {"result": "draw", "winner": None, "reason": "insufficient_material"}
        if self.board.is_fifty_moves():
            return {"result": "draw", "winner": None, "reason": "fifty_move_rule"}
        if self.board.is_repetition():
            return {"result": "draw", "winner": None, "reason": "threefold_repetition"}
        return None
