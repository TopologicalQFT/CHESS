import { useGame } from '../../context/GameContext'
import { useBoardInteraction } from '../../hooks/useBoardInteraction'
import { FILES, kingSquare } from '../../utils/fen'
import { pieceSrc } from './pieces'
import './Board.css'

const SQ = 100 // SVG units per square

export function Board() {
  const { state } = useGame()
  const {
    board, selected, destinations, pendingPromotion,
    clickSquare, choosePromotion, cancelPromotion,
  } = useBoardInteraction()

  // Orient the board so the player's color is at the bottom
  const flipped = state.myColor === 'b'
  const checkedKing = state.isCheck ? kingSquare(state.fen, state.turn) : null

  // Square name → x/y in SVG coords
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

  const isLast = (sq: string) =>
    state.lastMove !== null && (state.lastMove.from === sq || state.lastMove.to === sq)

  return (
    <svg className="board" viewBox="0 0 800 800">
      {/* Squares */}
      {squares.map((sq) => {
        const { x, y } = pos(sq)
        const fileIdx = FILES.indexOf(sq[0] as typeof FILES[number])
        const dark = (fileIdx + Number(sq[1])) % 2 === 1 // a1 (0+1) is dark
        return (
          <rect
            key={sq}
            x={x} y={y} width={SQ} height={SQ}
            className={dark ? 'sq-dark' : 'sq-light'}
            onClick={() => clickSquare(sq)}
          />
        )
      })}

      {/* Overlays under pieces: last move, selection, check */}
      {squares.filter(isLast).map((sq) => {
        const { x, y } = pos(sq)
        return <rect key={`last-${sq}`} x={x} y={y} width={SQ} height={SQ} className="ov-last" />
      })}
      {selected && (() => {
        const { x, y } = pos(selected)
        return <rect x={x} y={y} width={SQ} height={SQ} className="ov-selected" />
      })()}
      {checkedKing && (() => {
        const { x, y } = pos(checkedKing)
        return <CheckHighlight x={x} y={y} key={`check-${checkedKing}`} />
      })()}

      {/* Pieces */}
      {Object.entries(board).map(([sq, piece]) => {
        const { x, y } = pos(sq)
        return (
          <image
            key={`${sq}-${piece}`}
            href={pieceSrc(piece)}
            x={x + 5} y={y + 5} width={SQ - 10} height={SQ - 10}
            onClick={() => clickSquare(sq)}
            className="piece"
          />
        )
      })}

      {/* Legal destination markers (above pieces so captures show a ring) */}
      {destinations.map((sq) => {
        const { x, y } = pos(sq)
        const occupied = board[sq] !== undefined
        return occupied ? (
          <circle
            key={`dest-${sq}`}
            cx={x + SQ / 2} cy={y + SQ / 2} r={SQ / 2 - 6}
            className="ov-capture"
            onClick={() => clickSquare(sq)}
          />
        ) : (
          <circle
            key={`dest-${sq}`}
            cx={x + SQ / 2} cy={y + SQ / 2} r={14}
            className="ov-dot"
            onClick={() => clickSquare(sq)}
          />
        )
      })}

      {/* Coordinates */}
      {FILES.map((file, i) => {
        const col = flipped ? 7 - i : i
        return (
          <text key={`f-${file}`} x={col * SQ + SQ - 12} y={795} className="coord">
            {file}
          </text>
        )
      })}
      {[1, 2, 3, 4, 5, 6, 7, 8].map((rank) => {
        const row = flipped ? rank - 1 : 8 - rank
        return (
          <text key={`r-${rank}`} x={4} y={row * SQ + 16} className="coord">
            {rank}
          </text>
        )
      })}

      {/* Promotion picker */}
      {pendingPromotion && state.myColor && (
        <PromotionDialog
          color={state.myColor}
          square={pendingPromotion.to}
          pos={pos}
          onChoose={choosePromotion}
          onCancel={cancelPromotion}
        />
      )}
    </svg>
  )
}

function CheckHighlight({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <defs>
        <radialGradient id="check-grad">
          <stop offset="0%" stopColor="rgba(255,0,0,0.55)" />
          <stop offset="60%" stopColor="rgba(255,0,0,0.25)" />
          <stop offset="100%" stopColor="rgba(255,0,0,0)" />
        </radialGradient>
      </defs>
      <rect x={x} y={y} width={SQ} height={SQ} fill="url(#check-grad)" pointerEvents="none" />
    </g>
  )
}

function PromotionDialog({
  color, square, pos, onChoose, onCancel,
}: {
  color: 'w' | 'b'
  square: string
  pos: (sq: string) => { x: number; y: number }
  onChoose: (p: 'q' | 'r' | 'b' | 'n') => void
  onCancel: () => void
}) {
  const { x, y } = pos(square)
  const pieces: Array<'q' | 'r' | 'b' | 'n'> = ['q', 'r', 'b', 'n']
  // Stack downward from the promotion square, clamped to the board
  const startY = Math.min(y, 800 - 4 * SQ)
  return (
    <g className="promotion">
      <rect x={0} y={0} width={800} height={800} className="promo-backdrop" onClick={onCancel} />
      {pieces.map((p, i) => (
        <g key={p} onClick={() => onChoose(p)} className="promo-choice">
          <rect x={x} y={startY + i * SQ} width={SQ} height={SQ} />
          <image
            href={pieceSrc(`${color}${p.toUpperCase()}` as Parameters<typeof pieceSrc>[0])}
            x={x + 10} y={startY + i * SQ + 10} width={SQ - 20} height={SQ - 20}
          />
        </g>
      ))}
    </g>
  )
}
