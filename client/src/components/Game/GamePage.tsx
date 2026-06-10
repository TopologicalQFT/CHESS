import { useGame } from '../../context/GameContext'
import { Board } from '../Board/Board'
import { Sidebar } from './Sidebar'
import { WaitingOverlay } from './WaitingOverlay'
import { GameOverOverlay } from './GameOverOverlay'
import './Game.css'

export function GamePage() {
  const { state } = useGame()

  return (
    <div className="game-page">
      <div className="board-area">
        <Board />
        {state.view === 'waiting' && <WaitingOverlay />}
        {state.view === 'finished' && state.result && <GameOverOverlay />}
      </div>
      <Sidebar />
    </div>
  )
}
