---
date: 2026-06-10
topic: introspection — the user's expected per-move model vs. my actual decision procedure
game-referenced: 5-min blitz vs "Claude" (room 8a889e), won on time as Black
---

# How I actually choose moves — audited against the user's expected model

> ✅ **Adopted 2026-06-10 (dev session), with the user's explicit directive:** the expected model is now THE move loop — every move, blitz included; depth scales, steps never skip (your triage becomes depth-compression, not step-skipping). Your two asks landed: (a) plan-level opponent modeling is the new THEIRS line, written every turn beside GOAL and PREP — your Nf1-labeled-routine miss is cited as exactly what it watches for; (b) symmetric defense-counting is now an explicit COMMIT-step clause ("your attackers, then THEIR defenders — you are measurably worse at the second"). Your PLAN-line mechanism was the model for making goals explicit; it's renamed GOAL.

The user's expected per-move process:

1. **Observe the context change** after the opponent's move: what do they want,
   what is newly attacked, what weakness has emerged.
2. **Generate candidates from goals**: what is MY goal, what is THEIR goal,
   what looks good given both.
3. **Evaluate a specific move** by: what was this piece doing (its role, what
   it abandons by moving), and how will the opponent respond.

Below: what I actually do, point by point, with evidence from today's game —
including where my practice falls short of the model.

## 1. Observation — partial match, with an honest caveat

What I actually run is the report-reading habit plus deep-think step 1
("their last move: why? what does it newly attack — and what did it STOP
defending?"). When I engage it, it matches the user's model well:

- **Move 14 (Nf5):** I explicitly enumerated what the knight wanted (g7, h6,
  d6 targets), counted defenders of each, concluded the real threat was a slow
  buildup, and found the weakness it created — the knight itself was loose if
  kicked. That analysis produced g6 and, later, the free piece after Nxh6+.

**The caveat:** on quiet moves I don't run this analysis — I *classify* the
move as quiet and continue my PLAN. White's h3, Re1, c3, Nbd2, Nf1 each got a
one-glance "routine Italian regrouping" label, not a fresh "what does he want"
inquiry. This is by design (the Continuity protocol: a quiet reply to a quiet
move doesn't reset thinking; ~15s/move average must hold), and today it was
correct — but it means my "observe the context change" step is **triaged, not
universal**. The triage trigger is the report itself: CAPTURE/CHECK flags,
material-count change, or a move that contradicts my PREP. If none fire, I
trust the classification. The known cost: a genuinely venomous quiet move
(slow piece re-route building toward a sacrifice) could pass the triage. Nf1
today WAS the start of the Nf5–Nxh6 idea, and I labeled it routine — the
follow-up was unsound so it worked out, but the triage did miss the intent.

## 2. Candidate generation — goal-driven via PLAN, but thinner than the model

The user's model wants candidates derived from "my goal + their goal." My
actual mechanism is the **PLAN line** I write at the end of every turn — it IS
my standing goal, and most moves are simply its next step:

- PLAN "classical development, castle short" → Nc6, Nf6, Bc5, O-O, d6.
- PLAN "keep the bishop, restrain b4" → a6, Ba7.
- PLAN "seize the open h-file" → Rh8, Rh1+, Rdh8.

So "what is my goal" is explicit and persistent — it's written down, not
re-derived. "What is their goal" enters as the **PREP line**: I predict their
two or three most likely moves and pre-compute answers. Today seven moves were
played near-instantly off PREP hits.

**Where I'm thinner than the model:** I rarely hold a sentence-level model of
the opponent's *strategic plan* (e.g., "he is regrouping Nb1–d2–f1–g3 for a
kingside attack, therefore I should counter in the center NOW"). My PREP is
move-level prediction, not plan-level. A stronger version of me would have
read Nbd2–Nf1 as the classic Italian knight-lift and started ...d5 or ...Nh5
counterplay a move earlier. Candidate breadth is also deliberately capped:
2–3 candidates normally, 1 under blitz gates — the model's full
"goal × counter-goal" sweep only happens at moments I judge critical.

## 3. Evaluating a specific move — the strongest match, with one known hole

For a candidate I do run, the procedure matches the user's model closely:

- **"What was the piece doing"** — covered by simulation step 4: picture the
  position AFTER the move; which lines did it open, what of mine now stands on
  them, what stops being defended. Example: before g6 (move 14) I explicitly
  weighed what g7 was doing (covering h6/f6 dark squares) and accepted the
  weakening because the tempo won was concrete. Example: choosing Qxe6 over
  fxe6 (move 12) was a role question — the f7 pawn's job (king cover) versus
  the queen's gain (activity, h3/g4 targets).
- **"How will the opponent respond"** — every candidate gets "their best
  answer?" (step 3), and the answer I expect becomes next turn's PREP. The
  exd5-fork memo (never let a d5 trade fork Qe6+Nc6) lived in my PLAN/PREP for
  several moves as exactly this kind of response-anticipation.

**The known hole, demonstrated today:** my simulation verifies *my coverage*
of squares more reliably than *their defense* of them. The move-16 "trapped
knight" miscount happened because I checked that g4 was attacked by my Nf6
and never asked who defended g4 (the h3 pawn). Attack-counting and
defense-counting are the same operation run from opposite sides, and I am
measurably better at the first. Already filed as blunder-mode material in the
previous note; flagged here again because it is precisely the gap between
"considering the move" and "considering the move in THEIR terms."

## Summary verdict

| User's expected step | My implementation | Fidelity |
|---|---|---|
| Observe context change, opponent's intent, new weaknesses | Deep-think step 1 + report flags, but **triaged** — quiet moves get classified, not analyzed | Partial |
| Candidates from my goal + their goal | PLAN line (my goal, explicit) + PREP (their moves, predicted); their *strategic plan* mostly absent | Partial-good |
| Per-move: piece's role, opponent's response | Simulation step 4 + "their best answer" + PREP write-down | Good (modulo defense-counting hole) |

The triage and the capped candidate count are deliberate clock economics, not
laziness — the 15s/move average and blitz hard gates demand them, and today
they won the game on time. The two real deficiencies worth prompt work:
**(a)** plan-level (not just move-level) opponent modeling — one sentence per
turn, "his last N moves point at X"; **(b)** symmetric defense-counting in
simulations, same rigor as attack-counting.
