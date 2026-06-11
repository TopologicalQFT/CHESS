"""Unit tests for the agent toolkit.
Run: ../mcp_bridge/.venv/Scripts/python -m pytest -q
"""
import chess
import pytest

import toolkit

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


def test_pinned_pieces_king_pins_only():
    # Bb5 vs Nc6 with Qd7 behind: a RELATIVE pin — deliberately NOT reported
    # (tactical suggestion, not a rules fact; user decision 2026-06-11)
    fen = "4k3/3q4/2n5/1B6/8/8/8/4K3 b - - 0 1"
    out = toolkit.pinned_pieces(fen)
    assert "Black knight on c6" not in out
    assert out.count("(none)") == 2


def test_invalid_fen():
    with pytest.raises(ValueError):
        toolkit.hanging_report("garbage")


def test_xray_battery_detected():
    # Game 093d86's missed win: Qe2 behind Re3 on the e-file bearing on e5.
    # inspect_square(e5) must surface the queen as an X-RAY attacker.
    fen = "4k3/8/8/4p3/8/4R3/4Q3/4K3 w - - 0 1"
    out = toolkit.inspect_square(fen, "e5")
    assert "White rook on e3" in out           # direct
    assert "X-RAY" in out
    assert "White queen on e2" in out          # battery behind the rook


def test_xray_not_reported_when_unaligned():
    fen = "4k3/8/8/4p3/8/4R3/2Q5/4K3 w - - 0 1"  # queen off the e-file
    out = toolkit.inspect_square(fen, "e5")
    assert "X-RAY" not in out


def test_imagine_reports_absolute_material():
    vb = fresh_vb()
    vb.start(chess.STARTING_FEN)
    out = vb.push(["e4", "d5", "exd5"])
    assert "Material HERE (absolute): White +1" in out


def test_hanging_report():
    # White Qd5 attacks undefended black Ra8; white Ra1 is undefended but unattacked
    fen = "r3k3/8/8/3Q4/8/8/8/R3K3 b - - 0 1"
    out = toolkit.hanging_report(fen)
    assert "Black rook on a8" in out
    assert "1v0" in out and "NO defenders" in out      # attacked, no defenders
    assert "White rook on a1" in out
    assert "targetable" in out                          # undefended but not attacked


def test_hanging_report_counts_defenders():
    # Black pawn b5 defended by a6 pawn, attacked by white queen
    fen = "4k3/8/p7/1p1Q4/8/8/8/4K3 w - - 0 1"
    out = toolkit.hanging_report(fen)
    assert "Black pawn on b5" in out
    assert "1v1" in out                                 # one attacker, one defender


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
