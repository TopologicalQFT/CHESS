// TypeScript mirror of the WebSocket protocol.
// See docs/Overall Plan/Website Design/WebSocket Protocol.md

export type Color = 'w' | 'b'

export interface LegalMove {
  from: string
  to: string
  promotion?: string
}

export interface RoomSummary {
  room_id: string
  state: 'waiting' | 'playing'
  creator: string
  available_color: Color | null
  created_at: string
  white_name?: string
  black_name?: string
}

export interface ChatMessage {
  sender: string
  role: Color | 'spectator'
  text: string
}

export interface GameResult {
  result: 'checkmate' | 'stalemate' | 'resignation' | 'draw'
  winner: Color | null
  reason: string | null
  pgn: string
}

// ── Server → Client ──────────────────────────────────────────

export interface BoardUpdateFields {
  fen: string
  last_move: { from: string; to: string } | null
  legal_moves: LegalMove[]
  turn: Color
  is_check: boolean
  pgn: string
  captured: { w: string[]; b: string[] }
  move_san: string | null
  fullmove_number: number
}

export type ServerMessage =
  | ({ type: 'room_list'; rooms: RoomSummary[] })
  | ({ type: 'room_created'; room_id: string; color: Color })
  | ({ type: 'room_joined'; opponent_name: string })
  | ({ type: 'game_started'; fen: string; your_color: Color | null; white_name: string; black_name: string; legal_moves: LegalMove[]; turn: Color })
  | ({ type: 'spectate_joined'; room_id: string; room_state: string; white_name: string; black_name: string; chat: ChatMessage[] } & Partial<BoardUpdateFields>)
  | ({ type: 'chat' } & ChatMessage)
  | ({ type: 'board_update' } & BoardUpdateFields)
  | ({ type: 'game_over' } & GameResult)
  | ({ type: 'rematch_offered' })
  | ({ type: 'opponent_disconnected' })
  | ({ type: 'opponent_reconnected' })
  | ({ type: 'opponent_left' })
  | ({ type: 'game_restored'; room_state: string; your_color: Color; white_name: string; black_name: string } & Partial<BoardUpdateFields>)
  | ({ type: 'room_closed' })
  | ({ type: 'reconnect_failed' })
  | ({ type: 'error'; message: string })

// ── Client → Server ──────────────────────────────────────────

export type ClientMessage =
  | { type: 'get_rooms' }
  | { type: 'create_room'; player_name: string; color: Color | 'random' }
  | { type: 'join_room'; room_id: string; player_name: string }
  | { type: 'spectate'; room_id: string; player_name?: string }
  | { type: 'chat'; text: string }
  | { type: 'move'; from: string; to: string; promotion?: string }
  | { type: 'surrender' }
  | { type: 'rematch' }
  | { type: 'leave_room' }
  | { type: 'reconnect'; room_id: string; color: Color }
