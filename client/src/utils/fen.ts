// Parse the piece-placement field of a FEN into a square → piece map.
// Piece codes match asset filenames: wK, bQ, ...

export type PieceCode =
  | 'wK' | 'wQ' | 'wR' | 'wB' | 'wN' | 'wP'
  | 'bK' | 'bQ' | 'bR' | 'bB' | 'bN' | 'bP'

export const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'] as const

export function parseFen(fen: string): Record<string, PieceCode> {
  const placement = fen.split(' ')[0]
  const board: Record<string, PieceCode> = {}
  let rank = 8
  let fileIdx = 0
  for (const ch of placement) {
    if (ch === '/') {
      rank -= 1
      fileIdx = 0
    } else if (ch >= '1' && ch <= '8') {
      fileIdx += Number(ch)
    } else {
      const color = ch === ch.toUpperCase() ? 'w' : 'b'
      const piece = ch.toUpperCase() as 'K' | 'Q' | 'R' | 'B' | 'N' | 'P'
      board[FILES[fileIdx] + rank] = `${color}${piece}` as PieceCode
      fileIdx += 1
    }
  }
  return board
}

// Find the king's square for a color (for the check highlight)
export function kingSquare(fen: string, color: 'w' | 'b'): string | null {
  const board = parseFen(fen)
  const target: PieceCode = color === 'w' ? 'wK' : 'bK'
  for (const [square, piece] of Object.entries(board)) {
    if (piece === target) return square
  }
  return null
}
