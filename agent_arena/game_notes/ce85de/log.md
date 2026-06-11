# Log — append-only

<!-- One line per move worth remembering — decisions, warnings to future-you,
     things the opponent revealed:
       12. Bxe6 — removed the ...Bxh3 sac bishop (their plan defused)
       14. ...Rad8 — prepares ...d5. DON'T ignore.

     GAME OVER: append the result and a short post-mortem — what decided the
     game, and which notebook entry was wrong or missing ("the losing tactic
     was never in working.md tactic ideas", "plans.md was right but I
     abandoned it at move 18"). The dev session studies these to improve you. -->

1-12: Najdorf, classical 6.Be2; a4-a5 clamp + 12.Nd5 wedge — model play, position pleasant.
16. Rfc1 — correctly UN-staled the "c4 push safe" verdict after ...Rfc8 (recounted: 2v1 against). The discipline worked HERE.
17. Qxf5! — free pawn correctly counted and banked (+1).
18. Qd3 (vs Qe6+!?) — user later showed Qe6+ was the better practical try; my rejection used a PHANTOM DEFENDER (Qc7 "defending" e7 through their own Nd7). Cost: nothing on the board. Warning unheeded.
22. Bxf4 — right trade (+1 held, their attack defanged).
24. Qxc4?? — THE LOSING MOVE. Recaptured the exchange sac believing "Rc1 defends c4" — MY OWN c2 PAWN blocks c1-c4. Their ...Qxc4 stood unanswerable: queen lost for rook, -6.

## RESULT: 0-1 — resigned move 25. Two losses to the same opponent.

## Post-mortem
- The losing error was MODE 16 (phantom defender through an occupied square) — the EXACT pattern I had named, filed, and discussed IN THIS SESSION, ~20 minutes earlier, after the user's Qe6+ question exposed it at move 18. Writing the note did not change the behavior: at move 24 I again asserted a defense line ("Rc1 ✓ c1-c4 ✓") without tracing the squares. c2 has been my own pawn ALL GAME.
- Compounding: at move 16 I had even recounted c4-related geometry (the c4 PUSH) and the c2 pawn was central to that count. The knowledge was in context. Assertion beat derivation anyway.
- The opponent TELEGRAPHED it twice: "f4 and c4 share the rank" and "my queen already watches your knight" — Rxc4 was never a sac; c4 was 2v1 (their R+Q vs my Q as sole defender... and my "second defender" was fictional).
- Process conclusion for the dev session: in-context lessons do NOT reliably transfer to in-move behavior within the same session. The fix must be MECHANICAL: (a) the CONTACTS/defender-trace must come from the report or a toolkit call, not from my assertions; (b) protocol amendment candidate: before ANY recapture or "X defends Y" claim used in a decision, call inspect_square(fen, Y) — the tool lists real defenders only. inspect_square at move 24 would have shown c4: White defenders: Qd3 ONLY. One call, game saved.
- What worked: moves 1-23 were my best chess of the project — opening discipline, the un-staled c4 verdict at move 16, the counted pawn win at 17, the right defusing trade at 22. The gap between my best and my worst is one unverified geometric assertion.
