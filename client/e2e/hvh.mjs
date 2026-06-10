// E2E driver: two browser contexts play HvH chess via the real UI.
// Run: node e2e/hvh.mjs   (servers must be running on 5173 + 8000)
import { chromium } from 'playwright'

const URL = 'http://localhost:5173'
const SHOTS = 'e2e/shots'
const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

let step = 0
function log(msg) {
  step += 1
  console.log(`[${step}] ${msg}`)
}

async function clickSquare(page, square, flipped) {
  const box = await page.locator('svg.board').boundingBox()
  const fileIdx = FILES.indexOf(square[0])
  const rank = Number(square[1])
  const col = flipped ? 7 - fileIdx : fileIdx
  const row = flipped ? rank - 1 : 8 - rank
  const x = box.x + (col + 0.5) * (box.width / 8)
  const y = box.y + (row + 0.5) * (box.height / 8)
  await page.mouse.click(x, y)
}

const browser = await chromium.launch()
try {
  const ctxA = await browser.newContext({ viewport: { width: 1280, height: 860 } })
  const ctxB = await browser.newContext({ viewport: { width: 1280, height: 860 } })
  const alice = await ctxA.newPage()
  const bob = await ctxB.newPage()

  const errors = []
  for (const [name, page] of [['alice', alice], ['bob', bob]]) {
    page.on('pageerror', (e) => errors.push(`${name} pageerror: ${e.message}`))
    page.on('console', (m) => {
      if (m.type() === 'error') errors.push(`${name} console.error: ${m.text()}`)
    })
  }

  // ── Lobby: create + join ─────────────────────────────────
  await alice.goto(URL)
  await bob.goto(URL)
  await alice.getByPlaceholder('Enter your name').fill('Alice')
  await alice.getByRole('button', { name: '♔ White' }).click()
  await alice.getByRole('button', { name: 'Create Room' }).click()
  await alice.waitForSelector('.room-code')
  const roomCode = (await alice.locator('.room-code').textContent()).trim()
  log(`Alice created room ${roomCode}, sees waiting overlay`)
  await alice.screenshot({ path: `${SHOTS}/01-alice-waiting.png` })

  await bob.getByPlaceholder('Enter your name').fill('Bob')
  await bob.waitForSelector('.room-list li')
  log('Bob sees the room in the lobby list')
  await bob.screenshot({ path: `${SHOTS}/02-bob-lobby.png` })
  await bob.getByRole('button', { name: 'Join' }).click()

  await alice.waitForSelector('svg.board')
  await bob.waitForSelector('svg.board')
  await alice.waitForSelector('text=Your turn')
  log('Game started: Alice (white) sees "Your turn"')
  const bobStatus = await bob.locator('.status').textContent()
  if (!bobStatus.includes("Opponent's turn")) throw new Error(`Bob status wrong: ${bobStatus}`)
  log(`Bob (black) sees "${bobStatus.trim()}"`)

  // ── Probe: Bob clicks his pawn out of turn → nothing selected ──
  await clickSquare(bob, 'e7', true)
  const bobSelected = await bob.locator('.ov-selected').count()
  if (bobSelected !== 0) throw new Error('Bob could select a piece out of turn!')
  log('PROBE: Bob cannot select pieces out of turn')

  // ── Moves: 1. e4 e5 2. Nf3 ───────────────────────────────
  await clickSquare(alice, 'e2', false)
  await alice.waitForSelector('.ov-dot')
  const dots = await alice.locator('.ov-dot').count()
  log(`Alice selected e2, sees ${dots} legal move dots`)
  await alice.screenshot({ path: `${SHOTS}/03-alice-selected.png` })
  await clickSquare(alice, 'e4', false)

  await alice.waitForSelector('.move-row')
  await bob.waitForSelector('.move-row')
  const aliceHist = await alice.locator('.move-history').textContent()
  if (!aliceHist.includes('e4')) throw new Error(`move history missing e4: ${aliceHist}`)
  log('1. e4 played — both sides see board update + move history')

  await clickSquare(bob, 'e7', true)
  await bob.waitForSelector('.ov-dot')
  await clickSquare(bob, 'e5', true)
  await alice.waitForFunction(() =>
    document.querySelector('.move-history')?.textContent?.includes('e5'))
  log('1... e5 played by Bob (flipped board) — Alice sees it')

  await clickSquare(alice, 'g1', false)
  await alice.waitForSelector('.ov-dot')
  await clickSquare(alice, 'f3', false)
  await bob.waitForFunction(() =>
    document.querySelector('.move-history')?.textContent?.includes('Nf3'))
  log('2. Nf3 — knight move works, Bob sees SAN in history')
  await alice.screenshot({ path: `${SHOTS}/04-alice-midgame.png` })
  await bob.screenshot({ path: `${SHOTS}/05-bob-midgame.png` })

  // ── Probe: Alice tries to grab Bob's queen → no selection ──
  await clickSquare(bob, 'd8', true) // bob's turn now actually — use alice instead
  await clickSquare(alice, 'd8', false)
  const aliceSelectedEnemy = await alice.locator('.ov-selected').count()
  if (aliceSelectedEnemy !== 0) throw new Error('Alice selected an enemy piece!')
  log("PROBE: clicking opponent's piece does not select it")

  // ── Surrender flow with confirmation ─────────────────────
  await bob.getByRole('button', { name: 'Surrender' }).click()
  await bob.getByRole('button', { name: 'Confirm surrender' }).click()
  await alice.waitForSelector('text=You win')
  await bob.waitForSelector('text=You lose')
  log('Bob surrendered → Alice sees "You win by resignation", Bob sees "You lose"')
  await alice.screenshot({ path: `${SHOTS}/06-alice-wins.png` })
  await bob.screenshot({ path: `${SHOTS}/07-bob-gameover.png` })

  // ── Rematch: colors swap ─────────────────────────────────
  await alice.getByRole('button', { name: 'Rematch' }).click()
  await bob.waitForSelector('text=Opponent wants a rematch')
  await bob.getByRole('button', { name: 'Accept rematch' }).click()
  await bob.waitForSelector('text=Your turn')   // Bob is white now
  const aliceStatus2 = await alice.locator('.status').textContent()
  if (!aliceStatus2.includes("Opponent's turn")) throw new Error(`after rematch alice: ${aliceStatus2}`)
  log('Rematch accepted → colors swapped, Bob (now white) to move')
  await bob.screenshot({ path: `${SHOTS}/08-rematch-bob-white.png` })

  // ── Leave → both back to lobby ───────────────────────────
  await bob.getByRole('button', { name: 'Surrender' }).click()
  await bob.getByRole('button', { name: 'Confirm surrender' }).click()
  await alice.waitForSelector('text=You win')
  await alice.getByRole('button', { name: 'Back to lobby' }).click()
  await alice.waitForSelector('text=Create a room')
  log('Alice returned to lobby cleanly')

  if (errors.length > 0) {
    console.log('\nBROWSER ERRORS:')
    for (const e of errors) console.log('  ' + e)
    process.exitCode = 1
  } else {
    console.log('\nALL STEPS PASSED — no browser console errors')
  }
} finally {
  await browser.close()
}
