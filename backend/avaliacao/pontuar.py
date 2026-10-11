"""Score the final rules against the held-out blind judgments. Run from backend."""
import json, sqlite3, sys
sys.path.insert(0, '.')
import risk_rules as R
import foodrugs_store as store

SP = sys.argv[1]
out = json.load(open(SP + '/heldout_out.json', encoding='utf-8'))
labels = {(x['part'], x['n']): x for x in out['result']['labels']}
c = sqlite3.connect(store.PATH.resolve().as_uri() + '?mode=ro', uri=True)
summary = json.loads(c.execute("SELECT value FROM _metadata WHERE key='risk_rules'").fetchone()[0])
report = {'rules': summary['rules']}

# A. Sentences (re-classified with the final rules, same function used for the whole base).
a = json.load(open(SP + '/heldout_a_key.json', encoding='utf-8'))
rows = []
for it in a:
    cat, flags, _ = R.classify(it['text'])
    cat = R.adjust_for_terms(cat, flags, it['food'], it['drug'], it['text'])
    rows.append((cat, labels[('A', it['n'])]['label']))
pred_i = [j for cat, j in rows if cat == R.INTERACTION]
pred_m = [j for cat, j in rows if cat != R.INTERACTION]
prec = sum(j == 'yes' for j in pred_i) / len(pred_i)
miss = sum(j == 'yes' for j in pred_m) / len(pred_m)
n_i = summary['categories']['interacao']; n_m = summary['categories']['mencao'] + summary['categories']['sem_efeito']
est_recall = n_i * prec / (n_i * prec + n_m * miss) if (n_i * prec + n_m * miss) else None
report['A_sentencas'] = {
    'amostra': len(rows), 'regra_interacao': len(pred_i), 'regra_outros': len(pred_m),
    'precisao_interacao': round(prec, 3), 'acertos_interacao': sum(j == 'yes' for j in pred_i),
    'interacoes_entre_mencoes': sum(j == 'yes' for j in pred_m), 'taxa_omissao_por_trecho': round(miss, 4),
    'cobertura_estimada_na_base': round(est_recall, 3) if est_recall is not None else None,
    'acordo_juizes': sum(labels[('A', it['n'])]['agreement'] for it in a)}

# B. Realistic pairs (level recomputed from the final tables).
b = json.load(open(SP + '/heldout_b_key.json', encoding='utf-8'))
tp = fp = fn = tn = 0; detail = []
for it in b:
    d = store.search('d', it['drug']); f = store.search('f', it['food'])
    level = None
    for dd in d[:5]:
        for ff in f[:5]:
            if dd['name'] == it['drug'] and ff['name'] == it['food']:
                row = c.execute('SELECT level FROM _pair_risk WHERE drug_id=? AND food_id=?',
                                (store.entity_id(dd['id'], 'd'), store.entity_id(ff['id'], 'f'))).fetchone()
                if row: level = row[0]
    level = it['level'] if level is None else level
    judge = labels[('B', it['n'])]['label'] == 'yes'
    flagged = level >= 1
    tp += flagged and judge; fp += flagged and not judge; fn += (not flagged) and judge; tn += (not flagged) and not judge
    detail.append({'par': f"{it['drug']} + {it['food']}", 'nivel': level, 'juizes': 'interação' if judge else 'sem evidência'})
report['B_pares_realistas'] = {
    'pares': len(b), 'vp': tp, 'fp': fp, 'fn': fn, 'vn': tn,
    'precisao': round(tp / (tp + fp), 3) if tp + fp else None,
    'sensibilidade': round(tp / (tp + fn), 3) if tp + fn else None,
    'especificidade': round(tn / (tn + fp), 3) if tn + fp else None,
    'acuracia': round((tp + tn) / len(b), 3),
    'acordo_juizes': sum(labels[('B', it['n'])]['agreement'] for it in b), 'detalhes': detail}
print(json.dumps({k: (v if k != 'B_pares_realistas' else {x: y for x, y in v.items() if x != 'detalhes'}) for k, v in report.items()}, ensure_ascii=False, indent=2))
json.dump(report, open(SP + '/heldout_report.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
for d in detail:
    print(' ', d)
