import {chromium,expect} from '@playwright/test';
import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root=new URL('../',import.meta.url);
const base=process.env.TEST_BASE_URL||'http://127.0.0.1:8000';
const browser=await chromium.launch({channel:'chrome',headless:true});
const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
const password='Catalogo-teste-2026!';const email=`catalog-${Date.now()}@example.com`;
const screenshot=async name=>page.screenshot({path:fileURLToPath(new URL('preview-'+name,root)),fullPage:true});
const button=name=>page.getByRole('button',{name,exact:true});
try{
 await page.goto(base);await button('Criar conta gratuita').click();await page.getByLabel('Seu nome',{exact:true}).fill('Consulta de apresentação');await page.getByLabel('E-mail',{exact:true}).fill(email);await page.getByLabel('Senha',{exact:true}).fill(password);await page.getByRole('checkbox').check();await button('Criar conta').click();await page.getByRole('heading',{name:'Medicamento e alimento',exact:true}).waitFor();
 await expect(page.locator('.coverage')).toContainText('25');await expect(page.locator('.coverage')).toContainText('49');
 await page.locator('#drugs').fill('levot');await page.getByRole('option',{name:'Levotiroxina',exact:true}).click();await expect(page.locator('.related-foods')).toContainText('Soja');await button('Soja').click();await expect(page.locator('#foods')).toHaveValue('Soja');await screenshot('consulta-catalogo-atual.png');
 await button('Consultar base').click();await expect(page.locator('.result')).toContainText('Esses alimentos podem interferir');await expect(page.locator('.provenance')).toContainText('08/10/2026');
 await button('Base de conhecimento').click();await page.getByRole('heading',{name:'Base de conhecimento',exact:true}).waitFor();await expect(page.locator('.library-drug')).toHaveCount(12);await screenshot('base-conhecimento-atual.png');
 await button('Próxima').click();await expect(page.locator('.library-pagination')).toContainText('Página 2 de 3');await expect(page.locator('.library-drug')).toHaveCount(12);await button('Próxima').click();await expect(page.locator('.library-drug')).toHaveCount(1);await expect(page.locator('.library-drug')).toContainText('Varfarina');
 const search=page.getByLabel('Buscar medicamento, alimento ou sinônimo');await search.fill('leite');await expect(page.locator('.library-drug')).toHaveCount(1);await button('Consultar Ciprofloxacino com Leite').click();await expect(page.locator('.result')).toContainText('A fonte permite uma refeição');await screenshot('resultado-fonte-atual.png');
 await button('Grafo de conhecimento').click();await page.locator('.graph canvas').first().waitFor();await expect(page.locator('.graph-accessible')).toContainText('Fonte');
 await search.fill('qzxzzzz-inexistente');await page.getByRole('heading',{name:'Nenhum registro com esse termo'}).waitFor();await button('Ver toda a base').click();await expect(page.locator('.library-drug')).toHaveCount(12);
 await page.setViewportSize({width:390,height:844});await page.evaluate(()=>window.scrollTo(0,0));await screenshot('base-conhecimento-mobile.png');if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Overflow mobile no catálogo');
 await button('Abrir menu').click();await button('Histórico').click();await button('Reabrir').first().click();await expect(page.locator('.result')).toContainText('Ciprofloxacino');
 const cookie=(await context.cookies()).find(c=>c.name==='dfc_session');if(!cookie?.httpOnly||(base.startsWith('https://')&&!cookie?.secure))throw Error('Cookie sem proteção HTTPS');
 if(errors.length)throw Error(errors.join('\n'));
 console.log('PASS público: 25 medicamentos, 49 associações, sugestões por medicamento, consulta, fonte/data/orientação, catálogo completo paginado, busca por alimento, ausência de resultados, grafo, histórico, mobile e cookie HTTPS.');
}finally{await context.request.delete(base+'/api/privacy/account',{data:{password}}).catch(()=>{});await browser.close();}
