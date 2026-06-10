"""Post-game Stockfish analysis.

Replays a PGN, evaluates every position, classifies each move by
centipawn loss. The engine is server-side only — never exposed to agents.
"""
import io
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional

import chess
import chess.engine
import chess.pgn

MOVETIME = float(os.environ.get("STOCKFISH_MOVETIME", "0.08"))  # seconds/position
MATE_CAP = 1000  # centipawns; mate scores clamp to ±this


def engine_path() -> Optional[str]:
    """Find the Stockfish binary: env var, local engines/, or system install."""
    env = os.environ.get("STOCKFISH_PATH")
    if env and Path(env).exists():
        return env
    local = Path(__file__).parent / "engines" / (
        "stockfish.exe" if platform.system() == "Windows" else "stockfish"
    )
    if local.exists():
        return str(local)
    for system in ("/usr/games/stockfish", "/usr/bin/stockfish"):
        if Path(system).exists():
            return system
    return None


def classify(cp_loss: int) -> str:
    if cp_loss >= 300:
        return "blunder"
    if cp_loss >= 100:
        return "mistake"
    if cp_loss >= 50:
        return "inaccuracy"
    return "good"


def _score_cp(info: dict, pov: chess.Color) -> int:
    """PovScore → clamped centipawns from `pov`'s perspective."""
    score = info["score"].pov(pov)
    cp = score.score(mate_score=MATE_CAP * 10)
    return max(-MATE_CAP, min(MATE_CAP, cp))


def analyze_pgn(pgn: str) -> Dict:
    """Full-game analysis. Raises RuntimeError if no engine is available."""
    path = engine_path()
    if path is None:
        raise RuntimeError("Stockfish not found (set STOCKFISH_PATH)")

    game = chess.pgn.read_game(io.StringIO(pgn))
    if game is None:
        raise ValueError("Could not parse PGN")
    uci_moves = [m for m in game.mainline_moves()]
    if not uci_moves:
        raise ValueError("PGN contains no moves")

    board = chess.Board()
    fens = [board.fen()]
    moves: List[Dict] = []
    limit = chess.engine.Limit(time=MOVETIME)

    with chess.engine.SimpleEngine.popen_uci(path) as engine:
        # Evaluate the starting position (and each "before" position thereafter)
        info = engine.analyse(board, limit)
        eval_before_white = _score_cp(info, chess.WHITE)
        best_before: Optional[chess.Move] = info.get("pv", [None])[0]

        for ply, move in enumerate(uci_moves, start=1):
            mover = board.turn
            san = board.san(move)
            best_san = board.san(best_before) if best_before else san
            board.push(move)
            fens.append(board.fen())

            info = engine.analyse(board, limit)
            eval_after_white = _score_cp(info, chess.WHITE)
            best_before = info.get("pv", [None])[0]

            # Loss from the mover's perspective
            if mover == chess.WHITE:
                cp_loss = max(0, eval_before_white - eval_after_white)
            else:
                cp_loss = max(0, eval_after_white - eval_before_white)

            moves.append({
                "san": san,
                "uci": move.uci(),
                "ply": ply,
                "eval_after": eval_after_white,
                "best_san": best_san,
                "cp_loss": cp_loss,
                "class": classify(cp_loss),
            })
            eval_before_white = eval_after_white

    summary = {}
    for color, key in ((chess.WHITE, "w"), (chess.BLACK, "b")):
        own = [m for i, m in enumerate(moves) if (i % 2 == 0) == (color == chess.WHITE)]
        summary[key] = {
            "blunders": sum(1 for m in own if m["class"] == "blunder"),
            "mistakes": sum(1 for m in own if m["class"] == "mistake"),
            "inaccuracies": sum(1 for m in own if m["class"] == "inaccuracy"),
            "acpl": round(sum(m["cp_loss"] for m in own) / len(own)) if own else 0,
        }

    return {"moves": moves, "fens": fens, "summary": summary}
