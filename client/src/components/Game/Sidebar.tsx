import { useEffect, useRef, useState } from 'react'
import { useGame } from '../../context/GameContext'
import { pieceSrc } from '../Board/pieces'
import type { PieceCode } from '../../utils/fen'
import { ChatPanel } from './ChatPanel'

export function Sidebar() {
  const { state, actions } = useGame()
  const [confirmSurrender, setConfirmSurrender] = useState(false)

  const me = state.myColor ?? 'w'
  const opp = me === 'w' ? 'b' : 'w'
  const names = { w: state.whiteName || 'White', b: state.blackName || 'Black' }
  const spectator = state.isSpectator

  const statusText = (() => {
    if (state.view === 'waiting') return 'Waiting for opponent…'
    if (state.view === 'finished') return 'Game over'
    if (spectator) {
      const turnText = state.turn === 'w' ? 'White to move' : 'Black to move'
      return state.isCheck ? `${turnText} — Check!` : turnText
    }
    if (!state.opponentConnected) return 'Opponent disconnected…'
    const turnText = state.turn === me ? 'Your turn' : "Opponent's turn"
    return state.isCheck ? `${turnText} — Check!` : turnText
  })()

  return (
    <aside className="sidebar">
      {spectator && <div className="spectator-badge">👁 Spectating</div>}
      <PlayerRow name={names[opp]} color={opp} captured={state.captured} myRow={false} />
      <div className={`status ${!spectator && state.turn === me && state.view === 'playing' ? 'my-turn' : ''}`}>
        {statusText}
      </div>
      <MoveHistory pgn={state.pgn} />
      <ChatPanel />
      <PlayerRow name={names[me]} color={me} captured={state.captured} myRow={!spectator} />
      {spectator && (
        <button className="btn-flat" onClick={actions.leaveRoom}>Leave</button>
      )}
      {!spectator && state.view === 'playing' && (
        <div className="control-row">
          {confirmSurrender ? (
            <>
              <button className="btn-danger" onClick={() => { actions.surrender(); setConfirmSurrender(false) }}>
                Confirm surrender
              </button>
              <button className="btn-flat" onClick={() => setConfirmSurrender(false)}>Cancel</button>
            </>
          ) : (
            <button className="btn-danger" onClick={() => setConfirmSurrender(true)}>Surrender</button>
          )}
        </div>
      )}
      {state.error && <ErrorToast />}
    </aside>
  )
}

function PlayerRow({ name, color, captured, myRow }: {
  name: string
  color: 'w' | 'b'
  captured: { w: string[]; b: string[] }
  myRow: boolean
}) {
  // Pieces THIS player has captured = opponent's lost pieces
  const taken = captured[color === 'w' ? 'b' : 'w']
  const oppColor = color === 'w' ? 'b' : 'w'
  return (
    <div className="player-row">
      <span className={`color-dot ${color === 'w' ? 'dot-white' : 'dot-black'}`} />
      <span className="player-name">{name}{myRow ? ' (you)' : ''}</span>
      <span className="captured-row">
        {taken.map((p, i) => (
          <img
            key={`${p}-${i}`}
            src={pieceSrc(`${oppColor}${p.toUpperCase()}` as PieceCode)}
            alt={p}
          />
        ))}
      </span>
    </div>
  )
}

function MoveHistory({ pgn }: { pgn: string }) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    ref.current?.scrollTo({ top: ref.current.scrollHeight })
  }, [pgn])

  // "1. e4 e5 2. Nf3" → rows of [no, white, black]
  const tokens = pgn.split(/\s+/).filter(Boolean)
  const rows: Array<{ no: string; white?: string; black?: string }> = []
  for (const token of tokens) {
    if (/^\d+\.$/.test(token)) {
      rows.push({ no: token })
    } else if (rows.length > 0) {
      const row = rows[rows.length - 1]
      if (row.white === undefined) row.white = token
      else row.black = token
    }
  }

  return (
    <div className="move-history" ref={ref}>
      {rows.length === 0 ? (
        <span className="no-moves">No moves yet</span>
      ) : (
        rows.map((row) => (
          <div key={row.no} className="move-row">
            <span className="move-no">{row.no}</span>
            <span className="move">{row.white ?? ''}</span>
            <span className="move">{row.black ?? ''}</span>
          </div>
        ))
      )}
    </div>
  )
}

function ErrorToast() {
  const { state, actions } = useGame()
  useEffect(() => {
    const t = setTimeout(actions.clearError, 2500)
    return () => clearTimeout(t)
  }, [state.error])
  return <div className="error-toast">{state.error}</div>
}
