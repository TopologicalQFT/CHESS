# Visual Design

Visual identity for [[Chess Webpage]]. Preview: open `client/assets-preview.html` in a browser.

## Piece Set
**CBurnett** (public domain, by Colin M.L. Burnett) — the standard set used by Wikipedia and Lichess.
- Location: `client/src/assets/pieces/`
- Files: `wK wQ wR wB wN wP bK bQ bR bB bN bP` (.svg, 45×45 viewBox)
- Source: Wikimedia Commons (`Chess_klt45.svg` etc.)

## Board Colors (lichess-style)
| Element | Color | Notes |
|---------|-------|-------|
| Light squares | `#f0d9b5` | warm cream |
| Dark squares | `#b58863` | warm brown |
| Coordinate labels | contrasting square color | small, corners of edge squares |

## Highlight Colors
| Element | Color | Usage |
|---------|-------|-------|
| Selected square | `rgba(20, 85, 30, 0.5)` | green tint on the selected piece's square |
| Legal move dot | `rgba(20, 85, 30, 0.3)` | small circle, center of empty target squares |
| Legal capture ring | `rgba(20, 85, 30, 0.3)` | ring around occupied target squares |
| Last move | `rgba(155, 199, 0, 0.41)` | yellow-green tint on from/to squares |
| Check | radial `rgba(255, 0, 0, 0.55)` | red glow on the checked king's square |

## UI Palette (dark theme, lichess-inspired)
| Element | Color |
|---------|-------|
| Page background | `#161512` |
| Panel / sidebar background | `#262421` |
| Panel border | `#3d3a37` |
| Text primary | `#bababa` |
| Text bright | `#ffffff` |
| Accent (buttons, links) | `#629924` (green) |
| Accent hover | `#75b32d` |
| Danger (surrender, errors) | `#cc3333` |
| Move history hover | `#2b2926` |

## Typography
- UI: `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`
- Move notation: `"Segoe UI", sans-serif` with tabular numbers, or monospace fallback
- Sizes: board coordinates 11px, move list 14px, status 16px, headers 20px+

## Layout
```
┌──────────────────────────────────────────────┐
│ Header (site title, room info)               │
├───────────────────────────┬──────────────────┤
│                           │  Opponent info   │
│                           │  ───────────     │
│        Board              │  Move history    │
│   (max 85vh, square)      │  (scroll)        │
│                           │  ───────────     │
│                           │  Player info     │
│                           │  Controls        │
└───────────────────────────┴──────────────────┘
```
- Board is the dominant element, scales with viewport
- Sidebar fixed width (~280px) on desktop
- Captured pieces shown inline with each player's info row
