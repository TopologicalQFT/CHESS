import { useEffect, useState } from 'react'
import { useGame } from '../../context/GameContext'
import { Board } from '../Board/Board'
import { Sidebar } from './Sidebar'
import { WaitingOverlay } from './WaitingOverlay'
import { GameOverOverlay } from './GameOverOverlay'
import { AnalysisView } from '../Analysis/AnalysisView'
import './Game.css'

export function GamePage() {
  const { state } = useGame()
  const [analyzing, setAnalyzing] = useState(false)

  // A rematch (or leaving) ends analysis mode
  useEffect(() => {
    if (state.view !== 'finished') setAnalyzing(false)
  }, [state.view])

  if (analyzing && state.result) {
    return (
      <div className="game-page">
        <AnalysisView
          pgn={state.result.pgn}
          flipped={state.myColor === 'b'}
          onClose={() => setAnalyzing(false)}
        />
      </div>
    )
  }

  return (
    <div className="game-page">
      <div className="board-area">
        <Board />
        {state.view === 'waiting' && <WaitingOverlay />}
        {state.view === 'finished' && state.result && (
          <GameOverOverlay onAnalyze={() => setAnalyzing(true)} />
        )}
      </div>
      <Sidebar />
    </div>
  )
}
