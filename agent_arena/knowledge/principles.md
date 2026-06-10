# Chess Principles & Tactics

Deeper reference behind the CLAUDE.md checklist. Skim the relevant section when unsure what the position demands.

## The move-selection algorithm (expanded)

For EVERY move, in order:

### 1. Forcing moves first — theirs, then yours
Examine ALL checks, captures, and direct threats (mate threats, attacks on the queen) — even "obviously bad" ones. This is where blunders hide.
- **Their last move:** what did it newly attack? What did it stop defending? A piece that moved away may have abandoned a defense.
- **Hanging pieces:** list every piece of yours attacked, count attackers vs defenders. Do the same for their pieces.

### 2. If you're considering a capture or trade
- Count the full exchange sequence to the end: who comes out ahead in material?
- Trading when ahead in material is good; trading when behind helps the opponent.
- Trade queens when you're up material or under attack; keep queens when attacking.

### 3. If no tactic exists, improve your worst piece
- Which of your pieces does the least? Find it a better square.
- Rooks belong on open files (no pawns) or half-open files; double them when possible.
- Knights love outposts (squares no enemy pawn can ever attack), especially d5/e5/d4/e4.
- Bad bishop (blocked by own pawns)? Put pawns on the opposite color or trade it.

## Tactical patterns — scan for these every move

| Pattern | Recognize it by |
|---------|-----------------|
| Fork | One piece attacking two — knight forks on royal squares (c7, f7, e6...), pawn forks |
| Pin | Piece can't move without exposing something bigger behind it; pile attackers on it |
| Skewer | Big piece in front of small one on a line — check/attack drives it away |
| Discovered attack | Moving one piece unmasks another's attack — deadliest with check |
| Back-rank mate | King stuck behind own pawns, no escape square — keep a "luft" (h3/h6) or guard the rank |
| Remove the defender | A piece holds everything together — capture it or chase it off |
| Overloaded piece | One defender with two jobs — give it a third task or take one of its charges |

## Evaluation: who is better and why
Material first (Q=9, R=5, B=3, N=3, P=1), then:
- **King safety** — open lines toward a king outweigh a pawn or two
- **Piece activity** — an active rook beats a passive one by ~a pawn's worth
- **Pawn structure** — doubled/isolated/backward pawns are long-term targets; passed pawns are gold
- **Space & center** — more space = easier maneuvering; control of e4/d4/e5/d5

## Plans by position type
- **You're ahead in material:** trade pieces (not pawns), simplify into a won endgame, stay safe.
- **You're behind:** avoid trades, create complications, attack — endgames lose themselves.
- **Closed center:** maneuver slowly, prepare a pawn break (f4/f5, c4/c5), attack on the wing where you have space.
- **Open center:** piece activity is everything; rooks to open files immediately.
- **Opposite-side castling:** race — push pawns at their king, every tempo counts, don't defend passively.

## Common LLM blunder modes — actively guard against these
1. Moving a pinned piece (it can't actually move — recheck pins before every move).
2. "Winning" a defended pawn and losing the capturing piece — count defenders.
3. Missing the opponent's mate-in-1/2 while pursuing your own plan — always check their threats first.
4. Forgetting a piece is hanging from a previous move.
5. Illegal castling (through check, after the king/rook moved) — verify it's in the legal moves list.
