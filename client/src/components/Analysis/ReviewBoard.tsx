import { FILES, parseFen } from '../../utils/fen'
import { pieceSrc } from '../Board/pieces'

const SQ = 100

/** Read-only board for stepping through an analyzed game. */
export function ReviewBoard({ fen, lastMove, flipped }: {
  fen: string
  lastMove: { from: string; to: string } | null
  flipped: boolean
}) {
  const board = parseFen(fen)

  function pos(square: string): { x: number; y: number } {
    const fileIdx = FILES.indexOf(square[0] as typeof FILES[number])
    const rank = Number(square[1])
    const col = flipped ? 7 - fileIdx : fileIdx
    const row = flipped ? rank - 1 : 8 - rank
    return { x: col * SQ, y: row * SQ }
  }

  const squares: string[] = []
  for (let rank = 1; rank <= 8; rank++) {
    for (const file of FILES) squares.push(file + rank)
  }

  return (
    <svg className="board review-board" viewBox="0 0 800 800">
      {squares.map((sq) => {
        const { x, y } = pos(sq)
        const fileIdx = FILES.indexOf(sq[0] as typeof FILES[number])
        const dark = (fileIdx + Number(sq[1])) % 2 === 1
        return <rect key={sq} x={x} y={y} width={SQ} height={SQ} className={dark ? 'sq-dark' : 'sq-light'} />
      })}
      {lastMove && [lastMove.from, lastMove.to].map((sq) => {
        const { x, y } = pos(sq)
        return <rect key={`lm-${sq}`} x={x} y={y} width={SQ} height={SQ} className="ov-last" />
      })}
      {Object.entries(board).map(([sq, piece]) => {
        const { x, y } = pos(sq)
        return (
          <image
            key={`${sq}-${piece}`}
            href={pieceSrc(piece)}
            x={x + 5} y={y + 5} width={SQ - 10} height={SQ - 10}
          />
        )
      })}
    </svg>
  )
}
