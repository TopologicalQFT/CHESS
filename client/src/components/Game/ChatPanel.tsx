import { useEffect, useRef, useState } from 'react'
import { useGame } from '../../context/GameContext'

const ROLE_LABEL: Record<string, string> = { w: 'White', b: 'Black', spectator: '👁' }

export function ChatPanel() {
  const { state, actions } = useGame()
  const [draft, setDraft] = useState('')
  const listRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight })
  }, [state.chat.length])

  function submit() {
    const text = draft.trim()
    if (!text) return
    actions.sendChat(text)
    setDraft('')
  }

  return (
    <div className="chat-panel">
      <div className="chat-messages" ref={listRef}>
        {state.chat.length === 0 ? (
          <span className="chat-empty">No messages yet</span>
        ) : (
          state.chat.map((msg, i) => (
            <div key={i} className={`chat-msg role-${msg.role}`}>
              <span className="chat-sender">
                {msg.sender}
                <span className="chat-role"> ({ROLE_LABEL[msg.role] ?? msg.role})</span>
              </span>
              <span className="chat-text">{msg.text}</span>
            </div>
          ))
        )}
      </div>
      <div className="chat-input-row">
        <input
          type="text"
          placeholder="Say something…"
          maxLength={500}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
        />
        <button onClick={submit} disabled={!draft.trim()}>Send</button>
      </div>
    </div>
  )
}
