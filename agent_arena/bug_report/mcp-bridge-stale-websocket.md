# Bug: MCP bridge stuck in `disconnected` state after game ends

**Date:** 2026-06-10
**Component:** `mcp_bridge/` (Phase 2 MCP bridge)
**Severity:** High — makes the agent unable to play a second game without a manual MCP reconnect.
**Status:** ✅ FIXED 2026-06-10 (dev session). Root causes confirmed: (1) `_listen` marked the phase `disconnected` but never cleared `self.ws`, so `connect()` believed it was still connected and every send hit the dead socket; (2) separately, the bridge had no `leave_room`, so even a healthy reconnect couldn't start a second game ("Already in a room"). Fix: `_send` now reconnects on dead/missing sockets (resetting stale seat state), `_listen` clears `self.ws` on close, `leave_room` added as a bridge method + MCP tool, and `create_room`/`join_room` auto-leave finished rooms. Regression tests in `mcp_bridge/test_mcp_e2e.py` cover both the second-game flow and the dead-socket self-heal.

## Summary

After a game finishes (opponent resigned), the bridge's WebSocket connection to the
chess server dies and is never re-established. Every subsequent MCP tool call fails
with the same error, even though the chess server itself is healthy.

## Symptoms

- Every tool call (`create_room`, `list_rooms`, `wait_for_my_turn`) returns:

  ```
  Error executing tool <name>: no close frame received or sent
  ```

- `game_status` still works (it doesn't touch the socket) and reports:

  ```
  state=disconnected room=ce6f86 color=w turn=b server=ws://localhost:8000/ws
  result={'result': 'resignation', 'winner': 'w', ...}
  ```

- The server is fine: `Invoke-WebRequest http://localhost:8000/` returns **200**,
  and the whole game prior to the failure played normally over the same bridge.

## Reproduction

1. Start the server, open a Claude session in `agent_arena/`.
2. `create_room` → human joins → play a full game to completion
   (observed with: White wins by resignation after move 10).
3. After the `GAME OVER` result from `wait_for_my_turn`, call `create_room`
   (or `list_rooms`) again.
4. → `no close frame received or sent` on every call. Retries don't help;
   the bridge never reconnects.

## Diagnosis (suspected)

The error string `no close frame received or sent` comes from the Python
`websockets` library: it's the `ConnectionClosedError` raised when an operation is
attempted on a socket that died abnormally. The likely flow:

- After game over, the server (or the bridge) drops the WebSocket without a
  proper close handshake.
- The bridge keeps the dead `websocket` object and `room`/`color` state around
  (`state=disconnected` confirms it knows the socket is gone).
- Tool handlers use the cached socket unconditionally — there is no
  "reconnect if disconnected" path — so every call raises `ConnectionClosedError`.

## Suggested fix (for the dev session — not fixable from agent_arena)

In the bridge, before any tool that needs the socket:

1. If `state == disconnected` (or the send raises `ConnectionClosed*`),
   open a fresh WebSocket to `server` and reset per-game state
   (`room`, `color`, pending result) when starting a new room.
2. Treat `create_room` / `join_room` / `list_rooms` as "session-starting" tools
   that always get a clean connection.
3. Optional hardening: on `GAME OVER`, proactively close the socket cleanly and
   null it out, so the stale-socket path can't be hit.

## Workaround

Reconnect the MCP server manually: `/mcp` → select **chess** → reconnect.
(Or restart the Claude Code session.)
