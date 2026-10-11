"""Export the blind evaluation (items, judge labels, rule output, metrics) into data/. Run from backend."""
import json, sys
sys.path.insert(0, '.')
import risk_rules as R

SP = sys.argv[1]
report = json.load(open(SP + '/heldout_report.json', encoding='utf-8'))
out = json.load(open(SP + '/heldout_out.json', encoding='utf-8'))
labels = {(x['part'], x['n']): x for x in out['result']['labels']}
a = json.load(open(SP + '/heldout_a_key.json', encoding='utf-8'))
b = json.load(open(SP + '/heldout_b_key.json', encoding='utf-8'))
names = {R.INTERACTION: 'indica interação', R.MENTION: 'apenas menciona', R.NO_EFFECT: 'sem efeito observado'}
items_a = []
for it in a:
    cat, flags, _ = R.classify(it['text'])
    cat = R.adjust_for_terms(cat, flags, it['food'], it['drug'], it['text'])
    lab = labels[('A', it['n'])]
    items_a.append({'registro': it['id'], 'medicamento': it['drug'], 'alimento': it['food'], 'trecho': it['text'],
                    'regras': names[cat], 'juizes': lab['label'], 'juizes_concordaram': lab['agreement']})
levels = {d['par']: d['nivel'] for d in report['B_pares_realistas']['detalhes']}
items_b = []
for it in b:
    lab = labels[('B', it['n'])]
    items_b.append({'medicamento': it['drug'], 'alimento': it['food'], 'registros_no_par': it['records'],
                    'nivel_regras': levels[f"{it['drug']} + {it['food']}"], 'juizes': lab['label'],
                    'juizes_concordaram': lab['agreement'], 'trechos_mostrados': it['sentences']})
doc = {
    'data': '2026-10-11', 'regras': report['rules'],
    'metodo': ('Avaliação cega com amostras não usadas no ajuste das regras. Cada item foi julgado por dois juízes '
               'automatizados independentes (instâncias de modelo de linguagem), sem acesso à saída das regras; '
               'divergências foram decididas por um terceiro juiz. A: 120 trechos sorteados da base inteira, '
               'estratificados pela saída das regras (60 "indica interação", 60 demais). B: 60 pares realistas '
               '(medicamento comum + alimento comum presentes na base), 30 amarelos/vermelhos e 30 verdes; os juízes '
               'leram até 8 trechos sorteados de cada par. Recomenda-se revisão humana; a planilha '
               'amostra-revisao-trechos.csv serve para isso.'),
    'metricas': {k: (v if k != 'B_pares_realistas' else {x: y for x, y in v.items() if x != 'detalhes'}) for k, v in report.items() if k != 'rules'},
    'A_trechos': items_a, 'B_pares': items_b}
json.dump(doc, open('../data/avaliacao-cega-2026-10-11.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok', len(items_a), len(items_b))
