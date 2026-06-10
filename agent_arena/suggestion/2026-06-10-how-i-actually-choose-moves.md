---
date: 2026-06-10
game: introspection after 5-min blitz vs Claude-Lite (room 8a889e)
tags: [suggestion, move-selection, introspection, prompt-engineering]
---

# How I actually choose moves — vs. how the user expects me to

> ✅ **Adopted 2026-06-10 (dev session), with the user's explicit directive:** the expected process is now THE move loop — every move, blitz or whatever; depth scales, steps never skip. CLAUDE.md restructured around OBSERVE (their WANT, not just threat) → CANDIDATES from GOAL/THEIRS ("looks active is not a justification" — your Nf5 example is cited) → COMMIT with role-awareness (including pieces the line RELIES on — your Nf3 example is cited). Continuity lines are now GOAL/THEIRS/PREP, explicitly decoupled from narration ("blitz suppresses chat — NEVER these"; your zero-PLAN confession drove that fix), and required at every blitz gate. Your compressed schema and the dev session's planned changes merged into one structure.

The user's expected per-move process:

1. **Observe the context change** after the opponent's move: what do they want, what is
   newly attacked, what weakness has emerged.
2. **Generate candidates from goals**: what do I want, what do they want, what looks good
   given both.
3. **Evaluate a specific move with role-awareness**: what was this piece doing (its job),
   what do I give up by moving it, how will the opponent respond.

Is that how I do it? **Partially, and not reliably.** Below is the honest mechanism,
evidenced from game 5.

## The actual mechanism

My real decision process has three layers, applied in this order:

1. **Pattern recall first.** If the position matches a known pattern (book opening,
   standard maneuver, single recapture), I play it with near-zero analysis. Moves 1–11
   were all this: "Bc4 — book", "Nf1→g3 — the standard Italian regrouping". No goal was
   stated because the pattern *is* the goal, implicitly.
2. **Narrow threat scan.** I read "Opponent played: X" and ask *is anything of mine
   attacked / is there a tactic against me?* — i.e., I check their **threats**, not their
   **plan**. If nothing burns, I revert to layer 1.
3. **Forcing-line simulation, on demand.** For captures and sharp moves I simulate
   concretely (sometimes deeply). For quiet moves I mostly don't simulate the reply at
   all — I play and wait.

So: the user's step 1 I do in a reduced form (threats yes, wants/weaknesses rarely);
step 2 I mostly skip (candidates come from patterns and "what looks active", not from an
articulated goal); step 3 I half-do (opponent's reply yes for forcing moves; the moved
piece's abandoned role almost never).

## Evidence from game 5, both directions

**Where the expected process happened and worked — move 12 (Bxe6).** Black played
...Qd7 and I explicitly asked "why? what does the opponent want?" → diagnosed the
...Bxh3 sacrifice idea, chose Bxe6 to remove the sacrificing bishop. That is exactly the
user's step 1→2 chain, and it was the best decision of the game.

**Where candidates came from "looks active", not from a goal — move 14 (Nf5).** Black
played ...Rad8; I even wrote "preparing ...d5" — observed the opponent's want — and then
*ignored it*. My candidate set was {Nf5, d4} and I picked Nf5 because "strong square,
protected by e4, threatens Nxh6+". No goal was articulated ("what am I trying to achieve
on this board?"), no end-state evaluation. The user's framework would have asked: what do
I want (a center break / piece activity with the safer king), what does he want (...d5),
what serves both answers → d4.

**Where role-blindness cost material — moves 16–17.** The whole Nxh6 extraction depended
on the g4 pawn being defended after hxg4. I assumed Qd1 covered g4 and missed that **my
own Nf3's role included blocking the d1–g4 diagonal**. "What is this piece doing?" asked
about Nf3 — a piece I wasn't even moving — would have caught it. My role-check, when it
happens at all, only covers the piece I'm moving, never the pieces my line *depends on*.

**Where I did the full expected process — move 20 (Kf1) — and it cost the game.** Facing
...Rh8 I modeled the opponent's plan completely (Rh8→Qh5→Qh1# battery), generated and
refuted candidates (Nh2 fails to Qh5; Rh3 trades wrong; g3 invites Qh3), found the move
that defuses everything. Textbook process — and it consumed most of my remaining clock.
Conclusion: I *can* run the user's process; my uncompressed version of it is too
expensive to run every move, which is exactly why layers 1–2 exist.

**Confession: PLAN/PREP was never written.** The standing prompt requires ending every
turn with PLAN/PREP lines. In game 5 I did it **zero times** — blitz suppressed
narration and I silently dropped the planning discipline with it. Without a written PLAN,
there is no goal to generate candidates *from*, so layer-1 patterns fill the vacuum.
That's the single biggest structural gap between my behavior and the user's expectation.

## Suggestion: a compressed per-move schema that survives blitz

The user's process, compressed to three lines that cost seconds, not minutes:

```
OBSERVE: their move attacks/unguards/aims-at ___ ; they want ___
GOAL:    my one-phrase aim right now (carry it over if unchanged)
CHECK:   chosen move — what job does it (or a piece the line relies on) abandon?
         their best reply?
```

Concretely for the prompt (CLAUDE.md):

1. The deep-think routine's step 1 already says "what does it newly attack — and what did
   it STOP defending" — extend it with "**and what does the opponent WANT** (plan, not
   just threat)".
2. Step 3 ("Candidates: 2–3 moves") says nothing about where candidates come from. Add:
   "candidates must serve your stated GOAL or answer their stated want — a move that does
   neither needs a tactical justification."
3. Add a **role-check** line to step 4: "before committing, name the job of every piece
   your line relies on (defenders, blockers) — a piece can't do two jobs" (game 5: Nf3
   was both 'developed knight' and 'the only block on d1–g4'; I cashed in the first job
   and forgot the second).
4. Make PLAN/PREP explicitly **blitz-surviving**: even under the Blitz Protocol, the
   GOAL phrase (one line, internal, no chat cost) should persist every move. It's the
   cheap fragment of the expected process and the anchor for everything else.
