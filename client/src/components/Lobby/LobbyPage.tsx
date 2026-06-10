import { useState } from 'react'
import { useGame } from '../../context/GameContext'
import type { Color } from '../../types/protocol'
import './Lobby.css'

export function LobbyPage() {
  const { state, actions, connected } = useGame()
  const [name, setName] = useState(() => localStorage.getItem('chess_name') ?? '')
  const [color, setColor] = useState<Color | 'random'>('random')
  const [timeControl, setTimeControl] = useState<number | null>(600)

  const trimmed = name.trim()
  const ready = connected && trimmed.length > 0

  function remember() {
    localStorage.setItem('chess_name', trimmed)
  }

  function create() {
    if (!ready) return
    remember()
    actions.createRoom(trimmed, color, timeControl)
  }

  function join(roomId: string) {
    if (!ready) return
    remember()
    actions.joinRoom(roomId, trimmed)
  }

  return (
    <div className="lobby">
      <section className="panel">
        <h2>Your name</h2>
        <input
          type="text"
          placeholder="Enter your name"
          maxLength={30}
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </section>

      <section className="panel">
        <h2>Create a room</h2>
        <div className="color-picker">
          {(['w', 'random', 'b'] as const).map((c) => (
            <button
              key={c}
              className={`color-option ${color === c ? 'active' : ''}`}
              onClick={() => setColor(c)}
            >
              {c === 'w' ? '♔ White' : c === 'b' ? '♚ Black' : '⚄ Random'}
            </button>
          ))}
        </div>
        <div className="color-picker">
          {([[300, '5 min'], [600, '10 min'], [null, '∞ No limit']] as const).map(([tc, label]) => (
            <button
              key={label}
              className={`color-option ${timeControl === tc ? 'active' : ''}`}
              onClick={() => setTimeControl(tc)}
            >
              ⏱ {label}
            </button>
          ))}
        </div>
        <button className="btn-primary" disabled={!ready} onClick={create}>
          Create Room
        </button>
      </section>

      <section className="panel">
        <h2>Join a room</h2>
        {state.rooms.length === 0 ? (
          <p className="empty">No open rooms — create one!</p>
        ) : (
          <ul className="room-list">
            {state.rooms.map((room) => (
              <li key={room.room_id}>
                {room.state === 'waiting' ? (
                  <>
                    <span className="room-creator">{room.creator}</span>
                    <span className="room-id">#{room.room_id}</span>
                    <span className="room-color">
                      plays {room.available_color === 'w' ? 'White' : 'Black'}
                      {room.time_control ? ` · ⏱ ${room.time_control / 60} min` : ''}
                    </span>
                    <button className="btn-primary" disabled={!ready} onClick={() => join(room.room_id)}>
                      Join
                    </button>
                  </>
                ) : (
                  <>
                    <span className="room-creator">
                      {room.white_name} vs {room.black_name}
                    </span>
                    <span className="room-id">#{room.room_id}</span>
                    <span className="room-color live">● live</span>
                    <button
                      className="btn-watch"
                      disabled={!connected}
                      onClick={() => actions.spectate(room.room_id, trimmed || undefined)}
                    >
                      Watch
                    </button>
                  </>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      {!connected && <p className="conn-warning">Connecting to server…</p>}
    </div>
  )
}
