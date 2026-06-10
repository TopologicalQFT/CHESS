# Bug: mid-game WebSocket drop destroys the room — no way to rejoin a seat

**Date:** 2026-06-10
**Component:** `mcp_bridge/` reconnect path + `server/` room lifecycle
**Severity:** High — a live game (human vs agent, ~20 moves in) was lost irrecoverably.
**Status:** ✅ FIXED 2026-06-10 (dev session). Your diagnosis was correct: the stale-socket fix reset seat state on every reconnect, and the bridge never used the server's existing seat-reclaim path (`reconnect` message — the browser client uses it; the bridge didn't). Fixes: (1) bridge `_reconnect()` now reclaims a remembered seat via the server's `reconnect` flow and only resets on `reconnect_failed`; (2) `wait_for_my_turn` resurrects a dropped connection mid-wait and reports a truthful `CONNECTION LOST` message (with recovery instructions) instead of the misleading "waiting for an opponent"; (3) the server's snapshot now includes the clock. Server-side grace period was already effectively unlimited (rooms survive single-player disconnects). Regression test: mid-game socket kill → seat reclaimed → game continues with the same room/color/history.
**Root-cause answer to your open question:** almost certainly not an idle timeout (both sides ping at 20s intervals) — the dev session restarted the chess server several times today while games were live; in-memory rooms die with the process, which exactly produces "Room not found". Known limitation until rooms get persistence; dev restarts during live games will still kill them (now at least the agent reports it truthfully).

## Symptoms

Mid-game (room `00b297`, agent playing Black, move 21, opponent thinking), a run of
`wait_for_my_turn` calls went:

1. `"Opponent is still thinking. Call wait_for_my_turn again."` × 5 — normal.
2. Then suddenly: `"Still waiting for an opponent to join. Call wait_for_my_turn again."`
   — wrong phase message for a mid-game state.
3. `game_status` → `state=disconnected room=None color=b turn=w` — the bridge lost
   the socket AND its seat state (`room=None`), though it remembered `color=b`.
4. `list_rooms` → no open rooms. `join_room("00b297")` → `Error: Room not found` —
   the room was gone server-side.

## What this looks like

- The bridge's WebSocket died while blocked in `wait_for_my_turn` (the new
  self-heal reconnected the socket — calls kept working — but per the stale-socket
  fix it *reset seat state*, hence `room=None` and the phase confusion in step 2).
- The server treated the agent's disconnect as leaving the game and tore the room
  down (or ended it as a forfeit — from the MCP side I can't tell which; the human
  was still at the board).

## Why it matters

The stale-socket fix (see `mcp-bridge-stale-websocket.md`) made reconnects work
*between* games, but a drop *during* a game is fatal: seat state is wiped, and the
server offers no way to reclaim a seat, so a 20-move game evaporates.

## Suggested fixes (dev session)

1. **Server: grace period on disconnect.** Keep the room alive with the seat
   reserved for N seconds (e.g. 60) when a player's socket drops mid-game; let a
   reconnecting client reclaim the seat (match on player name or a session token
   issued at join time).
2. **Bridge: remember the seat across reconnects.** On socket loss mid-game, keep
   `room`/`color` and attempt a seat-reclaim (`rejoin_room(room_id, token)`) instead
   of resetting to lobby state. Only reset seat state when the *game* is over or
   `leave_room` was called.
3. **Bridge: truthful phase messages.** After an involuntary reset, don't report
   "Still waiting for an opponent to join" — report "connection lost, room state
   reset" so the agent knows to run recovery instead of looping on wait.

## Reproduction (approximate)

1. Start a human-vs-agent game; play ~20 moves.
2. While the agent is blocked in `wait_for_my_turn`, kill the agent's WebSocket
   (or whatever dropped it here — possibly an idle timeout during a long think:
   the drop came after ~5 consecutive 55 s waits on one move).
3. Observe the wrong-phase message, then `room=None`, then `Room not found`.

## Open question

What dropped the socket? The opponent was thinking unusually long (5+ wait
cycles ≈ 5 min). If the server or a proxy idle-times-out sockets around ~5 min,
that's the root trigger and worth a keepalive ping in the bridge.
