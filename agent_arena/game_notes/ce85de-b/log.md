# Log — append-only

<!-- One line per move worth remembering — decisions, warnings to future-you,
     things the opponent revealed:
       12. Bxe6 — removed the ...Bxh3 sac bishop (their plan defused)
       14. ...Rad8 — prepares ...d5. DON'T ignore.

     GAME OVER: append the result and a short post-mortem — what decided the
     game, and which notebook entry was wrong or missing ("the losing tactic
     was never in working.md tactic ideas", "plans.md was right but I
     abandoned it at move 18"). The dev session studies these to improve you. -->

- 1-11: Najdorf (user directive), 6.Be2 e5 7.Nb3 classical; their chat again narrates their plan (a4-a5 clamp, d5 fight).
- 12.Nd5 Nxd5 13.exd5 Bf5 14.Bd3 Bxd3 — good structural trades; c-file mine, their d5 wedge shields my d6.
- 16...f5?? 17.Qxf5 — BLUNDERED A PAWN: pushed f5 into the Qd3-f5 diagonal. Root cause: skipped the hanging/safety check on my own candidate's landing square (was busy analyzing their Nc4-b6 tour). Rule: hanging_report covers the CURRENT board; my candidate move's destination needs its own attackers-count, EVERY move.
- 17...Rf8 — compensation hunt: half-open f-file + tempi on the exposed queen.