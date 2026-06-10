import type { AnalyzedMove } from '../../types/analysis'

const W = 800
const H = 140
const CAP = 1000

/** Area chart of the evaluation over the game. Click to jump to a ply. */
export function EvalGraph({ moves, currentPly, onSelect }: {
  moves: AnalyzedMove[]
  currentPly: number
  onSelect: (ply: number) => void
}) {
  if (moves.length === 0) return null
  const n = moves.length
  const x = (ply: number) => (ply / n) * W
  // eval +CAP (White winning) → y=0, -CAP → y=H
  const y = (cp: number) => H / 2 - (Math.max(-CAP, Math.min(CAP, cp)) / CAP) * (H / 2)

  let path = `M 0 ${y(0)}`
  for (const m of moves) path += ` L ${x(m.ply)} ${y(m.eval_after)}`
  const area = path + ` L ${W} ${H} L 0 ${H} Z`

  function click(e: React.MouseEvent<SVGSVGElement>) {
    const rect = e.currentTarget.getBoundingClientRect()
    const frac = (e.clientX - rect.left) / rect.width
    onSelect(Math.max(0, Math.min(n, Math.round(frac * n))))
  }

  return (
    <svg className="eval-graph" viewBox={`0 0 ${W} ${H}`} onClick={click}>
      <rect x={0} y={0} width={W} height={H} className="eg-bg" />
      <path d={area} className="eg-area" />
      <line x1={0} y1={H / 2} x2={W} y2={H / 2} className="eg-zero" />
      {moves.filter((m) => m.class === 'blunder' || m.class === 'mistake').map((m) => (
        <circle
          key={m.ply}
          cx={x(m.ply)} cy={y(m.eval_after)} r={5}
          className={`eg-dot ${m.class}`}
        />
      ))}
      <line x1={x(currentPly)} y1={0} x2={x(currentPly)} y2={H} className="eg-cursor" />
    </svg>
  )
}
