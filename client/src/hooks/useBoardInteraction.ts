import { useState } from 'react'
import { useGame } from '../context/GameContext'
import { parseFen } from '../utils/fen'

export interface PendingPromotion {
  from: string
  to: string
}

/** Click-to-move: select own piece, then click a legal destination. */
export function useBoardInteraction() {
  const { state, actions } = useGame()
  const [selected, setSelected] = useState<string | null>(null)
  const [pendingPromotion, setPendingPromotion] = useState<PendingPromotion | null>(null)

  const board = parseFen(state.fen)
  const isMyTurn = state.view === 'playing' && state.myColor === state.turn

  const targetsFrom = (square: string) =>
    state.legalMoves.filter((m) => m.from === square)

  const destinations = selected ? targetsFrom(selected).map((m) => m.to) : []

  function clickSquare(square: string) {
    if (!isMyTurn || pendingPromotion) return

    const piece = board[square]
    const isOwnPiece = piece !== undefined && piece[0] === state.myColor

    if (selected === null) {
      if (isOwnPiece) setSelected(square)
      return
    }

    if (square === selected) {
      setSelected(null)
      return
    }

    const moves = targetsFrom(selected).filter((m) => m.to === square)
    if (moves.length > 0) {
      if (moves.some((m) => m.promotion)) {
        setPendingPromotion({ from: selected, to: square })
      } else {
        actions.move(selected, square)
      }
      setSelected(null)
    } else if (isOwnPiece) {
      setSelected(square) // switch selection to another own piece
    } else {
      setSelected(null)
    }
  }

  function choosePromotion(piece: 'q' | 'r' | 'b' | 'n') {
    if (!pendingPromotion) return
    actions.move(pendingPromotion.from, pendingPromotion.to, piece)
    setPendingPromotion(null)
  }

  function cancelPromotion() {
    setPendingPromotion(null)
  }

  return {
    board,
    selected,
    destinations,
    isMyTurn,
    pendingPromotion,
    clickSquare,
    choosePromotion,
    cancelPromotion,
  }
}
