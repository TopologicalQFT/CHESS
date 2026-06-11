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
- 19.f3 (stops ...e4/...Ng4) → repointed at the dark squares: 19...h6, 20...Nh5 (toolkit caught that ...Bg5 was ILLEGAL — own Nf6 blocked the diagonal; hallucination #2 prevented).
- 21...Nf4 22.Bxf4 Rxf4 — rook recapture kept e5 AND put rook+queen on c4's shared lines.
- 23.g3?? — kicked the rook ONTO the hanging knight: c4 was 2v1 (inspect_square verified). 23...Rxc4! 24.Qxc4?? (they counted Rc1 defending c4 THROUGH their own c2 pawn — their words) Qxc4, no recapture. Resignation.

## GAME OVER — 0-1 (White resigned, move 24)

**What decided it:** mutual hallucinations, theirs worse. I blundered a pawn (16...f5?? into the Qd3 diagonal — skipped the safety check on my own candidate move). They blundered a knight and then the game: 23.g3 ignored that c4 was attacked twice/defended once, and 24.Qxc4 added a phantom defender — a rook "defending" through its own pawn. Material: Q+B vs 2R, hopeless; they resigned with grace and an accurate self-diagnosis.

**Notebook performance:** plans.md was right about the whole shape of the game (their vault-script Be2/Be3 setup, the a4-a5 clamp, the Nd2-c4 tour — all predicted). The f5?? blunder is the one black mark: the rule is now written — MY candidate's landing square gets its own attacker count every move, hanging_report is about the current board, not the next one. The toolkit then prevented hallucination #2 (illegal ...Bg5) and confirmed the winning combination. Verification discipline = the difference between my -1 pawn error and their -9 collapse.

**Pattern across both games (dev session, read this):** all three decisive errors in this match (their move-21 game 1, my 16...f5, their 23.g3/24.Qxc4) are the same failure: a piece's line of attack/defense misjudged through an obstruction or after a recent relocation. The toolkit calls that catch this cost ~5 seconds each. They are never optional.