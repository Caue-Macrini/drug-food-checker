"""Read-only queries over the complete FooDrugs database and its derived indexes."""
import json, os, sqlite3
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import quote
from foodrugs_full import norm
from services import adjusted_risk
import risk_rules as R

VERSION='foodrugs-4.0.0-completa'
PATH=Path(os.getenv('FOODRUGS_DB',str(Path(__file__).resolve().parents[1]/'.local-data/foodrugs-v4.sqlite')))
@contextmanager
def connection():
    c=sqlite3.connect(PATH.resolve().as_uri()+'?mode=ro',uri=True,timeout=30)
    c.row_factory=sqlite3.Row
    try:yield c
    finally:c.close()

def metadata():
    with connection() as c:return json.loads(c.execute("SELECT value FROM _metadata WHERE key='manifest'").fetchone()[0])
def coverage():
    with connection() as c:return json.loads(c.execute("SELECT value FROM _metadata WHERE key='coverage'").fetchone()[0])

def entity_id(value,kind):
    prefix='fd:'+kind+':'
    if not value.startswith(prefix) or not value[len(prefix):].isdigit():raise ValueError('Identificador FooDrugs inválido')
    return int(value[len(prefix):])

def search(kind,term):
    table='_drugs' if kind=='d' else '_foods';q=norm(term)
    with connection() as c:
        if not q:rows=c.execute(f'SELECT * FROM {table} ORDER BY occurrences DESC,id LIMIT 12').fetchall()
        else:
            rows=c.execute(f'''SELECT DISTINCT e.* FROM {table} e WHERE e.norm=? OR e.id IN
                (SELECT entity_id FROM _aliases WHERE kind=? AND term=?) ORDER BY e.occurrences DESC LIMIT 12''',(q,kind,q)).fetchall()
            if len(rows)<12:
                extra=c.execute(f'''SELECT * FROM {table} WHERE norm>=? AND norm<?
                    ORDER BY occurrences DESC LIMIT 24''',(q,q+'\uffff')).fetchall()
                known={r['id'] for r in rows};rows=list(rows)+[r for r in extra if r['id'] not in known]
            if not rows:
                # Parameterized substring fallback; original entity terms are never rewritten.
                rows=c.execute(f'SELECT * FROM {table} WHERE instr(norm,?)>0 ORDER BY occurrences DESC LIMIT 12',(q,)).fetchall()
        return [{'id':f'fd:{kind}:{r["id"]}','name':r['name'],'score':100 if r['norm']==q else 90} for r in rows[:12]]

def foods(c,drug_id,offset=0,limit=12):
    level='r.level' if has_rules(c) else 'NULL'
    join=' LEFT JOIN _pair_risk r ON r.drug_id=p.drug_id AND r.food_id=p.food_id' if has_rules(c) else ''
    rows=c.execute(f'SELECT f.id,f.name,p.records,{level} AS level FROM _pairs p JOIN _foods f ON f.id=p.food_id{join} WHERE p.drug_id=? ORDER BY p.records DESC,f.id LIMIT ? OFFSET ?',(drug_id,limit,offset)).fetchall()
    total=c.execute('SELECT count(*) FROM _pairs WHERE drug_id=?',(drug_id,)).fetchone()[0]
    return {'items':[{'id':f'fd:f:{r["id"]}','name':r['name'],'records':r['records'],'level':r['level']} for r in rows],'total':total,'offset':offset,'limit':limit}

def library(term='',drug_id=None,offset=0,limit=12):
    q=norm(term)
    with connection() as c:
        condition='1=1';params=[]
        if drug_id:condition='d.id=?';params=[entity_id(drug_id,'d')]
        elif q:
            condition='''(instr(d.norm,?)>0 OR d.id IN (SELECT entity_id FROM _aliases WHERE kind='d' AND instr(term,?)>0)
                OR d.id IN (SELECT p.drug_id FROM _pairs p WHERE p.food_id IN
                (SELECT id FROM _foods WHERE instr(norm,?)>0 UNION SELECT entity_id FROM _aliases WHERE kind='f' AND instr(term,?)>0)))''';params=[q]*4
        total=c.execute('SELECT count(*) FROM _drugs d WHERE '+condition,params).fetchone()[0]
        rows=c.execute('SELECT d.* FROM _drugs d WHERE '+condition+' ORDER BY d.occurrences DESC,d.id LIMIT ? OFFSET ?',[*params,limit,offset]).fetchall()
        items=[]
        for r in rows:
            f=foods(c,r['id'])
            aliases=[a[0] for a in c.execute("SELECT label FROM _aliases WHERE kind='d' AND entity_id=? LIMIT 10",(r['id'],))]
            items.append({'id':f'fd:d:{r["id"]}','name':r['name'],'aliases':aliases,'foods':f['items'],'food_total':f['total'],'records':r['occurrences']})
        counts=json.loads(c.execute("SELECT value FROM _metadata WHERE key='coverage'").fetchone()[0])
        return {'counts':counts,'total':total,'offset':offset,'limit':limit,'items':items,'dataset':VERSION}

