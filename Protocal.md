
# When game starts:
agent creates `notebook` which consists of md files.
md files for each of following
- context in general : pawn structure, assymetry, who is winning
- weaknesses : ex) backrank weakness, overloading piece(doing 2 or 3 defending roles a la fois), ...
- assets (strongness) : fiancheto bishop, open file rook, outpost horsy, ...
- my long-term strategy
- what oponent wants
- role of each piece(should mark overloaded pieces)
- undefended pieces (even the ones not attacked right now should count, since they can be targeted)
- attacked pieces
- possible tactic ideas (even the ones not currently possible.) this file is highly related to weaknesses file.
- short term scenarios ("lines")

# Each move : 3 steps

agent recieve oponent's choice and modified board.
## 1: Mandatory step
- based on the "context" of the game, examine if oponent's move is somewhat expected or something new. (in the context or context change)
- role of each piece-moved piece update 
- update undefended pieces file and attacked pieces file

# Step2
## If oponents move is under context and my response is straightforward
- just respond inside context. short term scenarios file can help.
## under context, but my move is not straightforward
then we consider followings
- read possible tactic ideas file, find new ideas, remove outdated ideas, check if there is a excecutable tactic (that was not possible before, but became possible due to oponents move)
- consider giving role to nothing-doing piece
- consider simple long-term strategic moves
and guess how the opponent will respond to each, rull out not-working moves and decide.

## Not under context
- examin what oponent wants
- update the context file and weakness file
- update the long-term strategy if needed
- read possible tactic ideas file, find new ideas, remove outdated ideas, check if there is a excecutable tactic (that was not possible before, but became possible due to oponents move)
- consider giving role to nothing-doing piece
- consider simple long-term strategic moves

# Step3 : choosing the move among candidates

## Check1 : the previous role of moving piece
## Check2 : pawn move : wouldnt this move give opponent an outpost?
in some cases, pawn moves require long-term context thinking.
pawns cant go back, thier moves are permanent
## Check3 : how will oponent respond?




  



