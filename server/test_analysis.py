"""Tests for Stockfish analysis. Skipped entirely if no engine binary."""
import pytest

import analysis

pytestmark = pytest.mark.skipif(
    analysis.engine_path() is None, reason="stockfish binary not available"
)


def test_classify_thresholds():
    assert analysis.classify(0) == "good"
    assert analysis.classify(49) == "good"
    assert analysis.classify(50) == "inaccuracy"
    assert analysis.classify(100) == "mistake"
    assert analysis.classify(300) == "blunder"


def test_analyze_short_game():
    # Scholar's mate: Black's 3...Nf6?? misses the mate threat
    result = analysis.analyze_pgn("1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#")
    moves = result["moves"]
    assert len(moves) == 7
    assert moves[0]["san"] == "e4"
    assert moves[-1]["san"] == "Qxf7#"
    # Final position is mate for White → eval at the cap
    assert moves[-1]["eval_after"] == analysis.MATE_CAP
    # 3...Nf6 allowed mate-in-1: must be a blunder
    nf6 = moves[5]
    assert nf6["san"] == "Nf6"
    assert nf6["class"] == "blunder"
    # fens: start + one per ply
    assert len(result["fens"]) == 8
    # Summary shape
    assert result["summary"]["b"]["blunders"] >= 1
    assert "acpl" in result["summary"]["w"]


def test_bad_pgn_raises():
    with pytest.raises(ValueError):
        analysis.analyze_pgn("")
