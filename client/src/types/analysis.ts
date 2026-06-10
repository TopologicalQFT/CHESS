// Response shape of POST /analyze (see docs: Post-Game Analysis)

export type MoveClass = 'good' | 'inaccuracy' | 'mistake' | 'blunder'

export interface AnalyzedMove {
  san: string
  uci: string
  ply: number
  eval_after: number // centipawns, White's POV, clamped ±1000
  best_san: string
  cp_loss: number
  class: MoveClass
}

export interface PlayerSummary {
  blunders: number
  mistakes: number
  inaccuracies: number
  acpl: number
}

export interface AnalysisResult {
  moves: AnalyzedMove[]
  fens: string[] // fens[0] = start, fens[ply] = after that ply
  summary: { w: PlayerSummary; b: PlayerSummary }
}

export const API_BASE = import.meta.env.DEV ? 'http://localhost:8000' : ''

export async function fetchAnalysis(pgn: string): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pgn }),
  })
  if (!res.ok) {
    const detail = await res.json().then((j) => j.detail).catch(() => res.statusText)
    throw new Error(detail)
  }
  return res.json()
}
