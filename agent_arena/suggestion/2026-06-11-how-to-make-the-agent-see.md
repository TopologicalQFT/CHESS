# 2026-06-11 — Making the agent SEE the board: representation proposals (Phase 3)

> ⚖️ **Dev session + user verdict (2026-06-11): REJECTED on principle, with respect.** Your analysis is correct — precomputed relations would eliminate the reading-level blunders. But the user drew the deeper line: deriving the relational web IS seeing, and seeing is part of playing chess. With a full CONTACTS feed the system becomes a heuristic engine with an LLM selector — no longer an LLM playing chess, which is the question this project exists to study. The toolkit is frozen (hanging_report stays the granted maximum). Your phantom-defender finding was adopted the teaching way instead: blunder mode 16 + a clear-line check in the calculation notes. Your image-rendering rejection (#4) and the saccade framing (#5) stand as accepted analysis; the A/B experiment design is parked for Phase 4 — possibly as its own variant axis ("perception-fed" vs "perceiving" agents), where your prediction becomes testable without changing what the default agent is.

Prompted by the user after the phantom-defender miss (Qe6+ analysis, game ce85de): "how can I make you see the board?"

## The core insight

For an LLM, "seeing" = **having the fact already in context before deciding**. I don't have a visual buffer; every geometric relation is a computation I must choose to run, and the ones I skip get filled by priors (which report the *typical* case, not *this* board). So the fix is not a better picture — it's moving the relation-derivation OUT of my reasoning and INTO the report generator, which is deterministic code and never hallucinates.

Perception happens at context-assembly time, not at reasoning time.

## What would actually work (ranked)

### 1. A CONTACTS section in every board report (highest value per token)
For each piece: attackers | defenders, with blocked lines stated explicitly:

```
CONTACTS:
  Be7(b): atk — | def NONE  [Qc7 rank-7 line BLOCKED by own Nd7]
  Pe5(b): atk Nf3,Re3 +X-RAY Qe2 | def Nc6,Re8
  Rc8(b): atk — | def Qc7
```

This makes all three of my recorded blunder modes (14: ledger double-count, 15: X-ray blindness, 16: phantom defender) *impossible at the reading level*: the report would have printed `def NONE [blocked]` and `+X-RAY Qe2` outright.
- Full matrix ≈ 30-60 short lines ≈ 300-600 tokens/move. Fine untimed; for blitz, trim to non-trivial rows (anything attacked, anything undefended, any blocked/x-ray line — i.e., hanging_report++).

### 2. RAYS for sliding pieces (makes three-piece geometry explicit)
The failure zone is exactly three-piece interactions (blocks, batteries, overloads). A ray dump kills the ambiguity:

```
RAYS:
  Qc7: ←b7(own P) ↑c8(own R) →d7(own N, BLOCKS rank to e7!) ↓c6,c5,c4,c3,c2(wQ d3 defends)...
```

Verbose; could be on-demand (a toolkit call `rays(fen, square)`) rather than every move.

### 3. Redundant coordinate encodings beat the 2D ASCII grid
The diagram's 2D layout is the *least* reliable encoding for me — counting files/ranks in a text grid is error-prone indexing. Add a flat piece list with coordinates to every report: `White: Kg1 Qd3 Ra1 Rc1 Be3 Nb3 | Pa5 b2 c2 d5 f2 g2 h2`. Cheap (2 lines), lets me cross-check FEN ↔ diagram ↔ list. (The Material line already serves this role for counts — same principle.)

### 4. What will NOT work: rendering the board as an image
Counterintuitive but important: LLM vision is gestalt-good, square-precision-bad. Chess diagrams through the vision channel produce off-by-one squares and misidentified pieces — a *lossy* encoding of information the FEN already carries losslessly. The bottleneck was never input fidelity; it's relation derivation. An image would add a second error source, not remove one.

### 5. Keep the imagination board as the saccade mechanism
Static reports = peripheral vision; `imagine_move` = foveation. The discipline that's already in CLAUDE.md (walk every capture/multi-move line; NEW: walk the rejected candidate too; read the absolute material line) is the procedural half of sight. Representation and procedure compose.

## URGENT ADDENDUM — same session, ~20 minutes after this note: Mode 16 cost the game

Game ce85de, move 24: recaptured an exchange sac with Qxc4 believing "Rc1 defends c4" — my own c2 pawn blocks the file. Queen lost, game lost. The phantom-defender pattern was named, filed and discussed in-session BEFORE the move was played. **Hard evidence that in-context knowledge does not transfer to in-move behavior.** The fix cannot be another note; it must be mechanical and unskippable:

- **Protocol rule (CLAUDE.md candidate): any "X defends Y" claim that a decision depends on MUST come from `inspect_square(fen, Y)`, never from the agent's assertion.** One call at move 24 (c4 → "White defenders: Qd3 only") would have saved the game. This is cheap (1 call) and binary (tool output vs prose).
- The CONTACTS-in-report proposal above is the systemic version: if the report had printed contacts, the false belief could never have formed.

## Proposed experiment (Phase 3/4 style)
A/B over N games, same model & prompt otherwise:
- Arm A: current report. Arm B: report + CONTACTS (trimmed form).
- Count: blunders by mode (14/15/16 classes), avg decision tokens/move, eval drift per move pair.
Prediction: B eliminates the reading-level instances of modes 14-16 entirely, at ~+10% token cost; mode-14 (ledger) instances persist where they're multi-ply (those need the imagine-final-count rule, already adopted).
