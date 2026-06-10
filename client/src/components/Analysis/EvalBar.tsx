const CAP = 1000

/** Vertical eval bar (lichess-style): white fills from the bottom.
 *  Painted with a gradient — child-div % heights don't resolve reliably
 *  inside a flex row whose height comes from the board SVG. */
export function EvalBar({ evalCp, flipped }: { evalCp: number; flipped: boolean }) {
  const clamped = Math.max(-CAP, Math.min(CAP, evalCp))
  let whiteFrac = 0.5 + (clamped / CAP) * 0.45
  if (flipped) whiteFrac = 1 - whiteFrac
  const pct = (whiteFrac * 100).toFixed(1)
  const label = Math.abs(clamped) >= CAP ? '#' : (clamped / 100).toFixed(1)
  const whiteOnBottom = !flipped

  return (
    <div
      className="eval-bar"
      title={`${(clamped / 100).toFixed(2)} (White)`}
      style={{
        background: whiteOnBottom
          ? `linear-gradient(to top, #eee ${pct}%, #3a3a3a ${pct}%)`
          : `linear-gradient(to bottom, #eee ${pct}%, #3a3a3a ${pct}%)`,
      }}
    >
      <span
        className={`eval-bar-label ${clamped >= 0 ? 'on-white' : 'on-black'}`}
        style={
          // Label sits inside the winning side's zone
          (clamped >= 0) === whiteOnBottom ? { bottom: 3 } : { top: 3 }
        }
      >
        {label}
      </span>
    </div>
  )
}
