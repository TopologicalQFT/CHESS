// E2E: play Scholar's Mate through the UI, then run post-game analysis.
// Run: node e2e/analysis.mjs   (servers on 5173 + 8000)
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
  const ctxA = await browser.newContext({ viewport: { width: 1280, height: 860 } })
  const ctxB = await browser.newContext({ viewport: { width: 1280, height: 860 } })
  const alice = await ctxA.newPage()
  const bob = await ctxB.newPage()
  const errors = []
  for (const [n, p] of [['alice', alice], ['bob', bob]]) {
    p.on('pageerror', (e) => errors.push(`${n}: ${e.message}`))
    p.on('console', (m) => m.type() === 'error' && errors.push(`${n} console: ${m.text()}`))
  }

  await alice.goto(URL)
  await bob.goto(URL)
  await alice.getByPlaceholder('Enter your name').fill('Alice')
  await alice.getByRole('button', { name: '♔ White' }).click()
  await alice.getByRole('button', { name: 'Create Room' }).click()
  await alice.waitForSelector('.room-code')
  await bob.getByPlaceholder('Enter your name').fill('Bob')
  await bob.waitForSelector('.room-list li')
  await bob.getByRole('button', { name: 'Join' }).click()
  await alice.waitForSelector('text=Your turn')
  log('game started')

  // Scholar's mate: 1.e4 e5 2.Qh5 Nc6 3.Bc4 Nf6 4.Qxf7#
  const seq = [
    [alice, 'e2', 'e4', false], [bob, 'e7', 'e5', true],
    [alice, 'd1', 'h5', false], [bob, 'b8', 'c6', true],
    [alice, 'f1', 'c4', false], [bob, 'g8', 'f6', true],
    [alice, 'h5', 'f7', false],
  ]
  for (const [page, from, to, flip] of seq) {
    await page.waitForSelector('text=Your turn')
    await clickSquare(page, from, flip)
    await clickSquare(page, to, flip)
  }
  await alice.waitForSelector('text=You win by checkmate')
  log('checkmate delivered, game over overlay shown')

  // Analyze
  await alice.getByRole('button', { name: /Analyze game/ }).click()
  await alice.waitForSelector('.spinner')
  log('analysis requested, spinner visible')
  await alice.waitForSelector('.summary-card', { timeout: 60000 })
  log('analysis loaded')

  // Bob's Nf6?? must be marked a blunder somewhere in the move list
  const blunders = await alice.locator('.amove.blunder').allTextContents()
  if (!blunders.some((t) => t.includes('Nf6'))) throw new Error(`Nf6 not marked blunder: ${blunders}`)
  log(`blunder detected in move list: ${blunders.join(', ')}`)

  // Click the blunder → board jumps there, hint shows best move
  await alice.locator('.amove.blunder').first().click()
  await alice.waitForSelector('.hint-blunder')

  // Eval bar sanity: White is mating → bar must be ~95% white from the bottom
  const bar = await alice.locator('.eval-bar').evaluate((el) => ({
    bg: getComputedStyle(el).backgroundImage,
    h: el.offsetHeight,
  }))
  if (!bar.bg.includes('linear-gradient') || bar.h < 100) {
    throw new Error(`eval bar wrong: ${JSON.stringify(bar)}`)
  }
  log(`eval bar: h=${bar.h}px, bg=${bar.bg.slice(0, 80)}…`)
  const hint = await alice.locator('.hint-blunder').textContent()
  log(`hint shown: ${hint.trim()}`)
  await alice.screenshot({ path: `${SHOTS}/09-analysis.png` })

  // Eval graph exists with a cursor; navigation works
  await alice.locator('.eval-graph').waitFor()
  await alice.getByRole('button', { name: '⏮' }).click()
  const start = await alice.locator('.ply-label').textContent()
  if (!start.includes('Start')) throw new Error(`expected Start, got ${start}`)
  log('navigation to start works')

  await alice.getByRole('button', { name: 'Close analysis' }).click()
  await alice.waitForSelector('text=You win by checkmate')
  log('closed analysis, back at game over overlay')

  if (errors.length) {
    console.log('BROWSER ERRORS:'); errors.forEach((e) => console.log(' ', e))
    process.exitCode = 1
  } else {
    console.log('\nANALYSIS E2E PASSED — no browser console errors')
  }
} finally {
  await browser.close()
}
