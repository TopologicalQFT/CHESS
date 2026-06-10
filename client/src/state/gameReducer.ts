import type { ChatMessage, Clock, Color, GameResult, LegalMove, RoomSummary, ServerMessage } from '../types/protocol'

export type View = 'lobby' | 'waiting' | 'playing' | 'finished'

export interface GameState {
  view: View
  roomId: string | null
  rooms: RoomSummary[]
  myColor: Color | null
  isSpectator: boolean
  whiteName: string
  blackName: string

  // Board state (always mirrors the server)
  fen: string
  lastMove: { from: string; to: string } | null
  legalMoves: LegalMove[]
  turn: Color
  isCheck: boolean
  pgn: string
  captured: { w: string[]; b: string[] }

  chat: ChatMessage[]
  clock: Clock          // server-reported remaining seconds
  clockAt: number       // Date.now() when that report arrived (for local ticking)
  result: GameResult | null
  rematchOffered: boolean
  rematchRequested: boolean
  opponentConnected: boolean
  error: string | null
}

export const START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

export const initialState: GameState = {
  view: 'lobby',
  roomId: null,
  rooms: [],
  myColor: null,
  isSpectator: false,
  whiteName: '',
  blackName: '',
  fen: START_FEN,
  lastMove: null,
  legalMoves: [],
  turn: 'w',
  isCheck: false,
  pgn: '',
  captured: { w: [], b: [] },
  chat: [],
  clock: null,
  clockAt: 0,
  result: null,
  rematchOffered: false,
  rematchRequested: false,
  opponentConnected: true,
  error: null,
}

export type Action =
  | { kind: 'server'; msg: ServerMessage }
  | { kind: 'left_room' }
  | { kind: 'rematch_requested' }
  | { kind: 'clear_error' }

export function gameReducer(state: GameState, action: Action): GameState {
  if (action.kind === 'left_room') {
    return { ...initialState, rooms: state.rooms }
  }
  if (action.kind === 'rematch_requested') {
    return { ...state, rematchRequested: true }
  }
  if (action.kind === 'clear_error') {
    return { ...state, error: null }
  }

  const msg = action.msg
  switch (msg.type) {
    case 'room_list':
      return { ...state, rooms: msg.rooms }

    case 'room_created':
      return { ...state, view: 'waiting', roomId: msg.room_id, myColor: msg.color }

    case 'room_joined':
      // We are the creator; opponent just arrived. game_started follows.
      return state

    case 'spectate_joined': {
      const spectating: GameState = {
        ...state,
        view: msg.room_state === 'finished' ? 'finished' : 'playing',
        roomId: msg.room_id,
        myColor: null,
        isSpectator: true,
        whiteName: msg.white_name,
        blackName: msg.black_name,
        chat: msg.chat ?? [],
        result: null,
      }
      if (msg.fen) {
        spectating.fen = msg.fen
        spectating.lastMove = msg.last_move ?? null
        spectating.legalMoves = []
        spectating.turn = msg.turn ?? 'w'
        spectating.isCheck = msg.is_check ?? false
        spectating.pgn = msg.pgn ?? ''
        spectating.captured = msg.captured ?? { w: [], b: [] }
        spectating.clock = msg.clock ?? null
        spectating.clockAt = Date.now()
      }
      return spectating
    }

    case 'game_started':
      return {
        ...state,
        view: 'playing',
        myColor: msg.your_color,
        whiteName: msg.white_name,
        blackName: msg.black_name,
        fen: msg.fen,
        legalMoves: msg.legal_moves,
        turn: msg.turn,
        lastMove: null,
        isCheck: false,
        pgn: '',
        captured: { w: [], b: [] },
        clock: msg.clock ?? null,
        clockAt: Date.now(),
        result: null,
        rematchOffered: false,
        rematchRequested: false,
        opponentConnected: true,
        error: null,
      }

    case 'board_update':
      return {
        ...state,
        fen: msg.fen,
        lastMove: msg.last_move,
        legalMoves: msg.legal_moves,
        turn: msg.turn,
        isCheck: msg.is_check,
        pgn: msg.pgn,
        captured: msg.captured,
        clock: msg.clock ?? null,
        clockAt: Date.now(),
      }

    case 'game_over':
      return {
        ...state,
        view: 'finished',
        result: { result: msg.result, winner: msg.winner, reason: msg.reason, pgn: msg.pgn },
        legalMoves: [],
      }

    case 'rematch_offered':
      return { ...state, rematchOffered: true }

    case 'opponent_disconnected':
      return { ...state, opponentConnected: false }

    case 'opponent_reconnected':
      return { ...state, opponentConnected: true }

    case 'opponent_left':
      return { ...state, opponentConnected: false }

    case 'game_restored': {
      const restored: GameState = {
        ...state,
        view: msg.room_state === 'playing' ? 'playing' : msg.room_state === 'finished' ? 'finished' : 'waiting',
        myColor: msg.your_color,
        whiteName: msg.white_name,
        blackName: msg.black_name,
      }
      if (msg.fen) {
        restored.fen = msg.fen
        restored.legalMoves = msg.legal_moves ?? []
        restored.turn = msg.turn ?? 'w'
        restored.isCheck = msg.is_check ?? false
        restored.pgn = msg.pgn ?? ''
        restored.captured = msg.captured ?? { w: [], b: [] }
        restored.lastMove = msg.last_move ?? null
      }
      return restored
    }

    case 'chat':
      return {
        ...state,
        chat: [...state.chat, { sender: msg.sender, role: msg.role, text: msg.text }].slice(-100),
      }

    case 'room_closed':
      // Players abandoned the room (e.g. both disconnected) — back to lobby
      return { ...initialState, rooms: state.rooms, error: 'The players left — room closed.' }

    case 'reconnect_failed':
      return { ...initialState, rooms: state.rooms }

    case 'error':
      return { ...state, error: msg.message }

    default:
      return state
  }
}
