# Phase 1: Chess Webpage

Part of [[Project Overview]].

## Goal
A networked chess game where two players connect via browser, join a room, and play a full game. First milestone is **clean HvH** — everything a proper chess site needs.

## Architecture

### Client-Server Design
```
┌────────────────────────┐       WebSocket        ┌──────────────────────────┐
│    React Frontend      │ ◄──────────────────►   │     Python Backend       │
│                        │                        │                          │
│  Board (SVG)           │   ← board state        │  FastAPI + WebSocket     │
│  Sidebar (moves, etc.) │   ← game events        │  python-chess            │
│  Controls              │   → user intents        │  Room management         │
│  Lobby                 │     (move, resign,      │  Game engine             │
│                        │      create, join...)   │  Player abstraction      │
└────────────────────────┘                        └──────────────────────────┘
```

The frontend **never validates moves** — it sends intents ("move e2 to e4"), the server validates via python-chess, and broadcasts the resulting state.

## Room Flow (HvH)

```
Lobby ──► Create Room (choose W/B/Random) ──► Waiting for opponent
                                                     │
Lobby ──► Browse Rooms ──► Join Room ────────────────►│
                                                     ▼
                                               Both Ready?
                                                     │
                                                     ▼
                                               Game Starts
                                                     │
                                            ┌────────┴────────┐
                                            ▼                 ▼
                                       Game ends by:     Surrender
                                       - Checkmate       - by either player
                                       - Stalemate
                                       - Draw (various)
                                                     │
                                                     ▼
                                              Game Over Screen
                                              (result + rematch?)
```

## Room States
| State | Description |
|-------|-------------|
| `waiting` | Creator is in the room, waiting for opponent |
| `ready` | Both players connected |
| `playing` | Game in progress |
| `finished` | Game over (checkmate, stalemate, draw, resignation) |

## Board Features
- SVG rendering (8×8 grid)
- Piece images: CBurnett SVG set (public domain)
- Board oriented to player's color (white at bottom for white player, etc.)
- **Overlays:** legal move dots, last move highlight, check indication, selected piece
- Promotion dialog (Q/R/B/N picker)

## Sidebar
- **Player Info** — names, colors, connection status
- **Game Status** — whose turn, check, result
- **Move History** — scrollable PGN
- **Captured Pieces** — material diff
- **Timer** (optional, future — mention in UI but not wired initially)

## Game Actions
- **Move** — click-to-move (select piece → select destination)
- **Surrender** — confirm dialog → server ends game
- **Offer Draw** — (future, nice-to-have for Phase 1)
- **Rematch** — after game over, propose rematch (swaps colors)

## Pages / Views
See [[Component Hierarchy]] for the full component tree.

1. **Lobby** — create room, browse open rooms
2. **Game Room** — board + sidebar + controls

## Implementation Steps
See [[Implementation Order]] for the build sequence.
