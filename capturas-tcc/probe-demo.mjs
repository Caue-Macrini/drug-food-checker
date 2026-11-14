import { chromium } from '../frontend/node_modules/@playwright/test/index.mjs';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
const root = new URL('../', import.meta.url);
const acc = readFileSync(new URL('.local-run/ACESSOS-APRESENTACAO.txt', root), 'utf8');
const admin = acc.split('Visitante')[0];
const aEmail = admin.match(/E-mail:\s*(\S+)/)[1], aPass = admin.match(/Senha:\s*(\S+)/)[1];
let browser; try { browser = await chromium.launch(); } catch { browser = await chromium.launch({ channel: 'chrome' }); }
for (const base of ['https://drugfood.tail7a6e28.ts.net', 'http://127.0.0.1:8000']) {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  await page.goto(base, { waitUntil: 'networkidle' });
  const body = await page.locator('body').innerText();
  console.log('\n==', base);
  console.log('caixa demo:', body.includes('Ambiente público de demonstração'), '| criar conta visível:', body.includes('Criar conta gratuita'), '| esqueci senha visível:', body.includes('Esqueci minha senha'));
  const r = await page.evaluate(async ([e, p]) => { const x = await fetch('/api/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: e, password: p }) }); return x.status; }, [aEmail, aPass]);
  console.log('login admin ->', r);
  const reg = await page.evaluate(async () => (await fetch('/api/auth/register', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: 'Teste', email: 'x@example.com', password: 'Senha-segura-123', consent: true }) })).status);
  console.log('cadastro ->', reg, '(403 = bloqueado; 201/409 = aberto)');
  if (base.startsWith('https')) {
    await page.screenshot({ path: fileURLToPath(new URL('capturas-tcc/_demo-login.png', root)) });
    await page.getByRole('button', { name: /Entrar como visitante/i }).click();
    await page.getByRole('button', { name: 'Consultar interação' }).waitFor({ timeout: 20000 });
    const t = await page.locator('body').innerText();
    console.log('entrou como visitante | faixa de aviso:', t.includes('conta compartilhada de visitante'), '| menu admin:', t.includes('Administração'));
    await page.screenshot({ path: fileURLToPath(new URL('capturas-tcc/_demo-app.png', root)) });
  }
  await ctx.close();
}
await browser.close();
