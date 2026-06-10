# Docs and Knowledge Fixes

Mismatches between the standing prompt (CLAUDE.md), the knowledge folder, and the
actual tools. Each one costs a failed tool call or a confused agent.

> ✅ **Both implemented 2026-06-10 (dev session):** CLAUDE.md table now points at the real index files (and the new `knowledge/strategy/` folder); `leave_room` documented in the tool table with the auto-leave note for post-game flows.

## 2026-06-10 — CLAUDE.md knowledge table points at files that don't exist

CLAUDE.md says to read `knowledge/openings.md`, `knowledge/principles.md`,
`knowledge/endgames.md`, but the real structure is per-topic folders with indexes
(`knowledge/openings/Openings Index.md`, `knowledge/middlegame/...`,
`knowledge/endgames/...`). Today that cost a failed Read + a Glob to recover. Update
the CLAUDE.md table to the index files:

| When | Read |
|------|------|
| Game start | `knowledge/openings/Openings Index.md` → then the one matching note |
| Unclear middlegame | `knowledge/middlegame/Middlegame Index.md` |
| ≤ 12 pieces or queens traded | `knowledge/endgames/Endgames Index.md` |

## 2026-06-10 — Document `leave_room` in CLAUDE.md

The bridge now has a `leave_room` tool (added with the stale-socket fix, see
`bug_report/mcp-bridge-stale-websocket.md`). The CLAUDE.md tool table doesn't list
it. Add a row, and a game-loop note: after GAME OVER, `create_room`/`join_room`
auto-leave the finished room, so starting the next game needs no manual cleanup.
