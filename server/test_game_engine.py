"""Unit tests for GameEngine. Run: .venv/Scripts/python -m pytest -q"""
from game_engine import GameEngine


def test_initial_state():
    eng = GameEngine()
    update = eng.board_update()
    assert update["turn"] == "w"
    assert update["fen"].startswith("rnbqkbnr/pppppppp")
    assert len(update["legal_moves"]) == 20
    assert update["last_move"] is None
    assert update["captured"] == {"w": [], "b": []}
    assert eng.result() is None


def test_legal_and_illegal_moves():
    eng = GameEngine()
    assert eng.make_move("e2e4") is not None
    assert eng.make_move("e2e4") is None          # white pawn already moved
    assert eng.make_move("not-a-move") is None    # garbage input
    assert eng.make_move("e7e5") is not None
    assert eng.turn() == "w"
    assert eng.last_move() == {"from": "e7", "to": "e5"}


def test_pgn_generation():
    eng = GameEngine()
    for uci in ["e2e4", "e7e5", "g1f3"]:
        assert eng.make_move(uci)
    assert eng.pgn() == "1. e4 e5 2. Nf3"
    assert eng.last_move_san() == "Nf3"


def test_scholars_mate_checkmate():
    eng = GameEngine()
    for uci in ["e2e4", "e7e5", "d1h5", "b8c6", "f1c4", "g8f6", "h5f7"]:
        assert eng.make_move(uci), uci
    result = eng.result()
    assert result == {"result": "checkmate", "winner": "w", "reason": None}
    assert eng.board_update()["is_check"] is True


def test_captures_tracked():
    eng = GameEngine()
    for uci in ["e2e4", "d7d5", "e4d5"]:  # white captures black pawn
        assert eng.make_move(uci)
    captured = eng.captured_pieces()
    assert captured["b"] == ["p"]
    assert captured["w"] == []


def test_promotion():
    eng = GameEngine()
    # Fastest legal promotion setup via FEN
    eng.board.set_fen("8/P6k/8/8/8/8/7K/8 w - - 0 1")
    assert eng.make_move("a7a8q")
    assert eng.board.fen().startswith("Q7")


def test_stalemate():
    eng = GameEngine()
    # Black king h8 has no moves and is not in check
    eng.board.set_fen("7k/5Q2/5K2/8/8/8/8/8 b - - 0 1")
    result = eng.result()
    assert result == {"result": "stalemate", "winner": None, "reason": None}
