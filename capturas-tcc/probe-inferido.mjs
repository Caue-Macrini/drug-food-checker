import { chromium } from '../frontend/node_modules/@playwright/test/index.mjs';
import { fileURLToPath } from 'node:url';
const base = process.argv[2] || 'https://drugfood.tail7a6e28.ts.net';
let browser; try { browser = await chromium.launch(); } catch { browser = await chromium.launch({ channel: 'chrome' }); }
const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 });
await page.goto(base, { waitUntil: 'networkidle' });
await page.getByRole('button', { name: /Entrar como visitante/i }).click();
await page.getByRole('button', { name: 'Consultar interação' }).first().waitFor();
async function pick(kind, text, expect) {
  await page.locator('#' + kind).fill(text);
  const o = page.locator(`#${kind}-options [role=option]`, { hasText: expect }).first();
  await o.waitFor(); await o.click();
}
await pick('drugs', 'varfarina', 'Varfarina');
await pick('foods', 'espinafre', 'Espinafre');
await page.getByRole('button', { name: /Consultar base/i }).click();
await page.locator('.inferred-note').waitFor();
const card = page.locator('.verdict').locator('xpath=ancestor::section[1]');
await card.screenshot({ path: fileURLToPath(new URL('revisao-2026-11-02/resultado-inferido.png', import.meta.url)) });
console.log((await page.locator('.verdict').innerText()).replace(/\n+/g, ' | '));
console.log((await page.locator('.inferred-note').innerText()));
await browser.close();