def get_foods(drug_id,offset=0):
    with connection() as c:return foods(c,entity_id(drug_id,'d'),offset)

def source_url(row):
    for key in ('url','URL','link','reference_url'):
        v=str(row.get(key) or '')
        if v.startswith('https://'):return v
        if v.startswith('http://'):return 'https://'+v[7:]
    return 'https://doi.org/10.5281/zenodo.8192515'

def has_rules(c):
    """Rules version that produced the derived risk tables, or None when they are not installed."""
    if not c.execute("SELECT 1 FROM sqlite_master WHERE name='_pair_risk'").fetchone():return None
    row=c.execute("SELECT value FROM _metadata WHERE key='risk_rules'").fetchone()
    return json.loads(row[0]).get('rules') if row else None

def pair_stats(c,d,f):
    row=c.execute('SELECT * FROM _pair_risk WHERE drug_id=? AND food_id=?',(d,f)).fetchone()
    if not row:return None
    stats=dict(row)
    # Direction of pharmacokinetic changes, aggregated over the interaction sentences.
    inc,dec=c.execute('''SELECT coalesce(sum(s.flags&64>0),0),coalesce(sum(s.flags&128>0),0) FROM _tm t JOIN _tm_signal s ON s.source_id=t.source_id
        WHERE t.drug_id=? AND t.food_id=? AND s.category=1 AND s.flags&1''',(d,f)).fetchone()
    stats['increase'],stats['decrease']=inc,dec
    return stats

def explain(stats,drug,food):
    """Simplified explanation (RF010) assembled from the mechanisms detected in the sentences."""
    if not stats or not stats['interaction_docs']:return '',[], 'Não identificado'
    codes=[m for m in (stats['mechanisms'] or '').split(',') if m]
    mechanisms=R.mechanism_text(codes)
    parts=[]
    if stats['pk_docs']:
        # The sentences do not say reliably which of the two changes the other, so the text names both.
        if stats['increase']>stats['decrease']:parts.append(f'Os estudos descrevem aumento da concentração no sangue quando {drug} e {food} são usados juntos, o que pode intensificar efeitos, inclusive os colaterais.')
        elif stats['decrease']>stats['increase']:parts.append(f'Os estudos descrevem redução da absorção ou da concentração no sangue quando {drug} e {food} são usados juntos, o que pode diminuir o efeito esperado.')
        else:parts.append(f'Os estudos descrevem que, usados juntos, {drug} e {food} podem alterar a forma como o corpo absorve ou elimina um ao outro.')
    if stats['pd_docs']:parts.append(f'Também há trechos indicando que os efeitos de {drug} e {food} podem se somar ou se opor.')
    if not parts:parts.append(f'Os trechos descrevem uma possível interação entre {drug} e {food}, ou trazem recomendações sobre o uso conjunto.')
    # The type also follows from the mechanism detected (e.g. vitamin K antagonism is pharmacodynamic).
    pk=stats['pk_docs'] or any(m in R.PK_MECHANISMS for m in codes);pd=stats['pd_docs'] or any(m in R.PD_MECHANISMS for m in codes)
    kind=('Farmacocinética e farmacodinâmica' if pk and pd else 'Farmacocinética (absorção, metabolismo ou eliminação)' if pk
        else 'Farmacodinâmica (efeito do medicamento)' if pd else 'Descrita no texto, sem mecanismo identificado')
    return ' '.join(parts),mechanisms,kind

def basis(stats,level,found):
    if not found:return ['Nenhum registro deste par na FooDrugs 4.0.0. Pelo fluxo alternativo do TCC, o resultado é verde, com ressalva.']
    items=[]
    if stats['curated_level'] is not None:
        items.append(f'Uma monografia do Drugs.com incluída na FooDrugs classifica esta interação como {stats["curated_label"]}. Fontes com gravidade explícita têm prioridade.')
    n=lambda v:f'{v:,}'.replace(',','.')
    docs=lambda v:n(v)+(' documento' if v==1 else ' documentos')
    items.append(f'{n(stats["interaction_records"])} de {n(stats["records"])} {"trecho" if stats["records"]==1 else "trechos"} ({docs(stats["interaction_docs"])}) {"descreve" if stats["interaction_records"]==1 else "descrevem"} interação.')
    if stats['strong_docs']:items.append(f'{docs(stats["strong_docs"])} {"traz" if stats["strong_docs"]==1 else "trazem"} aviso forte (evitar, contraindicado ou efeito grave).')
    if stats['no_effect_docs']:items.append(f'{docs(stats["no_effect_docs"])} {"relata" if stats["no_effect_docs"]==1 else "relatam"} ausência de efeito relevante.')
    if stats['curated_level'] is None:
        rule={2:'Regra: 2 ou mais documentos com aviso forte → Risco elevado.',1:'Regra: ao menos 1 documento descreve interação → Atenção.',
              0:'Regra: nenhum documento descreve interação, ou estudos sem efeito são maioria → Sem interação identificada.'}[stats['level']]
        items.append(rule)
    return items

