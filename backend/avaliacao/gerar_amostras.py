"""Build the held-out evaluation samples (never used to tune the rules). Run from backend."""
import json, random, sqlite3, sys
sys.path.insert(0, '.')
import risk_rules as R
import foodrugs_store as store

SP = sys.argv[1]
c = sqlite3.connect(store.PATH.resolve().as_uri() + '?mode=ro', uri=True)
tuned = {int(x['id']) for x in json.load(open(SP + '/sample_blind.json', encoding='utf-8'))}

def sentence(source_id):
    tm = c.execute('SELECT texts_ID, start_index, end_index, drug, food FROM TM_interactions WHERE TM_interactions_ID=?', (source_id,)).fetchone()
    doc = c.execute('SELECT document FROM texts WHERE texts_ID=?', (tm[0],)).fetchone()[0] or ''
    start = tm[1] or 0
    end = tm[2] if tm[2] and tm[2] > start else start + 600
    return tm[3], tm[4], doc[start:min(end, start + 700)]

# A. Random sentences, stratified by the rule's category.
rng = random.Random(20261011)
a_items = []
for category, n in ((R.INTERACTION, 60), (R.MENTION, 60)):
    ids = [r[0] for r in c.execute('SELECT source_id FROM _tm_signal WHERE category=?', (category,)) if r[0] not in tuned]
    for sid in rng.sample(ids, n):
        drug, food, text = sentence(sid)
        a_items.append({'id': sid, 'drug': drug, 'food': food, 'text': text, 'rule': category})
rng.shuffle(a_items)
for k, it in enumerate(a_items): it['n'] = k

# B. Realistic pairs: common medicines x common foods present in the base.
catalog = json.load(open('../data/catalogo-oficial.json', encoding='utf-8'))['rows']
drugs = {a.lower() for r in catalog for a in r['drug_aliases']} | R.CYP450_SUBSTRATES | R.RENAL_EXCRETION | R.HEPATOTOXIC
drugs |= {'aspirin', 'ibuprofen', 'levothyroxine', 'tetracycline', 'doxycycline', 'alendronate', 'phenelzine', 'linezolid',
          'metronidazole', 'tinidazole', 'nifedipine', 'fexofenadine', 'ciprofloxacin', 'digoxin', 'lithium', 'statins'}
foods = {'grapefruit', 'grapefruit juice', 'alcohol', 'ethanol', 'milk', 'coffee', 'tea', 'green tea', 'orange juice',
         'apple juice', 'cranberry', 'cranberry juice', 'vitamin k', 'cheese', 'wine', 'red wine', 'beer', 'calcium',
         'iron', 'potassium', 'magnesium', 'zinc', 'soy', 'soybean', 'fiber', 'dietary fiber', 'garlic', 'licorice',
         'food', 'meal', 'high-fat meal', 'fat', 'yogurt', 'banana', 'spinach', 'broccoli', 'pomegranate', 'tyramine',
         'salt', 'sodium', 'water', 'fruit juice', 'juice', 'caffeine', 'chocolate', 'honey', 'ginger', 'turmeric', 'curcumin'}
rows = c.execute('''SELECT r.drug_id, r.food_id, d.name, f.name, r.level, r.records FROM _pair_risk r
    JOIN _drugs d ON d.id=r.drug_id JOIN _foods f ON f.id=r.food_id''').fetchall()
candidates = [r for r in rows if r[2].strip().lower() in drugs and r[3].strip().lower() in foods]
flagged = [r for r in candidates if r[4] >= 1]
green = [r for r in candidates if r[4] == 0]
print(f'realistic pairs in base: {len(candidates)} (yellow/red {len(flagged)}, green {len(green)})')
b_pairs = rng.sample(flagged, min(30, len(flagged))) + rng.sample(green, min(30, len(green)))
rng.shuffle(b_pairs)
b_items = []
for k, (d, f, dname, fname, level, records) in enumerate(b_pairs):
    sids = [r[0] for r in c.execute('SELECT source_id FROM _tm WHERE drug_id=? AND food_id=?', (d, f))]
    chosen = rng.sample(sids, min(8, len(sids)))
    b_items.append({'n': k, 'drug': dname, 'food': fname, 'records': records, 'level': level,
                    'sentences': [sentence(s)[2] for s in chosen]})

json.dump([{k: v for k, v in it.items() if k != 'rule'} for it in a_items], open(SP + '/heldout_a_blind.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(a_items, open(SP + '/heldout_a_key.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump([{k: v for k, v in it.items() if k not in ('level', 'records')} for it in b_items], open(SP + '/heldout_b_blind.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(b_items, open(SP + '/heldout_b_key.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('A', len(a_items), 'B', len(b_items))
