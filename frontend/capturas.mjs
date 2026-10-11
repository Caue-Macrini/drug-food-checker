// Gera capturas de tela de resultados de cada cor para o documento do TCC.
// Requer a aplicação na porta 8000 com a FooDrugs completa ativa e o Google Chrome.
// Uso: cd frontend; node capturas.mjs   (as imagens vão para ../capturas-tcc/)
import {chromium} from '@playwright/test';
import {mkdirSync} from 'node:fs';
const base=process.env.TEST_BASE_URL||'http://127.0.0.1:8000';
const out='../capturas-tcc';mkdirSync(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});
const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
const button=name=>page.getByRole('button',{name,exact:true});
const email=`capturas-${Date.now()}@example.com`,password=`Capturas-${Date.now()}!`;
async function consult(drug,food,file){
 const [d,f]=await Promise.all([context.request.get(base+'/api/catalog/drugs?q='+encodeURIComponent(drug)).then(r=>r.json()),context.request.get(base+'/api/catalog/foods?q='+encodeURIComponent(food)).then(r=>r.json())]);
 await button('Consultar interação').first().click().catch(()=>{});
 if(await button('Limpar campos').count())await button('Limpar campos').click();
 await page.locator('#drugs').fill(drug);await page.getByRole('option',{name:d[0].name,exact:true}).click();
 await page.locator('#foods').fill(food);await page.getByRole('option',{name:f[0].name,exact:true}).click();
 await button('Consultar base').click();await page.locator('.verdict h3').waitFor();
 await page.locator('.result').screenshot({path:`${out}/${file}-resultado.png`});
 if(await button('Evidências').count()){await button('Evidências').click();await page.locator('.source-excerpt').waitFor();
  await page.locator('.result').screenshot({path:`${out}/${file}-evidencias.png`});await button('Resumo').click();}
 return (await page.locator('.verdict h3').textContent()).trim();
}
try{
 await page.goto(base);
 // A conta de captura é removida ao final, mesmo se uma etapa falhar (bloco finally).
 await button('Criar conta gratuita').click();
 await page.getByLabel('Seu nome',{exact:true}).fill('Capturas TCC');await page.getByLabel('E-mail',{exact:true}).fill(email);
 await page.getByLabel('Senha',{exact:true}).fill(password);await page.getByRole('checkbox').check();await button('Criar conta').click();
 await page.getByRole('heading',{name:'Medicamento e alimento',exact:true}).waitFor();
 const shots=[['sinvastatina','toranja','1-vermelho-sinvastatina-toranja'],['cafeína','teofilina','2-amarelo-cafeina-teofilina'],
  ['omeprazol','leite','3-verde-omeprazol-leite'],['levotiroxina','soja','4-verde-sem-registro-levotiroxina-soja']];
 for(const [d,f,file] of shots)console.log(file,'→',await consult(d,f,file));
 // Perfil clínico: idade 70 e 3 medicamentos → varfarina + vitamina K passa de amarelo a vermelho.
 const profile=await context.request.put(base+'/api/profile',{headers:{'Content-Type':'application/json',Origin:base},data:{age:70,medications:['Varfarina','Losartana','Metformina']}});
 if(!profile.ok())throw Error('Perfil não salvo: '+profile.status()+' '+await profile.text());
 await page.reload();await page.getByRole('heading',{name:'Medicamento e alimento',exact:true}).waitFor();
 console.log('5-perfil-varfarina-vitamina-k →',await consult('varfarina','vitamina K','5-perfil-varfarina-vitamina-k'));
 await page.setViewportSize({width:390,height:844});await button('Resumo').click();
 await page.locator('.result').screenshot({path:`${out}/6-celular-varfarina-vitamina-k.png`});
 if(errors.length)throw Error(errors.join('\n'));
 }finally{
 const del=await context.request.delete(base+'/api/privacy/account',{headers:{'Content-Type':'application/json',Origin:base},data:{password}}).catch(()=>null);
 console.log('conta de captura removida:',!!del?.ok());
 await browser.close()}
