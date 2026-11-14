import { chromium } from '../frontend/node_modules/@playwright/test/index.mjs';
import { readFileSync } from 'node:fs';
const root = new URL('../', import.meta.url);
const base = process.argv[2];
const acc = readFileSync(new URL('.local-run/ACESSOS-APRESENTACAO.txt', root), 'utf8').split('Visitante')[1];
const email = acc.match(/E-mail:\s*(\S+)/)[1], password = acc.match(/Senha:\s*(\S+)/)[1];
let browser; try { browser = await chromium.launch(); } catch { browser = await chromium.launch({ channel: 'chrome' }); }
const page = await browser.newPage();
const t0 = Date.now();
await page.goto(base, { waitUntil: 'networkidle' });
console.log('página carregada em', Date.now() - t0, 'ms |', await page.title());
await page.locator('input[type=email]').first().fill(email);
await page.locator('input[type=password]').first().fill(password);
await page.getByRole('button', { name: /Entrar na minha conta/i }).click();
await page.getByRole('button', { name: 'Consultar interação' }).waitFor({ timeout: 20000 });
console.log('login OK');
async function pick(kind, text) {
  await page.locator('#' + kind).fill(text);
  const opt = page.locator(`#${kind}-options [role=option]`).filter({ hasText: new RegExp(text, 'i') }).first();
  await opt.waitFor({ timeout: 15000 }); await opt.click();
}
await pick('drugs', 'sinvastatina'); await pick('foods', 'toranja');
const t1 = Date.now();
await page.getByRole('button', { name: /Consultar base/i }).click();
await page.locator('.result-title h2', { hasText: /toranja/i }).waitFor({ timeout: 20000 });
console.log('consulta em', Date.now() - t1, 'ms ->', (await page.locator('.result-title').innerText()).replace(/\n+/g, ' | '));
await browser.close();
