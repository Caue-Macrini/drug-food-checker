import React, {useEffect, useState, useRef} from 'react';
import {BookOpen, Search, ArrowRight, ChevronRight, ChevronLeft, Pill} from 'lucide-react';

const num=n=>new Intl.NumberFormat('pt-BR').format(n||0);
const associations=n=>`${n} ${n===1?'associação disponível':'associações disponíveis'}`;

export function Coverage({counts, onBrowse}) {
 return <section className="coverage" aria-label="Cobertura da base ativa">
  <div><BookOpen size={19}/><strong>Base disponível</strong></div>
  {counts ? <p><b>{num(counts.drugs)}</b> {counts.dataset?'termos de medicamentos':'medicamentos'} <span>·</span> <b>{num(counts.foods)}</b> {counts.dataset?'termos alimentares/bioativos':'alimentos e bebidas'} <span>·</span> <b>{num(counts.associations)}</b> {counts.dataset?'registros textuais':'associações'} <span>·</span> <b>{num(counts.sources)}</b> {counts.dataset?'documentos associados':'referências'}</p> : <p>Consultando cobertura…</p>}
  {onBrowse&&<button className="text-button" onClick={onBrowse}>Explorar base <ArrowRight size={16}/></button>}
 </section>
}

export default function Library({api, notify, Result}) {
 const [query,setQuery]=useState(''),[offset,setOffset]=useState(0),[data,setData]=useState(null),[loading,setLoading]=useState(true),[error,setError]=useState(''),[result,setResult]=useState(null),[busy,setBusy]=useState(false),[extraFoods,setExtraFoods]=useState({});
 const resultRef=useRef();
 async function loadFoods(drug){setBusy(true);try{const loaded=extraFoods[drug.id]||drug.foods;const next=await api('/foodrugs/foods?drug_id='+encodeURIComponent(drug.id)+'&offset='+loaded.length);setExtraFoods(old=>({...old,[drug.id]:[...loaded,...next.items]}))}catch(e){notify(e.message)}finally{setBusy(false)}}
 useEffect(()=>{
  let current=true;setLoading(true);setError('');
  const timer=setTimeout(()=>api('/library?q='+encodeURIComponent(query)+'&offset='+offset).then(d=>{if(current)setData(d)}).catch(e=>{if(current)setError(e.message)}).finally(()=>{if(current)setLoading(false)}),200);
  return()=>{current=false;clearTimeout(timer)};
 },[query,offset]);
 async function consult(drug,food){
  setBusy(true);
  try {const r=await api('/check',{method:'POST',body:{drug_id:drug.id,food_id:food.id,personalize:false}});setResult(r);setTimeout(()=>resultRef.current?.scrollIntoView({behavior:'smooth',block:'start'}),80)}
  catch(e){notify(e.message)}finally{setBusy(false)}
 }
 return <>
  <header className="page-heading"><div><span className="eyebrow">CATÁLOGO E PROCEDÊNCIA</span><h1>Base de conhecimento</h1><p>Explore as associações cadastradas. Cada consulta apresenta a referência original.</p></div></header>
  <Coverage counts={data?.counts}/>
  <section className="card library-intro"><label htmlFor="library-search">Buscar medicamento, alimento ou sinônimo</label><div className="input-icon"><Search size={20}/><input id="library-search" type="search" value={query} maxLength={100} placeholder="Ex.: losartana, leite, soja, álcool…" onChange={e=>{setQuery(e.target.value);setOffset(0)}}/></div><p>Selecione um alimento abaixo do medicamento para consultar e salvar o resultado. Nesta tela, a consulta usa somente os dados da base, sem ajustes do perfil.</p><p className="inline-note">{data?.dataset?'FooDrugs completa: termos originais da extração automática, incluindo possíveis erros. Os registros não equivalem a interações clínicas confirmadas. Dados moleculares e documentos estão em Dados FooDrugs.':'As orientações resumem as fontes. A cobertura é limitada e não representa todos os medicamentos ou todas as interações existentes.'}</p></section>
  <div className="section-heading"><h2>{query?'Resultados da busca':data?.dataset?'Termos da FooDrugs':'Medicamentos cadastrados'}</h2><span className="muted" aria-live="polite">{loading?'Buscando…':data?`${data.total} ${data.total===1?'medicamento':'medicamentos'}`:''}</span></div>
  {error?<div className="error" role="alert">{error}</div>:loading?<div className="empty-inline" role="status">Carregando catálogo…</div>:data?.items.length?<div className="library-grid">{data.items.map(drug=><article className="card library-drug" key={drug.id}><div className="title-with-icon"><span className="soft-icon small"><Pill size={18}/></span><div><h3>{drug.name}</h3><small>{associations(drug.food_total||drug.foods.length)}</small></div></div><p className="library-aliases">{drug.aliases.length?'Também encontrado por: '+drug.aliases.join(', '):'Nome do princípio ativo'}</p><div className="food-links">{(extraFoods[drug.id]||drug.foods).map(food=><button disabled={busy} key={food.id} onClick={()=>consult(drug,food)} aria-label={`Consultar ${drug.name} com ${food.name}`}><span>{food.name}</span><ChevronRight size={16}/></button>)}</div>{drug.food_total>(extraFoods[drug.id]||drug.foods).length&&<button className="text-button load-foods" disabled={busy} onClick={()=>loadFoods(drug)}>Carregar mais alimentos ({(extraFoods[drug.id]||drug.foods).length}/{drug.food_total})</button>}</article>)}</div>:<div className="card empty-inline"><BookOpen/><h3>Nenhum registro com esse termo</h3><p>Tente o nome do princípio ativo ou um alimento. Um item ausente não significa que seja seguro.</p><button className="text-button" onClick={()=>{setQuery('');setOffset(0)}}>Ver toda a base</button></div>}
  {!loading&&!error&&data?.total>12&&<nav className="library-pagination" aria-label="Páginas do catálogo"><button className="button secondary" disabled={offset===0} onClick={()=>setOffset(Math.max(0,offset-12))}><ChevronLeft size={16}/>Anterior</button><span>Página {Math.floor(offset/12)+1} de {Math.ceil(data.total/12)}</span><button className="button secondary" disabled={offset+12>=data.total} onClick={()=>setOffset(offset+12)}>Próxima<ChevronRight size={16}/></button></nav>}
  <div ref={resultRef}>{result&&<Result key={result.history_id} result={result} onClose={()=>setResult(null)}/>}</div>
 </>
}
