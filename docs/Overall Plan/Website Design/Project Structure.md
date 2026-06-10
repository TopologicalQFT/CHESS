# Project Structure

Monorepo layout for [[Chess Webpage]].

```
CHESS/
├── docs/                              # Planning docs (Obsidian vault)
│
├── server/                            # Python backend
│   ├── pyproject.toml                 # Dependencies (FastAPI, python-chess, uvicorn)
│   ├── main.py                        # FastAPI app, WebSocket endpoint, startup
│   ├── game_engine.py                 # Chess logic wrapper around python-chess
│   ├── room_manager.py                # Room lifecycle: create, join, leave, list
│   ├── models.py                      # Pydantic models for WS messages
│   └── player.py                      # Player abstraction (HumanPlayer, future: LLMPlayer)
│
├── client/                            # React frontend
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── App.css
│       ├── index.css
│       │
│       ├── types/
│       │   └── protocol.ts            # TypeScript types mirroring server models
│       │
│       ├── hooks/
│       │   ├── useWebSocket.ts         # WS connection, reconnection, send/receive
│       │   ├── useGameState.ts         # Reducer for game state from server events
│       │   ├── useBoardInteraction.ts  # Click-to-move: select, legal moves, promotion
│       │   └── useLobby.ts            # Room list, create/join actions
│       │
│       ├── context/
│       │   ├── WebSocketContext.tsx     # Provides send() + connection status
│       │   └── GameContext.tsx          # Provides game state + actions
│       │
│       ├── components/
│       │   ├── Lobby/
│       │   │   ├── LobbyPage.tsx
│       │   │   ├── CreateRoomPanel.tsx
│       │   │   ├── RoomList.tsx
│       │   │   └── Lobby.css
│       │   │
│       │   ├── Board/
│       │   │   ├── Board.tsx
│       │   │   ├── Square.tsx
│       │   │   ├── Piece.tsx
│       │   │   ├── BoardOverlays.tsx
│       │   │   ├── PromotionDialog.tsx
│       │   │   └── Board.css
│       │   │
│       │   ├── Sidebar/
│       │   │   ├── Sidebar.tsx
│       │   │   ├── MoveHistory.tsx
│       │   │   ├── CapturedPieces.tsx
│       │   │   ├── GameStatus.tsx
│       │   │   ├── PlayerInfo.tsx
│       │   │   └── Sidebar.css
│       │   │
│       │   ├── Controls/
│       │   │   ├── GameControls.tsx
│       │   │   └── Controls.css
│       │   │
│       │   ├── Overlays/
│       │   │   ├── WaitingOverlay.tsx
│       │   │   └── GameOverOverlay.tsx
│       │   │
│       │   └── Layout/
│       │       ├── Header.tsx
│       │       ├── GamePage.tsx
│       │       └── Layout.css
│       │
│       └── assets/
│           └── pieces/                 # CBurnett SVG set (12 files)
│               ├── wK.svg ... wP.svg
│               └── bK.svg ... bP.svg
```

## Key Boundaries
- **`server/`** — all chess logic, move validation, game state. Single source of truth.
- **`client/`** — pure display + user intent capture. No chess validation.
- **Communication** — WebSocket JSON messages. See [[WebSocket Protocol]].
- **`server/player.py`** — Player abstraction lives server-side, ready for Phase 2 LLM integration.
