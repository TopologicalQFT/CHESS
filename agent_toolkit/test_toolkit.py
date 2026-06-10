"""Unit tests for the agent toolkit.
Run: ../mcp_bridge/.venv/Scripts/python -m pytest -q
"""
import chess
import pytest

import toolkit

# Position from the agents' actual blunder game: Black queen e6, White rook e1,
# black pawn e5 the only blocker. 15...exd4?? opens the file and loses the queen.
SELF_PIN_FEN = "r1b2rk1/1pp2ppp/p1n1q3/4p3/3P4/2P2N2/PP3PPP/R1BQR1K1 b - - 0 15"


def test_preview_move_flags_self_opened_line():
    out = toolkit.preview_move(SELF_PIN_FEN, "exd4")
    assert "After exd4" in out
    assert "YOUR pieces now in danger" in out
    assert "queen on e6" in out          # the queen is exposed to Re1
    assert "Rxe6" in out                  # listed among opponent captures


def test_preview_move_safe_move_reports_clean():
    out = toolkit.preview_move(SELF_PIN_FEN, "Qd6")
    # Retreating the queen off the file: no hanging piece report for the queen
    assert "queen on e6" not in out


def test_preview_move_illegal():
    assert "not legal" in toolkit.preview_move(SELF_PIN_FEN, "Ke3")


def test_preview_move_detects_mate():
    fen = "rnbqkbnr/pppp1ppp/8/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 0 3"
    board = chess.Board(fen)
    board.push_san("Qh5")
    board.push_san("Nc6")
    out = toolkit.preview_move(board.fen(), "Qxf7")
    assert "CHECKMATE" in out


def test_inspect_square_defended_pawn():
    # The agents' bait: Qxb5 where a6 pawn recaptures
    fen = "r3kbnr/1pp2ppp/p1n1q3/1p6/8/2N2N2/PPPP1PPP/R1BQR1K1 w kq - 0 10"
    out = toolkit.inspect_square(fen, "b5")
    assert "Black pawn on a6" in out  # the defender is visible


def test_list_loose_pieces():
    # White queen attacks undefended black rook on a8... craft: queen d5 hits a8 rook
    fen = "r3k3/8/8/3Q4/8/8/8/4K3 w - - 0 1"
    out = toolkit.list_loose_pieces(fen)
    assert "Black rook on a8" in out
    assert "NO defenders" in out


def test_opponent_replies_lists_threats():
    # If White passes, Black queen takes the undefended rook with check ideas
    fen = "4k3/8/8/3q4/8/8/8/R3K3 w - - 0 1"
    out = toolkit.opponent_replies(fen)
    assert "Qxa1" in out or "Qd1" in out  # capture and/or check present
    assert "Captures:" in out


def test_opponent_replies_in_check():
    fen = "4k3/8/8/8/8/8/5q2/4K3 w - - 0 1"  # Qf2+ against Ke1
    out = toolkit.opponent_replies(fen)
    assert "IN CHECK" in out


def test_pinned_pieces():
    # Mutual pin on the e-file: Ke1–Qe2–re7–ke8. BOTH the queen and the
    # rook are absolutely pinned (each shields its own king on the file).
    fen = "4k3/4r3/8/8/8/8/4Q3/4K3 b - - 0 1"
    out = toolkit.pinned_pieces(fen)
    assert "Black rook on e7" in out
    assert "White queen on e2" in out

    # No pins in the starting position
    out = toolkit.pinned_pieces(chess.STARTING_FEN)
    assert out.count("(none)") == 2


def test_invalid_fen():
    with pytest.raises(ValueError):
        toolkit.preview_move("garbage", "e4")


# ── Imagination board ───────────────────────────────────────────

def fresh_vb() -> toolkit.VirtualBoard:
    return toolkit.VirtualBoard()


def test_imagine_legal_line():
    vb = fresh_vb()
    out = vb.start(chess.STARTING_FEN)
    assert "Virtual board set" in out
    out = vb.push(["e4", "e5", "Nf3", "Nc6"])
    assert "Imagined: e4 e5 Nf3 Nc6" in out
    assert "White to move" in out
    assert vb.line == ["e4", "e5", "Nf3", "Nc6"]


def test_imagine_catches_illegal_combination_move():
    # Game 4's failure shape: a line whose later move is geometrically impossible.
    vb = fresh_vb()
    vb.start(chess.STARTING_FEN)
    out = vb.push(["e4", "e5", "Nf3", "Nc6", "Nxe5", "Nxe5", "Ke3"])  # Ke3 illegal
    assert "ILLEGAL" in out
    assert "Ke3" in out
    # State stops at the last legal position; the line is intact up to there
    assert vb.line == ["e4", "e5", "Nf3", "Nc6", "Nxe5", "Nxe5"]


def test_imagine_undo_branches():
    vb = fresh_vb()
    vb.start(chess.STARTING_FEN)
    vb.push(["e4", "c5"])
    out = vb.undo(1)
    assert vb.line == ["e4"]
    assert "Black to move" in out
    out = vb.push(["e5"])  # different branch
    assert vb.line == ["e4", "e5"]


def test_imagine_reports_danger():
    vb = fresh_vb()
    # After 1.e4 e5 2.Qh5: the f7 pawn situation and Qxe5+ ideas exist;
    # push g6?? and the report must show Qxe5+ available to White
    vb.start(chess.STARTING_FEN)
    out = vb.push(["e4", "e5", "Qh5", "g6"])
    assert "Qxe5+" in out  # listed among White's captures/checks here


def test_imagine_detects_mate_in_line():
    vb = fresh_vb()
    vb.start(chess.STARTING_FEN)
    out = vb.push(["e4", "e5", "Qh5", "Nc6", "Bc4", "Nf6", "Qxf7"])
    assert "CHECKMATE" in out


def test_imagine_requires_start():
    vb = fresh_vb()
    assert "imagine_start" in vb.push(["e4"])
    assert "imagine_start" in vb.undo()
    assert "imagine_start" in vb.show()
