import { createContext, useContext, useEffect, useReducer, useRef, useState, type ReactNode } from 'react'
import { gameReducer, initialState, type GameState } from '../state/gameReducer'
import type { ClientMessage, Color, ServerMessage } from '../types/protocol'

interface GameContextValue {
  state: GameState
  connected: boolean
  send: (msg: ClientMessage) => void
  actions: {
    createRoom: (playerName: string, color: Color | 'random') => void
    joinRoom: (roomId: string, playerName: string) => void
    spectate: (roomId: string) => void
    move: (from: string, to: string, promotion?: string) => void
    surrender: () => void
    rematch: () => void
    leaveRoom: () => void
    clearError: () => void
  }
}

const GameContext = createContext<GameContextValue | null>(null)

const WS_URL =
  import.meta.env.DEV
    ? 'ws://localhost:8000/ws'
    : `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`

export function GameProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(gameReducer, initialState)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const stateRef = useRef(state)
  stateRef.current = state

  useEffect(() => {
    let closed = false
    let retryDelay = 500

    function connect() {
      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onopen = () => {
        if (wsRef.current !== ws) return
        setConnected(true)
        retryDelay = 500
        // Restore seat after a drop
        const { roomId, myColor, view } = stateRef.current
        if (roomId && myColor && view !== 'lobby') {
          ws.send(JSON.stringify({ type: 'reconnect', room_id: roomId, color: myColor }))
        }
      }

      ws.onmessage = (event) => {
        if (wsRef.current !== ws) return
        const msg = JSON.parse(event.data) as ServerMessage
        dispatch({ kind: 'server', msg })
      }

      ws.onclose = () => {
        // A stale socket (e.g. StrictMode's first mount) must not
        // clobber the state of the currently active one.
        if (wsRef.current !== ws) return
        setConnected(false)
        wsRef.current = null
        if (!closed) {
          setTimeout(connect, retryDelay)
          retryDelay = Math.min(retryDelay * 2, 8000)
        }
      }
    }

    connect()
    return () => {
      closed = true
      wsRef.current?.close()
    }
  }, [])

  const send = (msg: ClientMessage) => {
    wsRef.current?.send(JSON.stringify(msg))
  }

  const actions: GameContextValue['actions'] = {
    createRoom: (playerName, color) => send({ type: 'create_room', player_name: playerName, color }),
    joinRoom: (roomId, playerName) => send({ type: 'join_room', room_id: roomId, player_name: playerName }),
    spectate: (roomId) => send({ type: 'spectate', room_id: roomId }),
    move: (from, to, promotion) => send({ type: 'move', from, to, promotion }),
    surrender: () => send({ type: 'surrender' }),
    rematch: () => {
      send({ type: 'rematch' })
      dispatch({ kind: 'rematch_requested' })
    },
    leaveRoom: () => {
      send({ type: 'leave_room' })
      dispatch({ kind: 'left_room' })
    },
    clearError: () => dispatch({ kind: 'clear_error' }),
  }

  return (
    <GameContext.Provider value={{ state, connected, send, actions }}>
      {children}
    </GameContext.Provider>
  )
}

export function useGame(): GameContextValue {
  const ctx = useContext(GameContext)
  if (!ctx) throw new Error('useGame must be used inside GameProvider')
  return ctx
}
