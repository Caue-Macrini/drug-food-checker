"""Build query indexes without discarding any source rows or changing source tables."""
import argparse, json, sqlite3, time
from pathlib import Path
from foodrugs_full import norm

# Search-only Portuguese translations, matched exactly against the original English terms.
# They only help users find a term; the original FooDrugs names are never rewritten.
DRUG_LABELS={'cafeína':'caffeine','teofilina':'theophylline','omeprazol':'omeprazole','paracetamol':'acetaminophen',
    'ibuprofeno':'ibuprofen','aspirina':'aspirin','ácido acetilsalicílico':'aspirin','amiodarona':'amiodarone',
    'tacrolimo':'tacrolimus','ciclosporina':'cyclosporine','atorvastatina':'atorvastatin','sinvastatina':'simvastatin',
    'lovastatina':'lovastatin','felodipino':'felodipine','nifedipino':'nifedipine','anlodipino':'amlodipine',
    'fenelzina':'phenelzine','lítio':'lithium','digoxina':'digoxin','metronidazol':'metronidazole',
    'tetraciclina':'tetracycline','doxiciclina':'doxycycline','alendronato':'alendronate','levotiroxina':'levothyroxine',
    'varfarina':'warfarin','metformina':'metformin','ciprofloxacino':'ciprofloxacin','clopidogrel':'clopidogrel',
    'sildenafila':'sildenafil','midazolam':'midazolam','carbamazepina':'carbamazepine','fenitoína':'phenytoin',
    'colchicina':'colchicine','buspirona':'buspirone','espironolactona':'spironolactone','captopril':'captopril',
    'enalapril':'enalapril','losartana':'losartan','isoniazida':'isoniazid','metotrexato':'methotrexate'}
FOOD_LABELS={'toranja':'grapefruit','suco de toranja':'grapefruit juice','leite':'milk','soja':'soy','café':'coffee',
    'chá':'tea','chá verde':'green tea','álcool':'alcohol','bebidas alcoólicas':'alcohol','etanol':'ethanol',
    'vinho':'wine','vinho tinto':'red wine','cerveja':'beer','cálcio':'calcium','ferro':'iron','potássio':'potassium',
    'magnésio':'magnesium','zinco':'zinc','sal':'salt','sódio':'sodium','suco de laranja':'orange juice',
    'suco de maçã':'apple juice','suco':'juice','fibras':'fiber','nozes':'walnuts','queijo':'cheese',
    'vitamina K':'vitamin k','iogurte':'yogurt','alho':'garlic','gengibre':'ginger','cúrcuma':'turmeric',
    'curcumina':'curcumin','oxicoco':'cranberry','suco de oxicoco':'cranberry juice','tiramina':'tyramine',
    'espinafre':'spinach','brócolis':'broccoli','romã':'pomegranate','alcaçuz':'licorice','chocolate':'chocolate',
    'banana':'banana','mel':'honey','teofilina':'theophylline','cafeína':'caffeine','alimento':'food','refeição':'meal'}

def add_translations(c):
    added=0
    for kind,table,labels in (('d','_drugs',DRUG_LABELS),('f','_foods',FOOD_LABELS)):
        for label,term in labels.items():
            entity=c.execute(f'SELECT id FROM {table} WHERE norm=? ORDER BY occurrences DESC LIMIT 1',(norm(term),)).fetchone()
            if entity:added+=c.execute('INSERT OR IGNORE INTO _aliases VALUES (?,?,?,?)',(kind,norm(label),label,entity[0])).rowcount
    return added

