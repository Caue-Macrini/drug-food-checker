import { chromium } from '../frontend/node_modules/@playwright/test/index.mjs';
import { readFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = new URL('../', import.meta.url);
const acc = readFileSync(new URL('.local-run/ACESSOS-APRESENTACAO.txt', root), 'utf8');
const block = acc.split('Visitante')[0];
const email = block.match(/E-mail:\s*(\S+)/)[1];
const password = block.match(/Senha:\s*(\S+)/)[1];
const base = process.argv[2] || 'http://127.0.0.1:8000';
mkdirSync(new URL('capturas-tcc/', root), { recursive: true });

let browser;
try { browser = await chromium.launch(); } catch { browser = await chromium.launch({ channel: 'chrome' }); }
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
await page.goto(base, { waitUntil: 'networkidle' });
await page.locator('input[type=email]').first().fill(email);
await page.locator('input[type=password]').first().fill(password);
await page.getByRole('button', { name: /Entrar na minha conta/i }).click();
await page.waitForTimeout(2500);
await page.screenshot({ path: fileURLToPath(new URL('capturas-tcc/_debug-login.png', root)) });
console.log('apos login:', (await page.locator('body').innerText()).slice(0,300).replace(/\n/g,' | '));
await page.getByRole('button', { name: 'Administração' }).click();
await page.getByText('Auditoria recente').waitFor();
await page.waitForTimeout(800);
const out = new URL('capturas-tcc/figura21-admin-completa.png', root);
await page.screenshot({ path: fileURLToPath(out), fullPage: true });
const txt = await page.locator('main').innerText();
console.log('OK', fileURLToPath(out), '| aviso novo:', txt.includes('instalada pelo instalador local'), '| aviso antigo:', txt.includes('precisam de normalização'));
await browser.close();
