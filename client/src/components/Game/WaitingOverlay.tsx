import { useGame } from '../../context/GameContext'

export function WaitingOverlay() {
  const { state, actions } = useGame()
  return (
    <div className="overlay">
      <div className="overlay-card">
        <h2>Waiting for opponent…</h2>
        <p>Share this room code:</p>
        <div className="room-code">{state.roomId}</div>
        <button className="btn-flat" onClick={actions.leaveRoom}>Cancel</button>
      </div>
    </div>
  )
}