def index(path):
    c=sqlite3.connect(path);c.create_function('normalize',1,norm,deterministic=True)
    c.execute('PRAGMA journal_mode=OFF');c.execute('PRAGMA synchronous=OFF');c.execute('PRAGMA cache_size=-100000')
    manifest=json.loads(c.execute("SELECT value FROM _metadata WHERE key='manifest'").fetchone()[0])
    if not manifest['complete']:raise ValueError('Partial source is not accepted')
    if c.execute("SELECT 1 FROM _metadata WHERE key='coverage'").fetchone():raise ValueError('Already indexed')
    for table,schema in manifest['tables'].items():
        for column in schema['columns']:
            if column.lower().endswith('_id'):
                c.execute(f'CREATE INDEX IF NOT EXISTS "idx_{table}_{column}" ON "{table}" ("{column}")')
        c.commit();print('Indexed source table:',table,flush=True)
    for kind,column in [('drugs','drug'),('foods','food')]:
        c.execute(f'CREATE TABLE _{kind} (id INTEGER PRIMARY KEY,name TEXT,norm TEXT UNIQUE,occurrences INTEGER)')
        c.execute(f'''INSERT INTO _{kind}(name,norm,occurrences)
            SELECT min(trim("{column}")),normalize("{column}"),count(*) FROM TM_interactions
            WHERE trim(coalesce("{column}",''))!='' GROUP BY normalize("{column}")''')
        c.execute(f'CREATE INDEX _{kind}_popular ON _{kind}(occurrences DESC,id)')
        c.commit();print('Entity terms:',kind,c.execute(f'SELECT count(*) FROM _{kind}').fetchone()[0],flush=True)
    c.execute('CREATE TABLE _tm(source_id INTEGER PRIMARY KEY,drug_id INTEGER,food_id INTEGER,text_id INTEGER)')
    c.execute('''INSERT INTO _tm SELECT t.TM_interactions_ID,d.id,f.id,t.texts_ID FROM TM_interactions t
        JOIN _drugs d ON d.norm=normalize(t.drug) JOIN _foods f ON f.norm=normalize(t.food)''')
    c.execute('CREATE INDEX _tm_pair ON _tm(drug_id,food_id,source_id)')
    c.execute('CREATE TABLE _pairs(drug_id INTEGER,food_id INTEGER,records INTEGER,PRIMARY KEY(drug_id,food_id))')
    c.execute('INSERT INTO _pairs SELECT drug_id,food_id,count(*) FROM _tm GROUP BY drug_id,food_id')
    c.execute('CREATE INDEX _pairs_food ON _pairs(food_id,drug_id)')
    c.execute('CREATE INDEX _pairs_rank ON _pairs(drug_id,records DESC,food_id)')
    c.execute('CREATE TABLE _aliases(kind TEXT,term TEXT,label TEXT,entity_id INTEGER,PRIMARY KEY(kind,term,entity_id))')
    catalog=Path(__file__).resolve().parents[1]/'data/catalogo-oficial.json'
    for r in json.loads(catalog.read_text(encoding='utf-8'))['rows']:
        # Explicit English labels already present in the source are the bridge.
        for kind,table,name,candidates in [('d','_drugs',r['drug'],r.get('drug_aliases',[])),('f','_foods',r['food'],r.get('food_aliases',[]))]:
            for candidate in candidates:
                entity=c.execute(f'SELECT id FROM {table} WHERE norm=?',(norm(candidate),)).fetchone()
                if entity:c.execute('INSERT OR IGNORE INTO _aliases VALUES (?,?,?,?)',(kind,norm(name),name,entity[0]))
    add_translations(c)
    count=lambda query:c.execute(query).fetchone()[0]
    coverage={'drugs':count('SELECT count(*) FROM _drugs'),'foods':count('SELECT count(*) FROM _foods'),
        'associations':manifest['tables']['TM_interactions']['rows'],'sources':count('SELECT count(DISTINCT texts_ID) FROM TM_interactions'),
        'pairs':count('SELECT count(*) FROM _pairs'),'searchable_records':count('SELECT count(*) FROM _tm'),
        'documents':manifest['tables']['texts']['rows'],'molecular_records':manifest['tables'].get('cmap_foodrugs',{}).get('rows',0),
        'total_rows':sum(t['rows'] for t in manifest['tables'].values()),'tables':len(manifest['tables']),'dataset':'foodrugs-4.0.0-completa'}
    missing=count('SELECT count(*) FROM TM_interactions t WHERE NOT EXISTS (SELECT 1 FROM texts x WHERE x.texts_ID=t.texts_ID)')
    manifest['validation']={'missing_text_references':missing,'indexed_text_records':coverage['searchable_records'],'unsearchable_text_records':coverage['associations']-coverage['searchable_records']}
    c.execute("UPDATE _metadata SET value=? WHERE key='manifest'",(json.dumps(manifest),))
    c.execute('INSERT INTO _metadata VALUES (?,?)',('coverage',json.dumps(coverage)))
    c.commit();c.execute('ANALYZE');c.commit()
    if c.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('Integrity check failed')
    c.close()
    Path(path).with_suffix('.manifest.json').write_text(json.dumps({**manifest,'coverage':coverage},indent=2,ensure_ascii=False),encoding='utf-8')
    print('READY',json.dumps(coverage),flush=True)
    return coverage

def update_translations(path):
    """Add new Portuguese search labels to an installed database without rebuilding it."""
    with sqlite3.connect(path) as c:
        c.create_function('normalize',1,norm,deterministic=True)
        return add_translations(c)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('database');a=p.parse_args();index(a.database)
