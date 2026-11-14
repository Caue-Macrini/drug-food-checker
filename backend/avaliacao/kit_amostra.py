"""Draw the stratified sample of medicine x food pairs for the pharmacist gold-standard evaluation.

Run from backend/:  ..\\.venv\\Scripts\\python.exe avaliacao\\kit_amostra.py [PASTA_SAIDA] [--semente N]
Writes PASTA_SAIDA/amostra_cega.json (what evaluators see) and PASTA_SAIDA/gabarito_sistema.json
(system output, kept away from evaluators). Standard library only.

Strata (realistic universe = common medicine x common food present in the base):
  E2   level 2 (red)                       E1c  level 1 with curated Drugs.com label
  E1t  level 1 from text mining only       E0   level 0 (records exist, no interaction identified)
  CTRL clinically well-known pairs chosen from the literature, sampled whatever the system says
       (absent from the base => system answer "sem registro", counted as negative).
Stratum sizes are stored so the scoring step can weight results back to the universe.
"""
import json, random, sqlite3, sys, datetime
from pathlib import Path
sys.path.insert(0, '.')
import foodrugs_store as store
import pt_names as N
import term_filter as TF
from foodrugs_full import norm

args = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = Path(args[0] if args else 'avaliacao/kit')
SEED = int(sys.argv[sys.argv.index('--semente') + 1]) if '--semente' in sys.argv else 20261114
SIZES = {'E2': 30, 'E1c': 25, 'E1t': 25, 'E0': 30}
LINKS = 3
OUT.mkdir(parents=True, exist_ok=True)
rng = random.Random(SEED)
c = sqlite3.connect(store.PATH.resolve().as_uri() + '?mode=ro', uri=True)

catalog = json.load(open('../data/catalogo-oficial.json', encoding='utf-8'))['rows']
DRUGS = {norm(a) for r in catalog for a in r['drug_aliases']} | {norm(x) for x in (
    'warfarin', 'acenocoumarol', 'simvastatin', 'atorvastatin', 'lovastatin', 'rosuvastatin', 'amlodipine', 'nifedipine',
    'felodipine', 'losartan', 'enalapril', 'captopril', 'spironolactone', 'furosemide', 'hydrochlorothiazide', 'digoxin',
    'metformin', 'glibenclamide', 'insulin glargine', 'levothyroxine', 'omeprazole', 'pantoprazole', 'aspirin', 'ibuprofen',
    'diclofenac', 'naproxen', 'paracetamol', 'acetaminophen', 'dipyrone', 'tramadol', 'codeine', 'amoxicillin',
    'azithromycin', 'clarithromycin', 'ciprofloxacin', 'levofloxacin', 'tetracycline', 'doxycycline', 'metronidazole',
    'tinidazole', 'fluconazole', 'itraconazole', 'ketoconazole', 'isoniazid', 'rifampicin', 'linezolid', 'phenelzine',
    'tranylcypromine', 'selegiline', 'moclobemide', 'sertraline', 'fluoxetine', 'escitalopram', 'amitriptyline',
    'clonazepam', 'diazepam', 'alprazolam', 'zolpidem', 'carbamazepine', 'phenytoin', 'valproic acid', 'lithium',
    'levodopa', 'clozapine', 'quetiapine', 'haloperidol', 'alendronate', 'calcium carbonate', 'ferrous sulfate',
    'prednisone', 'methotrexate', 'tacrolimus', 'cyclosporine', 'sildenafil', 'fexofenadine', 'theophylline', 'caffeine')}
FOODS = {norm(x) for x in (
    'grapefruit', 'grapefruit juice', 'orange juice', 'apple juice', 'cranberry', 'cranberry juice', 'pomegranate',
    'banana', 'spinach', 'broccoli', 'kale', 'cabbage', 'avocado', 'soy', 'soybean', 'garlic', 'ginger', 'turmeric',
    'curcumin', 'licorice', 'ginkgo', 'st. john\'s wort', 'green tea', 'tea', 'coffee', 'caffeine', 'milk', 'yogurt',
    'cheese', 'chocolate', 'honey', 'wine', 'red wine', 'beer', 'alcohol', 'ethanol', 'tyramine', 'vitamin k',
    'calcium', 'iron', 'magnesium', 'zinc', 'potassium', 'sodium', 'salt', 'dietary fiber', 'fiber', 'protein',
    'high-fat meal', 'high fat meal', 'eggs', 'egg', 'fish oil', 'omega-3 fatty acids', 'oat', 'oats', 'wheat bran')}

# Literature controls (expected to be clinically relevant; the evaluators, not this list, decide).
CONTROLS = [('warfarin', 'vitamin k'), ('warfarin', 'spinach'), ('warfarin', 'cranberry juice'), ('warfarin', 'garlic'),
            ('warfarin', 'ginkgo'), ('phenelzine', 'tyramine'), ('phenelzine', 'cheese'), ('linezolid', 'tyramine'),
            ('tetracycline', 'milk'), ('doxycycline', 'calcium'), ('ciprofloxacin', 'milk'), ('ciprofloxacin', 'calcium'),
            ('levothyroxine', 'coffee'), ('levothyroxine', 'soy'), ('simvastatin', 'grapefruit juice'),
            ('felodipine', 'grapefruit juice'), ('nifedipine', 'grapefruit juice'), ('metronidazole', 'alcohol'),
            ('levodopa', 'protein'), ('alendronate', 'coffee'), ('lithium', 'sodium'), ('spironolactone', 'potassium'),
            ('theophylline', 'caffeine'), ('fexofenadine', 'apple juice'), ('isoniazid', 'tyramine')]

