"""Re-score the blind evaluation of 11/10/2026 against the CURRENT system (same items, same judge labels).

Run from backend/:  ..\\.venv\\Scripts\\python.exe avaliacao\\reavaliar.py
Reads data/avaliacao-cega-2026-10-11.json (self-contained: sentences, pairs and judge labels) and writes
data/avaliacao-cega-reavaliada-AAAA-MM-DD.json with the October metrics next to the current ones.

A (sentences): each sentence is re-classified with the current rules.
B (realistic pairs): the level is what the application now shows for the pair (synonyms pooled and class or
component inference, as in /api/check, without clinical profile). Note: the judges read sentences of the
literal pair, so a pair raised only by inference is scored against a label given for the literal pair.
"""
import datetime, json, sqlite3, sys
from pathlib import Path
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import risk_rules as R
import foodrugs_store as store
from foodrugs_full import norm

ROOT = Path(__file__).resolve().parents[2]
src = json.load(open(ROOT / 'data/avaliacao-cega-2026-10-11.json', encoding='utf-8'))
old = src['metricas']

# A. Sentences.
rows = []
for it in src['A_trechos']:
    cat, flags, _ = R.classify(it['trecho'])
    cat = R.adjust_for_terms(cat, flags, it['alimento'], it['medicamento'], it['trecho'])
    rows.append((cat == R.INTERACTION, it['juizes'] == 'yes'))
pred_i = [j for p, j in rows if p]; pred_m = [j for p, j in rows if not p]
a_new = {'amostra': len(rows), 'regra_interacao': len(pred_i), 'regra_outros': len(pred_m),
         'precisao_interacao': round(sum(pred_i) / len(pred_i), 3) if pred_i else None,
         'taxa_omissao_por_trecho': round(sum(pred_m) / len(pred_m), 4) if pred_m else None}

# B. Pairs, as the application answers them now.
c = sqlite3.connect(store.PATH.resolve().as_uri() + '?mode=ro', uri=True)
def entity(table, name):
    r = c.execute(f'SELECT id FROM {table} WHERE norm=?', (norm(name),)).fetchone()
    return r[0] if r else None
tp = fp = fn = tn = 0; detail = []
for it in src['B_pares']:
    d, f = entity('_drugs', it['medicamento']), entity('_foods', it['alimento'])
    r = store.evidence(f'fd:d:{d}', f'fd:f:{f}', limit=1)
    level = r['risk'] if r['found'] else 0
    flagged, judge = (level or 0) >= 1, it['juizes'] == 'yes'
    tp += flagged and judge; fp += flagged and not judge; fn += (not flagged) and judge; tn += (not flagged) and not judge
    detail.append({'par': f"{it['medicamento']} + {it['alimento']}", 'nivel_outubro': it['nivel_regras'], 'nivel_atual': level,
                   'inferido': (r.get('inferred') or {}).get('type'), 'juizes': 'interação' if judge else 'sem evidência'})
ratio = lambda a, b: round(a / b, 3) if b else None
b_new = {'pares': len(detail), 'vp': tp, 'fp': fp, 'fn': fn, 'vn': tn, 'precisao': ratio(tp, tp + fp),
         'sensibilidade': ratio(tp, tp + fn), 'especificidade': ratio(tn, tn + fp), 'acuracia': ratio(tp + tn, len(detail))}

today = datetime.date.today().isoformat()
out = {'data': today, 'base': 'Mesmos itens e rótulos da avaliação cega de 2026-10-11, pontuados no sistema atual.',
       'outubro': {'A_sentencas': {k: old['A_sentencas'].get(k) for k in a_new}, 'B_pares_realistas': {k: old['B_pares_realistas'].get(k) for k in b_new}},
       'atual': {'A_sentencas': a_new, 'B_pares_realistas': b_new},
       'pares_que_mudaram': [x for x in detail if x['nivel_outubro'] != x['nivel_atual']], 'detalhes_B': detail}
path = ROOT / f'data/avaliacao-cega-reavaliada-{today}.json'
json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ('outubro', 'atual')}, ensure_ascii=False, indent=1))
print('pares que mudaram:'); [print(' ', x) for x in out['pares_que_mudaram']]
print('gravado', path)