def evidence(drug_id,food_id,offset=0,limit=20,profile=None,personalize=False):
    d=entity_id(drug_id,'d');f=entity_id(food_id,'f')
    with connection() as c:
        drug=c.execute('SELECT name FROM _drugs WHERE id=?',(d,)).fetchone();food=c.execute('SELECT name FROM _foods WHERE id=?',(f,)).fetchone()
        if not drug or not food:raise ValueError('Termo não encontrado')
        total=c.execute('SELECT records FROM _pairs WHERE drug_id=? AND food_id=?',(d,f)).fetchone()
        rules=has_rules(c);stats=pair_stats(c,d,f) if rules and total else None
        if rules and total and stats is None:rules=None  # pair missing from the risk tables: show it unclassified
        if rules:
            rows=c.execute('''SELECT t.*,s.category,s.flags,s.mechanisms AS signal_mechanisms,s.curated,s.curated_label FROM _tm t JOIN _tm_signal s ON s.source_id=t.source_id
                WHERE t.drug_id=? AND t.food_id=? ORDER BY (s.curated IS NOT NULL) DESC,CASE s.category WHEN 1 THEN 0 WHEN 2 THEN 1 ELSE 2 END,(s.flags&8>0) DESC,t.source_id LIMIT ? OFFSET ?''',(d,f,limit,offset)).fetchall()
        else:
            rows=c.execute('SELECT t.*,NULL AS category,0 AS flags,"" AS signal_mechanisms,NULL AS curated,"" AS curated_label FROM _tm t WHERE drug_id=? AND food_id=? ORDER BY source_id LIMIT ? OFFSET ?',(d,f,limit,offset)).fetchall()
        found=bool(total)
        if rules:
            base=stats['level'] if stats else 0
            explanation,mechanisms,kind=explain(stats,drug[0],food[0])
            flags=R.drug_flags(drug[0],(stats or {}).get('mechanisms') or '')
            # TCC p. 21/31: modifiers intensify an identified interaction (base >= 1); they do not
            # create one, so absent pairs and pairs without described interaction stay green.
            level,modifiers=adjusted_risk(base,profile or {},flags) if found and base>=1 else (base,[])
            summary=R.verdict(level,base,found,drug[0],food[0],stats or {})
        else:
            base=level=None;explanation,mechanisms,kind='',[],'Mineração de texto (FooDrugs)';modifiers=[];summary=None
        records=[]
        for r in rows:
            raw=c.execute('SELECT * FROM TM_interactions WHERE TM_interactions_ID=?',(r['source_id'],)).fetchone()
            doc=c.execute('SELECT * FROM texts WHERE texts_ID=?',(r['text_id'],)).fetchone();doc=dict(doc) if doc else {}
            content=next((str(doc[k]) for k in ('text','content','abstract','document') if doc.get(k)), '')
            start=raw['start_index'] or 0;end=raw['end_index'] or start+600
            snippet=content[max(0,start):min(len(content),start+min(max(end-start,1),600))]
            category=r['category'];record_mechanisms=R.mechanism_text([m for m in (r['signal_mechanisms'] or '').split(',') if m])
            records.append({'id':f'fd:tm:{r["source_id"]}','source_record_id':str(r['source_id']),'source_text_id':str(r['text_id']),
                'drug':drug[0],'food':food[0],'base_risk':base,'adjusted_risk':level,'reviewed':False,
                'risk_basis':'Derivado por regras explícitas sobre os trechos da FooDrugs ('+rules+').' if rules else '','modifiers':modifiers,
                'signal':{R.MENTION:'mencao',R.INTERACTION:'interacao',R.NO_EFFECT:'sem_efeito'}.get(category,'nao_classificado'),
                'signal_label':R.SIGNAL_LABELS.get(category,'Não classificado'),'signal_detail':R.signal_detail(category,r['flags'] or 0,r['curated_label'] or '') if category is not None else '',
                'evidence_status':'Trecho extraído automaticamente pela FooDrugs; classificação por regras do sistema, sem validação clínica independente.',
                'mechanism':(record_mechanisms[0][0].upper()+record_mechanisms[0][1:]+'.') if record_mechanisms else 'Não descrito neste trecho.','compound':'Não especificado na fonte',
                'interaction_type':kind,'explanation':explanation or 'A FooDrugs registrou estes termos em um contexto textual.',
                'recommendation':summary['recommendation'] if summary else 'Examine o documento original com um profissional.',
                'guidance':summary['title'] if summary else 'Requer avaliação da evidência','reference_title':f'FooDrugs · registro {r["source_id"]} · documento {r["text_id"]}',
                'reference_url':source_url(doc),'source':'FooDrugs 4.0.0 · IMDEA Food Institute · CC BY 4.0','version':VERSION,
                'source_excerpt':snippet,'citation':str(doc.get('citation') or ''),'source_document':{k:str(v)[:600] for k,v in doc.items() if v is not None and k not in ('text','content','abstract','document')}})
        return {'drug':drug[0],'food':food[0],'drug_id':drug_id,'food_id':food_id,'found':found,'risk':level,'base_risk':base,'unclassified':found and not rules,
            'verdict':summary,'explanation':explanation,'mechanisms':mechanisms,'interaction_type':kind,'basis':(basis(stats,base,found)+([f'Perfil clínico (Tabela 2 do TCC): +{len(modifiers)} → {R.LEVEL_NAMES[level]}.'] if modifiers else [])) if rules else [],
            'strength':R.strength(stats['curated_level'],stats['interaction_docs']) if stats else '','modifiers':modifiers,
            'stats':{k:stats[k] for k in ('records','interaction_records','interaction_docs','strong_docs','no_effect_docs','curated_label')} if stats else None,
            'rules_version':rules,'personalization':{'requested':bool(personalize),'profile_filled':bool(profile)},'evidence':records,
            'evidence_total':total[0] if total else 0,'evidence_offset':offset,'dataset':VERSION,'personalized':bool(modifiers),
            'heuristic':'Classificação derivada por regras explícitas e auditáveis sobre os trechos da FooDrugs (TCC, p. 31). Não é validação clínica.',
            'notice':'Ausência de registro não comprova segurança. Não altere seu tratamento sem orientação profissional.'}

