import { useGame } from '../../context/GameContext'

export function GameOverOverlay({ onAnalyze }: { onAnalyze: () => void }) {
  const { state, actions } = useGame()
  const result = state.result!
  const me = state.myColor

  const headline = (() => {
    if (result.winner === null) {
      const reason = result.reason?.replace(/_/g, ' ') ?? result.result
      return `Draw — ${reason}`
    }
    if (state.isSpectator) {
      const winnerName = result.winner === 'w' ? state.whiteName : state.blackName
      const how = result.result === 'checkmate' ? 'by checkmate' : 'by resignation'
      return `${winnerName} wins ${how}`
    }
    const iWon = result.winner === me
    const how = result.result === 'checkmate' ? 'by checkmate' : 'by resignation'
    return iWon ? `You win ${how}! 🎉` : `You lose ${how}`
  })()

  return (
    <div className="overlay">
      <div className="overlay-card">
        <h2>{headline}</h2>
        {state.isSpectator && (
          <p className="rematch-note">If the players rematch, you'll keep watching.</p>
        )}
        {!state.isSpectator && state.rematchOffered && !state.rematchRequested && (
          <p className="rematch-note">Opponent wants a rematch!</p>
        )}
        {!state.isSpectator && (state.rematchRequested ? (
          <p className="rematch-note">Rematch requested — waiting for opponent…</p>
        ) : (
          <button className="btn-primary" onClick={actions.rematch}>
            {state.rematchOffered ? 'Accept rematch' : 'Rematch'}
          </button>
        ))}
        {result.pgn && (
          <button className="btn-flat" onClick={onAnalyze}>Analyze game 🔍</button>
        )}
        <button className="btn-flat" onClick={actions.leaveRoom}>Back to lobby</button>
      </div>
    </div>
  )
}
