import { useEffect, useState } from 'react'
import { fetchAnalysis, type AnalysisResult } from '../../types/analysis'
import { ReviewBoard } from './ReviewBoard'
import { EvalGraph } from './EvalGraph'
import './Analysis.css'

const MARKS: Record<string, string> = { blunder: '??', mistake: '?', inaccuracy: '?!' }

export function AnalysisView({ pgn, flipped, onClose }: {
  pgn: string
  flipped: boolean
  onClose: () => void
}) {
  const [data, setData] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [ply, setPly] = useState(0) // 0 = starting position

  useEffect(() => {
    let cancelled = false
    fetchAnalysis(pgn)
      .then((d) => { if (!cancelled) { setData(d); setPly(d.moves.length) } })
      .catch((e) => { if (!cancelled) setError(e.message) })
    return () => { cancelled = true }
  }, [pgn])

  // Arrow-key navigation
  useEffect(() => {
    if (!data) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') setPly((p) => Math.max(0, p - 1))
      if (e.key === 'ArrowRight') setPly((p) => Math.min(data.moves.length, p + 1))
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [data])

  if (error) {
    return (
      <div className="analysis-state">
        <p>Analysis failed: {error}</p>
        <button className="btn-flat" onClick={onClose}>Back</button>
      </div>
    )
  }
  if (!data) {
    return (
      <div className="analysis-state">
        <div className="spinner" />
        <p>Stockfish is analyzing the game…</p>
      </div>
    )
  }

  const current = ply > 0 ? data.moves[ply - 1] : null
  const lastMove = current
    ? { from: current.uci.slice(0, 2), to: current.uci.slice(2, 4) }
    : null

  return (
    <div className="analysis-view">
      <div className="analysis-board-col">
        <ReviewBoard fen={data.fens[ply]} lastMove={lastMove} flipped={flipped} />
        <div className="nav-row">
          <button className="btn-flat" onClick={() => setPly(0)} disabled={ply === 0}>⏮</button>
          <button className="btn-flat" onClick={() => setPly(Math.max(0, ply - 1))} disabled={ply === 0}>◀</button>
          <span className="ply-label">
            {current ? `${Math.ceil(current.ply / 2)}${current.ply % 2 ? '.' : '…'} ${current.san}` : 'Start'}
          </span>
          <button className="btn-flat" onClick={() => setPly(Math.min(data.moves.length, ply + 1))} disabled={ply === data.moves.length}>▶</button>
          <button className="btn-flat" onClick={() => setPly(data.moves.length)} disabled={ply === data.moves.length}>⏭</button>
        </div>
        <EvalGraph moves={data.moves} currentPly={ply} onSelect={setPly} />
      </div>

      <div className="analysis-side">
        <div className="summary-grid">
          <SummaryCard label="White" s={data.summary.w} />
          <SummaryCard label="Black" s={data.summary.b} />
        </div>
        {current && current.class !== 'good' && (
          <div className={`hint hint-${current.class}`}>
            {current.san}{MARKS[current.class]} lost {(current.cp_loss / 100).toFixed(1)} pawns — best was <b>{current.best_san}</b>
          </div>
        )}
        <div className="analysis-moves">
          {data.moves.map((m) => (
            <span
              key={m.ply}
              className={`amove ${m.class} ${m.ply === ply ? 'current' : ''}`}
              onClick={() => setPly(m.ply)}
            >
              {m.ply % 2 === 1 ? `${Math.ceil(m.ply / 2)}. ` : ''}{m.san}
              {MARKS[m.class] ?? ''}
            </span>
          ))}
        </div>
        <button className="btn-flat" onClick={onClose}>Close analysis</button>
      </div>
    </div>
  )
}

function SummaryCard({ label, s }: { label: string; s: AnalysisResult['summary']['w'] }) {
  return (
    <div className="summary-card">
      <h3>{label}</h3>
      <div><b className="c-blunder">{s.blunders}</b> blunders</div>
      <div><b className="c-mistake">{s.mistakes}</b> mistakes</div>
      <div><b className="c-inaccuracy">{s.inaccuracies}</b> inaccuracies</div>
      <div className="acpl">ACPL {s.acpl}</div>
    </div>
  )
}