hidden_d, hidden_f = TF.hidden('d'), TF.hidden('f')
GENERIC = {norm(x) for x in ('food', 'foods', 'diet', 'diets', 'meal', 'meals', 'fruit', 'fruits', 'beverage', 'beverages',
                              'juice', 'fruit juice', 'vegetables', 'drink', 'drinks', 'nutrition', 'feeding')}
names_d = {i: (name, n) for i, name, n in c.execute('SELECT id, name, norm FROM _drugs')}
names_f = {i: (name, n) for i, name, n in c.execute('SELECT id, name, norm FROM _foods')}
drug_ids = {i: v for i, v in names_d.items() if v[1] in DRUGS and v[1] not in hidden_d}
food_ids = {i: v for i, v in names_f.items() if v[1] in FOODS and v[1] not in hidden_f}
print(f'medicamentos comuns na base: {len(drug_ids)} | alimentos comuns: {len(food_ids)}')

def usable(r):
    """Both terms are real (not hidden by the term filter, not generic, not the same substance)."""
    d, f = names_d[r[0]][1], names_f[r[1]][1]
    return d not in hidden_d and f not in hidden_f and f not in GENERIC and d != f

rows = c.execute('SELECT drug_id, food_id, level, curated_level, curated_label, records FROM _pair_risk').fetchall()
realistic = [r for r in rows if r[0] in drug_ids and r[1] in food_ids]
strata = {'E2': [r for r in rows if r[2] == 2 and usable(r)],
          'E1c': [r for r in rows if r[2] == 1 and r[3] is not None and usable(r)],
          'E1t': [r for r in realistic if r[2] == 1 and r[3] is None],
          'E0': [r for r in realistic if r[2] == 0]}
universe = {(r[0], r[1]) for v in strata.values() for r in v}
drug_ids, food_ids = names_d, names_f
print('universo avaliado:', len(universe), {k: len(v) for k, v in strata.items()})

def links(d, f):
    tids = sorted({r[0] for r in c.execute('SELECT text_id FROM _tm WHERE drug_id=? AND food_id=?', (d, f))})
    out = []
    # Only PubMed articles: Drugs.com/DrugBank pages carry the curated severity and would unblind the evaluator.
    pubmed = [t for t in tids if 'pubmed' in (c.execute('SELECT link FROM texts WHERE texts_ID=?', (t,)).fetchone()[0] or '')]
    for t in rng.sample(pubmed, min(LINKS, len(pubmed))):
        out.append(c.execute('SELECT link FROM texts WHERE texts_ID=?', (t,)).fetchone()[0])
    return out

def resolve(kind, term):
    """Entity a user gets as the first suggestion when typing the term (same search used by the app)."""
    hits = store.search(kind, term)
    return (store.entity_id(hits[0]['id'], kind), hits[0]['original']) if hits else (None, term)

def app_answer(d, f):
    """What the application shows for the pair (synonyms pooled, class/component inference), without profile."""
    if d is None or f is None: return None, None
    r = store.evidence(f'fd:d:{d}', f'fd:f:{f}', limit=1)
    return (r['risk'] if r['found'] else None), r.get('inferred')

def item(d_name, f_name, row, stratum, control, d=None, f=None):
    d, f = (row[0], row[1]) if row is not None else (d, f)
    level_app, inferred = app_answer(d, f)
    return {'drug_en': d_name, 'food_en': f_name, 'stratum': stratum, 'control': control,
            'level_direto': None if row is None else row[2], 'level': level_app, 'inferido': inferred,
            'curated_label': None if row is None else (row[4] or None),
            'records': 0 if row is None else row[5],
            'links': [] if row is None else links(row[0], row[1])}

chosen, seen = [], set()
for k, size in SIZES.items():
    pool = strata[k]
    for r in rng.sample(pool, min(size, len(pool))):
        seen.add((r[0], r[1]))
        chosen.append(item(drug_ids[r[0]][0], food_ids[r[1]][0], r, k, False))

pair_row = {(r[0], r[1]): r for r in rows}
ctrl_n = 0
for dn, fn in CONTROLS:
    (d, d_name), (f, f_name) = resolve('d', dn), resolve('f', fn)
    if (d, f) in seen:
        for it in chosen:
            if it['drug_en'] == d_name and it['food_en'] == f_name: it['control'] = True
        continue
    seen.add((d, f))
    chosen.append(item(d_name, f_name, pair_row.get((d, f)), 'CTRL', True, d, f))
    ctrl_n += 1

rng.shuffle(chosen)
blind, key = [], []
for k, it in enumerate(chosen, 1):
    code = f'P{k:03d}'
    blind.append({'id': code, 'medicamento': N.display(it['drug_en']), 'alimento': N.display(it['food_en']),
                  'medicamento_original': it['drug_en'], 'alimento_original': it['food_en'], 'artigos': it['links']})
    key.append({'id': code, **it})

meta = {'gerado_em': datetime.date.today().isoformat(), 'semente': SEED, 'base': 'FooDrugs 4.0.0',
        'universo_realista': len(universe), 'estratos_universo': {k: len(v) for k, v in strata.items()},
        'estratos_amostra': {k: sum(i['stratum'] == k for i in key) for k in list(SIZES) + ['CTRL']},
        'controles_fora_da_amostra_aleatoria': ctrl_n, 'total': len(key)}
json.dump({'meta': {k: meta[k] for k in ('gerado_em', 'total')}, 'itens': blind},
          open(OUT / 'amostra_cega.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({'meta': meta, 'itens': key}, open(OUT / 'gabarito_sistema.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(meta, ensure_ascii=False, indent=1))