def table_rows(table,offset=0,limit=25,record=None):
    manifest=metadata()
    if table not in manifest['tables']:raise ValueError('Tabela indisponível')
    schema=manifest['tables'][table];columns=schema['columns']
    with connection() as c:
        where='';params=[]
        if record is not None:
            where=' WHERE "'+columns[0]+'"=?';params=[record]
        rows=c.execute('SELECT * FROM "'+table+'"'+where+' LIMIT ? OFFSET ?',[*params,limit,offset]).fetchall()
        total=c.execute('SELECT count(*) FROM "'+table+'"'+where,params).fetchone()[0] if where else schema['rows']
        # The full originals are stored; browser previews bound long document cells.
        return {'table':table,'columns':columns,'total':total,'offset':offset,'limit':limit,
            'rows':[{k:(str(v)[:600]+'…' if isinstance(v,str) and len(v)>600 else v) for k,v in dict(row).items()} for row in rows]}

def molecular(term='',offset=0,limit=20):
    query=norm(term);where='';params=[]
    if query:
        where=''' WHERE (cf.cmap_node_id IN (SELECT cmap_node_id FROM cmap WHERE instr(lower(compound),?)>0)
            OR cf.node_id IN (SELECT n.node_id FROM nodes n JOIN sample s ON s.sample_id=n.sample_id WHERE instr(lower(s.treatment),?)>0))'''
        params=[query,query]
    with connection() as c:
        total=c.execute('SELECT count(*) FROM cmap_foodrugs cf'+where,params).fetchone()[0] if query else metadata()['tables']['cmap_foodrugs']['rows']
        # Limit source edges first, then resolve the experimental context.
        rows=c.execute('''SELECT cf.rowid AS source_row,cf.tau,cf.node_id,cf.cmap_node_id,
            cm.compound,cm.pert_type,cm.cell_line,s.sample_id,s.treatment,s.origin_name,s.time_point,s.concentration,
            st.study_id,st.title,st.accession,st.pubmed_id
            FROM (SELECT rowid,* FROM cmap_foodrugs cf'''+where+''' LIMIT ? OFFSET ?) cf
            LEFT JOIN cmap cm ON cm.cmap_node_id=cf.cmap_node_id
            LEFT JOIN nodes n ON n.node_id=cf.node_id
            LEFT JOIN sample s ON s.sample_id=n.sample_id
            LEFT JOIN study st ON st.study_id=s.study_id''',[*params,limit,offset]).fetchall()
        return {'total':total,'offset':offset,'limit':limit,'rows':[dict(r) for r in rows]}
