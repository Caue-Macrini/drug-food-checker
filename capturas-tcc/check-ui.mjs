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
await consult('sinvastatina', 'toranja', 'resultado-vermelho.png');
await page.getByRole('button', { name: 'Evidências' }).click(); await page.waitForTimeout(600);
await page.locator('.verdict').locator('xpath=ancestor::section[1]').screenshot({ path: shot('evidencias.png') });
await page.getByRole('button', { name: 'Grafo de conhecimento' }).click(); await page.waitForTimeout(1500);
await page.locator('.graph').locator('xpath=ancestor::section[1]').screenshot({ path: shot('grafo.png') });
if (zero) await consult('sinvastatina', zero.name, 'resultado-cinza.png');
await consult('sinvastatina', 'morango', 'resultado-sem-registro.png').catch(async e => {
  console.log('morango falhou, tentando tâmara', e.message.slice(0, 80));
  await consult('sinvastatina', 'tâmara', 'resultado-sem-registro.png');
});
await page.getByRole('button', { name: 'Consultar interação' }).click();
await page.locator('#drugs').fill('sinvastatina');
await page.locator('#drugs-options [role=option]').filter({ hasText: /sinvastatina/i }).first().waitFor();
await page.screenshot({ path: shot('consulta-autocompletar.png') });
await page.getByRole('button', { name: 'Dados FooDrugs' }).click(); await page.waitForTimeout(2500);
await page.screenshot({ path: shot('dados-foodrugs.png'), fullPage: true });
await page.getByRole('button', { name: 'Histórico' }).click(); await page.waitForTimeout(1200);
await page.screenshot({ path: shot('historico.png') });
await page.setViewportSize({ width: 390, height: 844 });
await page.getByRole('button', { name: /Abrir menu/i }).click().catch(() => {});
await page.getByRole('button', { name: 'Consultar interação' }).click();
await pick('drugs', 'sinvastatina'); await pick('foods', 'toranja');
await page.getByRole('button', { name: /Consultar base/i }).click();
await page.locator('.result-title h2', { hasText: /toranja/i }).waitFor({ timeout: 20000 }); await page.waitForTimeout(800);
await page.locator('.verdict').scrollIntoViewIfNeeded();
await page.screenshot({ path: shot('mobile.png') });
console.log('OK');
await browser.close();
