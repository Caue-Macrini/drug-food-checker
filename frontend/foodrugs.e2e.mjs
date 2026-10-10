import {chromium,expect} from '@playwright/test';
const base=process.env.TEST_BASE_URL||'http://127.0.0.1:8000';
const browser=await chromium.launch({channel:'chrome',headless:true});
const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
const email=`foodrugs-${Date.now()}@example.com`,password='FooDrugs-test-2026!';
const button=name=>page.getByRole('button',{name,exact:true});
try{
 const health=await (await context.request.get(base+'/api/health')).json();if(health.datasets[0].version!=='foodrugs-4.0.0-completa')throw Error('Full FooDrugs is not active');
 await page.goto(base);await button('Criar conta gratuita').click();await page.getByLabel('Seu nome',{exact:true}).fill('Demonstração FooDrugs');await page.getByLabel('E-mail',{exact:true}).fill(email);await page.getByLabel('Senha',{exact:true}).fill(password);await page.getByRole('checkbox').check();await button('Criar conta').click();await page.getByRole('heading',{name:'Medicamento e alimento',exact:true}).waitFor();
 await expect(page.locator('.coverage')).toContainText('1.108.429');
 const drugs=await (await context.request.get(base+'/api/catalog/drugs?q=sinvastatina')).json();const foods=await (await context.request.get(base+'/api/catalog/foods?q=toranja')).json();
 await page.locator('#drugs').fill('sinvastatina');await page.getByRole('option',{name:drugs[0].name,exact:true}).click();await page.locator('#foods').fill('toranja');await page.getByRole('option',{name:foods[0].name,exact:true}).click();await button('Consultar base').click();
 await page.getByRole('heading',{name:'Associação textual potencial · requer avaliação'}).waitFor();await button('Evidências').click();await page.getByRole('heading',{name:'Contexto original da extração'}).waitFor();await expect(page.locator('.source-excerpt')).not.toBeEmpty();await page.screenshot({path:'../preview-foodrugs-evidencia.png',fullPage:true});
 const more=button('Carregar mais evidências');if(await more.count()){const before=await page.locator('.result select option').count();await more.click();await expect(page.locator('.result select option')).not.toHaveCount(before);}
 await button('Base de conhecimento').click();await page.getByLabel('Buscar medicamento, alimento ou sinônimo').fill('sinvastatina');await page.locator('.library-drug').first().waitFor();await expect(page.locator('.library-drug').first()).toContainText(/simvastatin/i);const moreFoods=page.getByRole('button',{name:/Carregar mais alimentos/}).first();if(await moreFoods.count()){const n=await page.locator('.food-links button').count();await moreFoods.click();await expect(page.locator('.food-links button')).not.toHaveCount(n);}
 await button('Dados FooDrugs').click();await page.getByRole('heading',{name:'FooDrugs 4.0.0',exact:true}).waitFor();await expect(page.locator('.dataset-facts')).toContainText('26.365.254');await page.getByText('Integridade e contagem por tabela',{exact:true}).click();await expect(page.locator('.import-integrity')).toContainText('3c8f26240dd571ded1e4b100d1dfc9d2');await page.screenshot({path:'../preview-foodrugs-completa.png',fullPage:true});
 await expect(page.locator('nav[aria-label="Páginas moleculares"]')).toBeVisible();await page.getByLabel('Buscar tratamento, composto ou gene').fill('resveratrol');await button('Pesquisar estudos').click();await expect(page.locator('.source-table').first()).toContainText(/resveratrol/i,{timeout:60000});
 await page.getByLabel('Tabela científica').selectOption('texts');await page.getByLabel('Identificador (texts_ID)').fill('0');await button('Buscar identificador').click();await expect(page.locator('.source-table').last().locator('tbody tr')).toHaveCount(1);await expect(page.locator('.source-table').last()).toContainText('document');
 await page.setViewportSize({width:390,height:844});await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'../preview-foodrugs-mobile.png',fullPage:false});if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile overflow');
 await button('Abrir menu').click();await button('Histórico').click();await button('Reabrir').first().click();await page.getByRole('heading',{name:'Associação textual potencial · requer avaliação'}).waitFor();
 if(errors.length)throw Error(errors.join('\n'));
 console.log('PASS: full FooDrugs active; Portuguese alias lookup; original evidence and pagination; catalog; scientific tables; molecular joins/search; history; mobile.');
}finally{await context.request.delete(base+'/api/privacy/account',{data:{password}}).catch(()=>{});await browser.close();}
