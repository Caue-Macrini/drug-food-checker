import { chromium } from '../frontend/node_modules/@playwright/test/index.mjs';
import { readFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = new URL('../', import.meta.url);
const acc = readFileSync(new URL('.local-run/ACESSOS-APRESENTACAO.txt', root), 'utf8');
const block = acc.split('Visitante')[1];
const email = block.match(/E-mail:\s*(\S+)/)[1];
const password = block.match(/Senha:\s*(\S+)/)[1];
const base = process.argv[2] || 'http://127.0.0.1:8000';
const outDir = new URL('capturas-tcc/revisao-2026-11-02/', root);
mkdirSync(outDir, { recursive: true });
const shot = n => fileURLToPath(new URL(n, outDir));

let browser; try { browser = await chromium.launch(); } catch { browser = await chromium.launch({ channel: 'chrome' }); }
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
await page.goto(base, { waitUntil: 'networkidle' });
await page.locator('input[type=email]').first().fill(email);
await page.locator('input[type=password]').first().fill(password);
await page.getByRole('button', { name: /Entrar na minha conta/i }).click();
await page.getByRole('button', { name: 'Consultar interação' }).waitFor();

const j = p => page.evaluate(async p => (await fetch('/api' + p, { credentials: 'same-origin' })).json(), p);
const sim = (await j('/catalog/drugs?q=sinvastatina'))[0];
console.log('busca sinvastatina ->', sim.name, '/', sim.original);
const lib = await j('/library?drug_id=' + encodeURIComponent(sim.id));
const foods = lib.items[0].foods;
console.log('alimentos sugeridos:', foods.slice(0, 12).map(f => `${f.name}(${f.level})`).join(', '));
const zero = foods.find(f => f.level === 0);

async function pick(kind, text) {
  const input = page.locator('#' + kind);
  await input.fill('');
  await page.waitForTimeout(300);
  await input.fill(text);
  const want = new RegExp('^\\s*' + text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
  const opt = page.locator(`#${kind}-options [role=option]`).filter({ hasText: new RegExp(text, 'i') }).first();
  await opt.waitFor({ timeout: 15000 });
  await opt.click();
}
async function consult(drug, food, name) {
  await page.getByRole('button', { name: 'Consultar interação' }).click();
  await pick('drugs', drug);
  await pick('foods', food);
  await page.getByRole('button', { name: /Consultar base/i }).click();
  await page.locator('.result-title h2', { hasText: new RegExp(food, 'i') }).waitFor({ timeout: 20000 });
  await page.waitForTimeout(900);
  const card = page.locator('.verdict').locator('xpath=ancestor::section[1]');
  await card.screenshot({ path: shot(name) });
  const t = await page.locator('.result-title').innerText() + ' || ' + await page.locator('.verdict').innerText();
  console.log(name, '->', t.replace(/\n+/g, ' | ').slice(0, 300));
}
await page.getByRole('button', { name: 'Consultar interação' }).click();
await page.evaluate(() => window.scrollTo(0, 0));
await pick('drugs', 'sinvastatina');
await pick('foods', 'toranja');
await page.locator('h1').click();
await page.waitForTimeout(800);
await page.evaluate(() => window.scrollTo(0, 0));
await page.screenshot({ path: shot('consulta.png') });
console.log('OK');
await browser.close();
