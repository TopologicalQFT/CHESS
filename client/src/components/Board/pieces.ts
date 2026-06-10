// Vite resolves these imports to hashed asset URLs at build time.
import wK from '../../assets/pieces/wK.svg'
import wQ from '../../assets/pieces/wQ.svg'
import wR from '../../assets/pieces/wR.svg'
import wB from '../../assets/pieces/wB.svg'
import wN from '../../assets/pieces/wN.svg'
import wP from '../../assets/pieces/wP.svg'
import bK from '../../assets/pieces/bK.svg'
import bQ from '../../assets/pieces/bQ.svg'
import bR from '../../assets/pieces/bR.svg'
import bB from '../../assets/pieces/bB.svg'
import bN from '../../assets/pieces/bN.svg'
import bP from '../../assets/pieces/bP.svg'
import type { PieceCode } from '../../utils/fen'

const PIECES: Record<PieceCode, string> = { wK, wQ, wR, wB, wN, wP, bK, bQ, bR, bB, bN, bP }

export function pieceSrc(code: PieceCode): string {
  return PIECES[code]
}
