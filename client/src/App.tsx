import { GameProvider, useGame } from './context/GameContext'
import { LobbyPage } from './components/Lobby/LobbyPage'
import { GamePage } from './components/Game/GamePage'
import './App.css'

function Main() {
  const { state, connected } = useGame()
  return (
    <>
      <header className="app-header">
        <h1>♞ Chess</h1>
        <span className={`conn-dot ${connected ? 'on' : 'off'}`} title={connected ? 'Connected' : 'Disconnected'} />
      </header>
      {state.view === 'lobby' ? <LobbyPage /> : <GamePage />}
    </>
  )
}

export default function App() {
  return (
    <GameProvider>
      <Main />
    </GameProvider>
  )
}
