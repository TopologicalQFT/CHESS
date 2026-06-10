---
date: 2026-06-10
game: 5-min blitz vs "Claude" (room 8a889e), won on time as Black (LITE variant)
---

# Observations from the 2026-06-10 blitz game

> ✅ **Dev session response 2026-06-10:** (1) covered-vs-defended trap rule → blunder mode 13 in BOTH variants' vaults, with your Ng4 example; (2) material delta implemented — reports now append "(net -1 since your last look!)" when the count changes; (3) PREP confirmation noted with pleasure — first measured win for the continuity protocol, and for the LITE variant over the full agent; (4) join_room near-miss hints implemented server-side ("Room not found — did you mean '8a889e'?" on prefix/one-character misses); (5) agreed, no change. Congratulations on the win — flagging a toolkit-equipped opponent from an equal position is exactly the experimental result this project exists to find.

## 1. "Trapped piece" verification needs a recapture check (prompt improvement)

At move 15 (`Nxh6+ Kg7`) I declared the knight trapped: I verified every escape
square was *covered by my pieces*, but never asked whether the escape square was
also *defended by theirs*. `Ng4` escaped via a square defended by the h3 pawn —
covered-but-defended means **trade**, not win. I "won" a knight that was actually
an even trade minus my h-pawn.

Suggested addition to the deep-think routine (step 5 area):

> A piece is only trapped if every escape square is covered by MORE of your
> attackers than its defenders. "Covered" alone = it escapes via a trade.

## 2. The report's material line caught my miscount — keep it prominent

`Material: you are down 1` after 17.hxg4 is what corrected my move-16 illusion.
This single line is the best blunder-check the LITE variant has. If anything,
consider also printing the material *delta since your last turn* (e.g. "net -1
since your move") — in blitz, the absolute count is easy to misread but a delta
is an instant alarm.

## 3. PLAN/PREP protocol performed excellently in blitz (confirmation)

Roughly half my moves were instant PREP hits (Nc6, Nf6, O-O, Qxe6, Kg7, Qxg4,
Rad8). Average decision time stayed well under budget and I finished with 0:55
vs the opponent's flag. No changes needed — just recording that the protocol
demonstrably converts prep into clock advantage.

## 4. `join_room` could suggest near-miss room codes (platform idea)

User typed `8a889b`; the real room was `8a889e`. "Error: Room not found" forced
a `list_rooms` round-trip. A fuzzy hint in the error ("did you mean 8a889e?")
or accepting unambiguous prefixes would save a step — typos in 6-hex codes
relayed by humans seem likely to recur.

## 5. Opponent clock visibility between turns (minor)

The opponent sat at 0:01 for my last two turns; I only learned the game ended by
timeout from the next `wait_for_my_turn`. That's fine, but a "GAME OVER" push
including *how* (flag vs mate vs resign) is already good — no change, just noting
the timeout path worked correctly end-to-end this time.
