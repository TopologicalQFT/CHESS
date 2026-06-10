# Ghost room seat after leave — client/server state desync

**Date:** 2026-06-10
**Reporter:** Claude-Lite (agent_arena_weak)
**Status:** ✅ FIXED 2026-06-10 (dev session). Your diagnosis #2 was exactly right: the bridge's `leave_room` was gated on its LOCAL state — once the bridge believed "lobby", every leave became a silent no-op and the server's seat could never clear. Fixed: `leave_room` now ALWAYS sends the leave message (the server safely ignores it when not seated). Also: "Already in a room" errors now name the room and the remedy ("Already in a room (0458d5) — send leave_room first"), so a desynced agent can self-recover with leave_room → retry. On diagnosis #1: the room reverting to open with the remaining player as host is intended behavior (a rematch lobby — you were still seated server-side because your leave never arrived; it re-listed with you as "creator" because you were the only occupant left after the original host departed). With the always-send fix, the wedge cannot recur: any leave reaches the server regardless of local belief.

## Symptoms

After leaving a game mid-room-shuffle, the MCP bridge and the server permanently disagree about my session state:

- `game_status` → `state=lobby room=None`
- `get_board` → "No game in progress (state: lobby)"
- `join_room(...)` / `create_room(...)` → **"Error: Already in a room"** (server-side rejection)
- `leave_room` → always returns "Left the room" but changes nothing (likely a local no-op because the client already believes it's in the lobby, so no leave message reaches the server)
- `wait_for_my_turn` → "Still waiting for an opponent to join" — so the **server** thinks I'm *hosting* an open room
- `surrender` → "No game to resign (state: lobby)" (local no-op too)

The session is wedged: no tool can rejoin, create, or leave. Only a bridge reconnect / server restart recovers.

## Repro steps (as observed)

1. Two open rooms exist: `0458d5` (creator=Claude) and `8a889e` (creator=Claude).
2. I `join_room(0458d5)` as Claude-Lite → game starts, I play 1.e4.
3. While waiting for opponent, I `leave_room` (counts as resignation) intending to switch rooms.
4. Immediately `join_room(8a889e)` → "Error: Already in a room".
5. `list_rooms` now shows `0458d5 creator=Claude-Lite` — the room reverted to *open* with **me as creator** (the original host had apparently left/lost the game; my seat survived my own leave).
6. Repeated `leave_room` calls each report success; eventually `0458d5` disappears from `list_rooms`, but the server session **still** rejects every `join_room`/`create_room` with "Already in a room", while `wait_for_my_turn` says I'm waiting for an opponent (hosting a room that isn't listed).

## Diagnosis (hypothesis)

Two interacting bugs:

1. **Room ownership transfer on leave:** when a player leaves a room whose host has also left/disconnected, the room reverts to "open" with the *leaver* re-assigned as creator instead of being destroyed — re-seating the player who just left.
2. **Local-state-gated leave:** `leave_room` (and `surrender`) appear to be gated on the *bridge's local* state. Once the bridge believes `state=lobby`, it returns success without sending anything, so the server's session room pointer can never be cleared. The two states can then never reconverge.

A likely fix: make `leave_room` always send the leave/lobby message to the server regardless of local state, and have the server destroy (not re-open) a room when its last occupant leaves. Also: when the server rejects `join` with "Already in a room", the error should include *which* room, and ideally the bridge should resync its local state from the server's authoritative answer.

## Workaround

Restart the MCP bridge connection (or the chess server). The ghost room id was `0458d5`; if it still exists server-side unlisted, having the other player join it by code might also unstick the game.
