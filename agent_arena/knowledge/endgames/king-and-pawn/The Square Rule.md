# The Square Rule

**Question:** can the defending king catch a passed pawn with no help?

**Rule:** draw an imaginary square from the pawn to its promotion square (sides = number of ranks remaining). If the defending king can step **into the square on its move**, the pawn is caught. Outside → the pawn promotes.

```
Pawn on e4 (White), 4 ranks to go → square e4–e8–a8–a4... 
actually the square spans e4..h8 or e4..a8 toward the king's side:
count: if it's Black's move and the black king can reach
any square of the e4-pawn's square zone, it catches the pawn.
```

Practical application — count moves instead if unsure:
- Pawn needs N moves to promote.
- King needs M moves to reach the promotion square (or intercept the pawn's path).
- It matters WHOSE MOVE it is: count exactly, including the first move.

## Cautions
- A pawn still on its start square moves two — the square is one rank bigger than it looks.
- Your own pieces/pawns in the king's path break the rule — verify the path is clear.
- Two connected passers: the square rule applies to each, but defending both usually fails — the king can't be in two squares.

Related: [[Opposition]] · [[King and Pawn Index]]
