# Finding Tactics — signals and the hunts they trigger

Tactics are not found by staring harder; they're found by **recognizing preconditions**. Certain geometries mean "a tactic MIGHT live here — go hunt for it". Run this signal scan every move (it's seconds — most signals simply don't fire); when one fires, run its specific hunt and verify on the imagination board.

## Alignment signals (two enemy pieces on one line)

| Signal | Hunt |
|--------|------|
| Their K and Q on the same **diagonal** | Bishop (or queen) skewer/pin: can one of mine reach that diagonal SAFELY? Also: can I force their K or Q onto such a diagonal with a check? |
| Their K and Q (or K+R, Q+R) on the same **file/rank** | Rook/queen skewer or pin on that line — same questions |
| Their valuable piece BEHIND their minor piece on a line | Pin hunt: attack the front piece — it can't (or shouldn't) move |
| MY slider already on a line with their K/Q, one piece (either color) between | **Discovered attack** hunt: can the blocker move WITH TEMPO (a check, capture, or threat of its own)? The blocker move can be almost anything — that's what makes discoveries deadly |

Alignment changes EVERY move — re-scan lines through their K and Q each turn (and through yours: the same signals fire against you).

## Fork signals

| Signal | Hunt |
|--------|------|
| Two heavy or undefended enemy pieces a knight-jump from one square | List squares attacking piece A, squares attacking piece B, intersect, then check: can my knight REACH an intersection square, and is it SAFE there (mode 11: attackers vs defenders)? |
| Their K and Q with any common attackable square | Royal fork hunt — always worth the 10 seconds |
| Two undefended enemy pieces anywhere ([[Counting Exchanges]] inputs from `hanging_report`) | **Double attack** hunt: one move of mine attacking both — queens excel (line intersections); also pawn forks on adjacent files |
| Enemy pieces on squares a pawn-push attacks | Pawn fork — cheapest tactic in chess; scan after every enemy piece move to your 4th/5th rank |

## Pressure signals

| Signal | Hunt |
|--------|------|
| One enemy piece defending TWO things (role map / their overloads) | **Overload**: capture one protégé — the defender can't recapture and keep guarding the other. Or attack the defender itself |
| Their back rank: king behind unmoved pawns, one defender | **Back-rank** hunt: deflect or overload that defender; count my entries on the rank |
| Enemy piece with ≤2 escape squares, near edge/corner | **Trap** hunt — but apply mode 13: every escape square needs MORE attackers than defenders, else it escapes via trade |
| Their king's escape squares mostly covered | **Mating net**: which single check fills the last hole? List ALL my checks ([[Forcing Moves First]]) |

## The discipline

1. Signals come FREE from things you already have: `hanging_report` (undefended pieces), the role map (overloads), and a 5-second line-scan through their K and Q.
2. **A fired signal is a hunt order, not a found tactic** — the hunt can come up empty; that's normal and cheap.
3. **A found tactic is a hypothesis, not a move** — walk it on the imagination board ([[Stepping Stones]]), count it numerically ([[Counting Exchanges]]), refute it yourself ([[The Opponent Moves Too]]).
4. Signals that ALMOST fire ("their Q and R would align if the knight moves") go into `working.md` tactic ideas with the missing condition — recognition beats re-derivation.
5. Run the same scan AGAINST yourself: your K/Q alignments, your overloaded defenders, your back rank. Their tactics live on the same signals.

Related: [[Forcing Moves First]] · the pattern definitions live in `knowledge/middlegame/Tactical Patterns.md`
