"""Read-only queries over the complete FooDrugs database and its derived indexes."""
import json, os, sqlite3
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import quote
from foodrugs_full import norm

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
    rows=c.execute('SELECT f.id,f.name,p.records FROM _pairs p JOIN _foods f ON f.id=p.food_id WHERE p.drug_id=? ORDER BY p.records DESC,f.id LIMIT ? OFFSET ?',(drug_id,limit,offset)).fetchall()
    total=c.execute('SELECT count(*) FROM _pairs WHERE drug_id=?',(drug_id,)).fetchone()[0]
    return {'items':[{'id':f'fd:f:{r["id"]}','name':r['name'],'records':r['records']} for r in rows],'total':total,'offset':offset,'limit':limit}

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

def evidence(drug_id,food_id,offset=0,limit=20):
    d=entity_id(drug_id,'d');f=entity_id(food_id,'f')
    with connection() as c:
        drug=c.execute('SELECT name FROM _drugs WHERE id=?',(d,)).fetchone();food=c.execute('SELECT name FROM _foods WHERE id=?',(f,)).fetchone()
        if not drug or not food:raise ValueError('Termo não encontrado')
        total=c.execute('SELECT records FROM _pairs WHERE drug_id=? AND food_id=?',(d,f)).fetchone()
        rows=c.execute('SELECT t.* FROM _tm t WHERE drug_id=? AND food_id=? ORDER BY source_id LIMIT ? OFFSET ?',(d,f,limit,offset)).fetchall()
        records=[]
        for r in rows:
            raw=c.execute('SELECT * FROM TM_interactions WHERE TM_interactions_ID=?',(r['source_id'],)).fetchone()
            doc=c.execute('SELECT * FROM texts WHERE texts_ID=?',(r['text_id'],)).fetchone();doc=dict(doc) if doc else {}
            content=next((str(doc[k]) for k in ('text','content','abstract','document') if doc.get(k)), '')
            start=raw['start_index'] or 0;end=raw['end_index'] or start+600
            snippet=content[max(0,start):min(len(content),start+min(max(end-start,1),600))]
            records.append({'id':f'fd:tm:{r["source_id"]}','source_record_id':str(r['source_id']),'source_text_id':str(r['text_id']),
                'drug':drug[0],'food':food[0],'base_risk':None,'adjusted_risk':None,'reviewed':False,'risk_basis':'','modifiers':[],
                'evidence_status':'Associação textual potencial; extração automática da FooDrugs, sem validação clínica independente.',
                'mechanism':'Não estabelecido pelo registro de mineração de texto.','compound':'Não especificado na fonte',
                'interaction_type':'Mineração de texto (FooDrugs)',
                'explanation':'A FooDrugs registrou estes termos em um contexto textual. A extração pode conter erros e não confirma, por si só, uma interação clínica.',
                'recommendation':'Examine o documento original com um profissional; este registro não recomenda mudanças no tratamento.',
                'guidance':'Requer avaliação da evidência','reference_title':f'FooDrugs · registro {r["source_id"]} · documento {r["text_id"]}',
                'reference_url':source_url(doc),'source':'FooDrugs 4.0.0 · IMDEA Food Institute · CC BY 4.0','version':VERSION,
                'source_excerpt':snippet,'citation':str(doc.get('citation') or ''),'source_document':{k:str(v)[:600] for k,v in doc.items() if v is not None and k not in ('text','content','abstract','document')}})
        return {'drug':drug[0],'food':food[0],'drug_id':drug_id,'food_id':food_id,'found':bool(total),'risk':None,'unclassified':bool(total),'evidence':records,
            'evidence_total':total[0] if total else 0,'evidence_offset':offset,'dataset':VERSION,'personalized':False,
            'heuristic':'Escores de transcriptômica e extrações textuais não são convertidos em risco clínico.',
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
