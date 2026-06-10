# Component Hierarchy

React component tree for [[Chess Webpage]].

## Pages

The app has two main views, switching based on whether the player is in a game.

```
App
├── Header                            # Site title, nav
│
├── LobbyPage                         # When not in a game
│   ├── CreateRoomPanel
│   │   ├── ColorPicker               # Choose White / Black / Random
│   │   └── CreateButton              # → sends WS "create_room"
│   │
│   └── RoomList                      # Open rooms waiting for opponent
│       └── RoomCard (×N)             # Room ID, creator name, color available
│           └── JoinButton            # → sends WS "join_room"
│
└── GamePage                           # When in a game room
    ├── GameHeader
    │   ├── RoomInfo                   # Room ID, game mode
    │   └── ConnectionStatus           # WS connected/reconnecting indicator
    │
    ├── BoardArea                      # Central column
    │   ├── OpponentInfo               # Name, color, captured pieces (top)
    │   ├── Board                      # SVG chess board
    │   │   ├── Square (×64)          # Rect + click handler
    │   │   │   └── Piece             # SVG piece image (if occupied)
    │   │   ├── BoardOverlays
    │   │   │   ├── LastMoveHighlight  # Yellow tint on from/to squares
    │   │   │   ├── CheckHighlight     # Red tint on king's square
    │   │   │   ├── LegalMoveDots      # Circles on valid destinations
    │   │   │   └── SelectedHighlight  # Border on selected piece
    │   │   └── PromotionDialog        # Q/R/B/N picker overlay
    │   └── PlayerInfo                 # Name, color, captured pieces (bottom)
    │
    ├── Sidebar
    │   ├── GameStatus                 # "Your turn" / "Waiting..." / "Checkmate!"
    │   ├── MoveHistory                # Scrollable PGN move list
    │   │   └── MoveRow (×N)          # "1. e4 e5" — clickable for future replay
    │   └── CapturedPieces             # Material balance display
    │
    ├── GameControls
    │   ├── SurrenderButton            # With confirmation dialog
    │   ├── OfferDrawButton            # (future: sends draw offer)
    │   └── LeaveButton                # Leave room (only when game not active)
    │
    ├── WaitingOverlay                 # Shown when room is in "waiting" state
    │   ├── RoomCode                   # Shareable room ID
    │   └── WaitingMessage             # "Waiting for opponent..."
    │
    └── GameOverOverlay                # Shown when game finishes
        ├── ResultMessage              # "Checkmate — You win!" / "Draw by stalemate"
        ├── RematchButton              # Propose rematch (swap colors)
        └── BackToLobbyButton          # Return to lobby
```

## State Flow

```
WebSocket ──► useWebSocket hook ──► dispatches to useGameState reducer
                                          │
                                    GameContext (provides state + actions)
                                          │
                              ┌───────────┼───────────┐
                              ▼           ▼           ▼
                          Board      Sidebar      Controls
                       (read + act)  (read only)  (act only)
```

### Key hooks
| Hook | Responsibility |
|------|---------------|
| `useWebSocket` | Manages WS connection, reconnection, sends/receives messages |
| `useGameState` | Reducer for game state updates from server messages |
| `useBoardInteraction` | Piece selection, legal move filtering, click-to-move logic |
| `useLobby` | Room list, create/join actions |

### Context
- `WebSocketContext` — provides `send()` and connection status to all components
- `GameContext` — provides current game state (board, moves, status, players)

### Actions (what the frontend sends)
| Action | When | WebSocket message |
|--------|------|-------------------|
| Create room | Lobby → Create | `{ type: "create_room", color: "w"/"b"/"random" }` |
| Join room | Lobby → Join | `{ type: "join_room", room_id: "..." }` |
| Make move | Click destination | `{ type: "move", from: "e2", to: "e4" }` |
| Promote | Choose piece | `{ type: "move", from: "e7", to: "e8", promotion: "q" }` |
| Surrender | Click button | `{ type: "surrender" }` |
| Rematch | Click button | `{ type: "rematch" }` |
| Leave room | Click button | `{ type: "leave_room" }` |

### Events (what the server sends)
| Event | When | Payload |
|-------|------|---------|
| `room_created` | Room created | `{ room_id, color }` |
| `room_joined` | Opponent joined | `{ opponent_name }` |
| `game_started` | Both ready | `{ fen, your_color, white_name, black_name }` |
| `board_update` | After each move | `{ fen, last_move, legal_moves, turn, is_check, pgn, captured }` |
| `game_over` | Game ends | `{ result, reason, winner }` |
| `opponent_disconnected` | Opponent's WS drops | `{}` |
| `opponent_reconnected` | Opponent back | `{}` |
| `error` | Invalid action | `{ message }` |
| `room_list` | Lobby query | `{ rooms: [...] }` |
