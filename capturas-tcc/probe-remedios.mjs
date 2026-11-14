// Exercises "Meus remédios" as the demo visitor and leaves the visitor's list as it was found.
import { chromium } from '../frontend/node_modules/@playwright/test/index.mjs';
import { fileURLToPath } from 'node:url';
const base = process.argv[2] || 'https://drugfood.tail7a6e28.ts.net';
const shot = n => fileURLToPath(new URL('revisao-2026-11-02/' + n, import.meta.url));
let browser; try { browser = await chromium.launch(); } catch { browser = await chromium.launch({ channel: 'chrome' }); }
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
await page.goto(base, { waitUntil: 'networkidle' });
await page.getByRole('button', { name: /Entrar como visitante/i }).click();
await page.getByRole('button', { name: 'Meus remédios' }).click();
await page.getByText('Medicamentos em uso').waitFor();
async function pick(kind, text, expect) {
  await page.locator('#' + kind).fill(text);
  const o = page.locator(`#${kind}-options [role=option]`, { hasText: expect }).first();
  await o.waitFor(); await o.click();
}
for (const [q, name] of [['marevan', 'Varfarina'], ['sinvastatina', 'Sinvastatina'], ['levotiroxina', 'Levotiroxina']]) {
  await pick('drugs', q, name);
  await page.getByRole('button', { name: /^Adicionar/ }).click();
  await page.locator('.med-list li', { hasText: name }).waitFor();
}
await page.locator('.attention-item').first().waitFor();
console.log('atenção:', (await page.locator('.attention-list').innerText()).replace(/\n+/g, ' | ').slice(0, 400));
await pick('foods', 'toranja', 'Toranja');
await page.getByRole('button', { name: /^Conferir/ }).click();
await page.locator('.check-results li').first().waitFor();
console.log('conferência:', (await page.locator('.check-results').innerText()).replace(/\n+/g, ' | ').slice(0, 400));
await page.screenshot({ path: shot('meus-remedios.png'), fullPage: true });
await page.setViewportSize({ width: 390, height: 844 });
await page.waitForTimeout(400);
await page.screenshot({ path: shot('meus-remedios-mobile.png') });
await page.setViewportSize({ width: 1440, height: 1000 });
// restore: remove the three medicines
for (const name of ['Varfarina', 'Sinvastatina', 'Levotiroxina']) {
  await page.getByRole('button', { name: 'Remover ' + name }).click();
  await page.locator('.med-list li', { hasText: name }).waitFor({ state: 'detached' });
}
console.log('lista restaurada:', await page.locator('.med-list li').count());
await browser.close();
