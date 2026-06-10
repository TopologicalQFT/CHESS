// E2E: Carol watches Alice vs Bob live, view-only, through the real UI.
// Run: node e2e/spectator.mjs   (servers on 5173 + 8000)
import { chromium } from 'playwright'

const URL = 'http://localhost:5173'
const SHOTS = 'e2e/shots'
const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

let step = 0
const log = (m) => console.log(`[${++step}] ${m}`)

async function clickSquare(page, square, flipped) {
  const box = await page.locator('svg.board').boundingBox()
  const f = FILES.indexOf(square[0])
  const r = Number(square[1])
  const col = flipped ? 7 - f : f
  const row = flipped ? r - 1 : 8 - r
  await page.mouse.click(box.x + (col + 0.5) * (box.width / 8), box.y + (row + 0.5) * (box.height / 8))
}

const browser = await chromium.launch()
try {
  const pages = []
  for (let i = 0; i < 3; i++) {
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 860 } })
    pages.push(await ctx.newPage())
  }
  const [alice, bob, carol] = pages
  const errors = []
  for (const [n, p] of [['alice', alice], ['bob', bob], ['carol', carol]]) {
    p.on('pageerror', (e) => errors.push(`${n}: ${e.message}`))
    p.on('console', (m) => m.type() === 'error' && errors.push(`${n} console: ${m.text()}`))
  }

  // Alice and Bob start a game
  await alice.goto(URL)
  await bob.goto(URL)
  await carol.goto(URL)
  await alice.getByPlaceholder('Enter your name').fill('Alice')
  await alice.getByRole('button', { name: '♔ White' }).click()
  await alice.getByRole('button', { name: 'Create Room' }).click()
  await alice.waitForSelector('.room-code')
  const roomCode = (await alice.locator('.room-code').textContent()).trim()
  await bob.getByPlaceholder('Enter your name').fill('Bob')
  await bob.waitForSelector('.room-list li')
  await bob.locator('.room-list li', { hasText: `#${roomCode}` }).getByRole('button', { name: 'Join' }).click()
  await alice.waitForSelector('text=Your turn')
  log(`Alice vs Bob game started (room ${roomCode})`)

  // Carol sees the live room appear in her lobby without refreshing
  const carolRoom = carol.locator('.room-list li', { hasText: `#${roomCode}` })
  await carolRoom.waitFor()
  await carolRoom.locator('text=● live').waitFor()
  log('Carol sees "Alice vs Bob — live" in the lobby (pushed, no refresh)')
  await carol.screenshot({ path: `${SHOTS}/10-spectate-lobby.png` })

  // Carol watches
  await carolRoom.getByRole('button', { name: 'Watch' }).click()
  await carol.waitForSelector('svg.board')
  await carol.waitForSelector('text=Spectating')
  await carol.waitForSelector('text=White to move')
  log('Carol is in the room: board + spectator badge + neutral status')

  // Alice plays e4 → Carol sees it live
  await clickSquare(alice, 'e2', false)
  await clickSquare(alice, 'e4', false)
  await carol.waitForFunction(() =>
    document.querySelector('.move-history')?.textContent?.includes('e4'))
  await carol.waitForSelector('text=Black to move')
  log('Carol saw 1. e4 live; status flipped to "Black to move"')

  // Carol clicks pieces → nothing selects (view-only)
  await clickSquare(carol, 'e7', false)
  await clickSquare(carol, 'd2', false)
  const sel = await carol.locator('.ov-selected').count()
  if (sel !== 0) throw new Error('Spectator could select a piece!')
  log('PROBE: spectator clicks select nothing')

  // No surrender button for Carol
  const surr = await carol.getByRole('button', { name: 'Surrender' }).count()
  if (surr !== 0) throw new Error('Spectator sees a Surrender button!')
  log('PROBE: no Surrender button for spectator')

  // Chat: Alice explains her move; Carol sees it and replies; Bob sees both
  await alice.getByPlaceholder('Say something…').fill('e4 — claiming the center early')
  await alice.getByPlaceholder('Say something…').press('Enter')
  await carol.waitForSelector('text=claiming the center')
  log('Chat: Alice → Carol delivered (player to spectator)')
  await carol.getByPlaceholder('Say something…').fill('nice, classical stuff')
  await carol.getByPlaceholder('Say something…').press('Enter')
  await bob.waitForSelector('text=classical stuff')
  await bob.waitForSelector('text=(👁)')
  log('Chat: Carol → Bob delivered with spectator label')
  await carol.screenshot({ path: `${SHOTS}/11-spectate-live.png` })

  // Bob plays e5; then Bob surrenders → Carol sees neutral result
  await clickSquare(bob, 'e7', true)
  await clickSquare(bob, 'e5', true)
  await carol.waitForFunction(() =>
    document.querySelector('.move-history')?.textContent?.includes('e5'))
  await bob.getByRole('button', { name: 'Surrender' }).click()
  await bob.getByRole('button', { name: 'Confirm surrender' }).click()
  await carol.waitForSelector('text=Alice wins by resignation')
  log('Game over: Carol sees "Alice wins by resignation" (neutral wording)')
  const rematchBtn = await carol.getByRole('button', { name: /^Rematch|Accept rematch/ }).count()
  if (rematchBtn !== 0) throw new Error('Spectator sees a rematch button!')
  log('PROBE: no rematch voting for spectator')
  await carol.screenshot({ path: `${SHOTS}/12-spectate-gameover.png` })

  // Players rematch → Carol keeps watching automatically
  await alice.getByRole('button', { name: 'Rematch' }).click()
  await bob.getByRole('button', { name: 'Accept rematch' }).click()
  await carol.waitForSelector('text=White to move')
  log('Rematch started — Carol kept watching automatically')

  // Carol leaves, back to lobby
  await carol.getByRole('button', { name: 'Leave' }).click()
  await carol.waitForSelector('text=Create a room')
  log('Carol left back to the lobby')

  if (errors.length) {
    console.log('BROWSER ERRORS:'); errors.forEach((e) => console.log(' ', e))
    process.exitCode = 1
  } else {
    console.log('\nSPECTATOR E2E PASSED — no browser console errors')
  }
} finally {
  await browser.close()
}
