"""Inter-rater agreement, adjudication and system metrics for the pharmacist evaluation (standard library only).

Usage (from backend/):  python avaliacao/kit_concordancia.py avaliacao/kit
Reads avaliador_A.xlsx and avaliador_B.xlsx (filled), gabarito_sistema.json and, when present,
adjudicacao.csv (third evaluator's decision on the disagreements).

Step 1 - agreement between A and B: percent agreement, Cohen's kappa (relevant = class >= 1) and weighted
         kappa (linear and quadratic) on the ordinal classes 0/1/2, with stratified bootstrap 95% CIs.
         Disagreements are written to adjudicacao.csv for a third evaluator.
Step 2 - reference standard = agreed class, or the adjudicated class. System positive = level >= 1;
         a pair absent from the base ("sem registro") counts as negative. Reports confusion matrices,
         sensitivity, specificity, PPV, NPV and accuracy with Wilson 95% CIs, per stratum, for the random
         sample weighted back to the evaluated universe, and for the literature controls.
Writes relatorio_avaliacao.json and relatorio_avaliacao.md.
"""
import csv, json, math, random, re, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

KIT = Path(sys.argv[1] if len(sys.argv) > 1 else 'avaliacao/kit')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # Windows console (cp1252) cannot print "≥"
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
VALID = ('0', '1', '2')

def read_sheet(path, title='Avaliação'):
    """Rows of one worksheet as dicts keyed by the header (minimal xlsx reader)."""
    z = zipfile.ZipFile(path)
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS):
            shared.append(''.join(t.text or '' for t in si.iter(f'{{{NS["m"]}}}t')))
    book = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    target = {r.get('Id'): r.get('Target') for r in rels}
    sheet = next(s for s in book.find('m:sheets', NS) if s.get('name') == title)
    file = target[sheet.get(f'{{{NS["r"]}}}id')].lstrip('/')
    file = file if file.startswith('xl/') else 'xl/' + file
    rows = []
    for row in ET.fromstring(z.read(file)).iter(f'{{{NS["m"]}}}row'):
        values = {}
        for cell in row.findall('m:c', NS):
            col = re.match(r'[A-Z]+', cell.get('r')).group()
            kind, v = cell.get('t'), cell.find('m:v', NS)
            if kind == 's' and v is not None: text = shared[int(v.text)]
            elif kind == 'inlineStr': text = ''.join(t.text or '' for t in cell.iter(f'{{{NS["m"]}}}t'))
            else: text = v.text if v is not None else ''
            values[col] = (text or '').strip()
        rows.append(values)
    head = rows[0]
    return [{head[c]: r.get(c, '') for c in head} for r in rows[1:] if r.get('A')]

def code(answer):
    """'2 - Interação relevante…' -> '2'; 'NS - …' -> 'NS'; '' -> ''."""
    return answer.split(' ')[0].strip().upper() if answer else ''

def answers(ev):
    rows = read_sheet(KIT / f'avaliador_{ev}.xlsx')
    note = next((h for h in (rows[0] if rows else {}) if h.startswith(('Comentário', 'Trecho'))), None)
    return {r['ID']: {'classe': code(r['Classificação']), 'confianca': r['Confiança'], 'fonte': r['Fonte principal'],
                      'comentario': r.get(note, '') if note else ''} for r in rows}

def kappa(pairs, cats, weight=None):
    """Cohen's kappa; weight in (None, 'linear', 'quadratic') for ordinal categories."""
    n = len(pairs)
    if not n: return None
    k = len(cats); ix = {c: i for i, c in enumerate(cats)}
    w = [[(0 if i == j else 1) if weight is None else (abs(i - j) / (k - 1)) ** (1 if weight == 'linear' else 2)
          for j in range(k)] for i in range(k)]
    obs = [[0] * k for _ in range(k)]
    for a, b in pairs: obs[ix[a]][ix[b]] += 1
    ra = [sum(obs[i]) / n for i in range(k)]; rb = [sum(obs[i][j] for i in range(k)) / n for j in range(k)]
    do = sum(w[i][j] * obs[i][j] / n for i in range(k) for j in range(k))
    de = sum(w[i][j] * ra[i] * rb[j] for i in range(k) for j in range(k))
    return 1.0 if de == 0 else 1 - do / de

def boot(pairs, fn, reps=2000, seed=7):
    if len(pairs) < 2: return None
    rng = random.Random(seed); vals = []
    for _ in range(reps):
        v = fn([pairs[rng.randrange(len(pairs))] for _ in pairs])
        if v is not None: vals.append(v)
    vals.sort()
    return [round(vals[int(0.025 * len(vals))], 3), round(vals[int(0.975 * len(vals)) - 1], 3)]

def wilson(x, n):
    if not n: return None
    p, z = x / n, 1.959964
    d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 3), round((c + h) / d, 3)]

def binary(rows, w=None):
    """rows: (system_positive, reference_positive). Optional weights for the universe estimate."""
    w = w or [1] * len(rows)
    tp = sum(wi for (s, g), wi in zip(rows, w) if s and g); fp = sum(wi for (s, g), wi in zip(rows, w) if s and not g)
    fn = sum(wi for (s, g), wi in zip(rows, w) if not s and g); tn = sum(wi for (s, g), wi in zip(rows, w) if not s and not g)
    r = lambda a, b: round(a / b, 3) if b else None
    out = {'vp': round(tp, 1), 'fp': round(fp, 1), 'fn': round(fn, 1), 'vn': round(tn, 1),
           'sensibilidade': r(tp, tp + fn), 'especificidade': r(tn, tn + fp), 'vpp': r(tp, tp + fp),
           'vpn': r(tn, tn + fn), 'acuracia': r(tp + tn, tp + fp + fn + tn)}
    if all(x == 1 for x in w):
        out['ic95'] = {'sensibilidade': wilson(tp, tp + fn), 'especificidade': wilson(tn, tn + fp),
                       'vpp': wilson(tp, tp + fp), 'vpn': wilson(tn, tn + fn), 'acuracia': wilson(tp + tn, len(rows))}
    return out

key = {it['id']: it for it in json.load(open(KIT / 'gabarito_sistema.json', encoding='utf-8'))['itens']}
meta = json.load(open(KIT / 'gabarito_sistema.json', encoding='utf-8'))['meta']
A, B = answers('A'), answers('B')
ids = sorted(key)
missing = {ev: [i for i in ids if not ans.get(i, {}).get('classe')] for ev, ans in (('A', A), ('B', B))}
report = {'amostra': len(ids), 'sem_resposta': {k: len(v) for k, v in missing.items()}}

# Step 1: agreement.
both = [(A[i]['classe'], B[i]['classe']) for i in ids if A.get(i, {}).get('classe') in VALID and B.get(i, {}).get('classe') in VALID]
rel = [('1' if a != '0' else '0', '1' if b != '0' else '0') for a, b in both]
agree = {
    'pares_com_classe_valida_nos_dois': len(both),
    'concordancia_exata': round(sum(a == b for a, b in both) / len(both), 3) if both else None,
    'kappa_relevante_vs_nao': round(kappa(rel, ('0', '1')), 3) if rel else None,
    'kappa_relevante_ic95': boot(rel, lambda p: kappa(p, ('0', '1'))),
    'kappa_ponderado_linear': round(kappa(both, VALID, 'linear'), 3) if both else None,
    'kappa_ponderado_quadratico': round(kappa(both, VALID, 'quadratic'), 3) if both else None,
    'kappa_quadratico_ic95': boot(both, lambda p: kappa(p, VALID, 'quadratic')),
    'ns_inv': {ev: {c: sum(ans.get(i, {}).get('classe') == c for i in ids) for c in ('NS', 'INV')} for ev, ans in (('A', A), ('B', B))},
}
report['concordancia'] = agree

# Disagreements -> adjudication (keeps a decision already written by the third evaluator).
adj_path = KIT / 'adjudicacao.csv'
decided = {}
if adj_path.exists():
    for r in csv.DictReader(open(adj_path, encoding='utf-8-sig'), delimiter=';'):
        if code(r.get('decisao', '')): decided[r['id']] = code(r['decisao'])
disagree = [i for i in ids if A.get(i, {}).get('classe') and B.get(i, {}).get('classe') and A[i]['classe'] != B[i]['classe']]
with open(adj_path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['id', 'medicamento', 'alimento', 'classe_A', 'comentario_A', 'classe_B', 'comentario_B',
                'decisao', 'justificativa'])
    for i in disagree:
        w.writerow([i, key[i]['drug_en'], key[i]['food_en'], A[i]['classe'], A[i]['comentario'], B[i]['classe'],
                    B[i]['comentario'], decided.get(i, ''), ''])
report['divergencias'] = len(disagree); report['adjudicadas'] = sum(i in decided for i in disagree)

# Step 2: reference standard and system metrics.
reference = {}
for i in ids:
    a, b = A.get(i, {}).get('classe'), B.get(i, {}).get('classe')
    if a and a == b: reference[i] = a
    elif i in decided: reference[i] = decided[i]
pending = [i for i in ids if i not in reference]
report['padrao_ouro'] = {'definidos': len(reference), 'pendentes': len(pending),
                         'por_classe': {c: sum(v == c for v in reference.values()) for c in VALID + ('NS', 'INV')}}

def sys_level(i): return key[i]['level']  # None = sem registro
judged = [i for i in ids if reference.get(i) in VALID]
strata = [s for s in meta['estratos_universo']]
random_ids = [i for i in judged if key[i]['stratum'] in strata]
rows = lambda sel: [((sys_level(i) or 0) >= 1, reference[i] != '0') for i in sel]

# Weights: each judged item stands for N_h / n_h pairs of its stratum in the evaluated universe.
n_h = {s: sum(key[i]['stratum'] == s for i in random_ids) for s in strata}
weight = {s: meta['estratos_universo'][s] / n_h[s] for s in strata if n_h[s]}
metrics = {
    'amostra_aleatoria_nao_ponderada': binary(rows(random_ids)),
    'universo_ponderado': binary(rows(random_ids), [weight[key[i]['stratum']] for i in random_ids]),
    'controles_da_literatura': binary(rows([i for i in judged if key[i]['control']])),
    'por_estrato': {s: {'n': n_h[s], 'N_universo': meta['estratos_universo'][s],
                        'proporcao_relevante_padrao_ouro': round(sum(reference[i] != '0' for i in random_ids if key[i]['stratum'] == s) / n_h[s], 3) if n_h[s] else None,
                        'proporcao_classe_2': round(sum(reference[i] == '2' for i in random_ids if key[i]['stratum'] == s) / n_h[s], 3) if n_h[s] else None}
                    for s in strata},
}
lv = lambda i: str(sys_level(i) if sys_level(i) is not None else 0)
matrix = {s: {g: sum(lv(i) == s and reference[i] == g for i in judged) for g in VALID} for s in VALID}
metrics['matriz_sistema_x_padrao_ouro'] = matrix
metrics['kappa_quadratico_sistema_x_padrao_ouro'] = round(kappa([(lv(i), reference[i]) for i in judged], VALID, 'quadratic'), 3) if judged else None
metrics['sem_registro_na_base'] = [{'id': i, 'par': f"{key[i]['drug_en']} + {key[i]['food_en']}", 'padrao_ouro': reference.get(i)}
                                   for i in ids if key[i]['level'] is None]
metrics['falsos_negativos'] = [{'id': i, 'par': f"{key[i]['drug_en']} + {key[i]['food_en']}", 'sistema': key[i]['level'], 'padrao_ouro': reference[i]}
                               for i in judged if (sys_level(i) or 0) == 0 and reference[i] != '0']
metrics['pares_invalidos_por_estrato'] = {s: sum(reference.get(i) == 'INV' and key[i]['stratum'] == s for i in ids) for s in strata + ['CTRL']}
report['desempenho'] = metrics if not pending else {'aviso': f'{len(pending)} pares sem padrão-ouro; resolva adjudicacao.csv', **metrics}

json.dump(report, open(KIT / 'relatorio_avaliacao.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def pct(v): return '—' if v is None else f'{100 * v:.1f}%'
def ci(v): return '' if not v else f' (IC95% {100 * v[0]:.1f}–{100 * v[1]:.1f}%)'
u, s, c = metrics['universo_ponderado'], metrics['amostra_aleatoria_nao_ponderada'], metrics['controles_da_literatura']
md = [f'# Relatório da avaliação ({KIT.name})', '',
      f"Amostra: {len(ids)} pares ({', '.join(f'{k} {v}' for k, v in meta['estratos_amostra'].items())}). "
      f"Universo avaliado: {meta['universo_realista']} pares.", '',
      '## Concordância entre avaliadores', '',
      f"- Pares com classe válida (0/1/2) nos dois: {agree['pares_com_classe_valida_nos_dois']}",
      f"- Concordância exata: {pct(agree['concordancia_exata'])}",
      f"- Kappa (relevante × não relevante): {agree['kappa_relevante_vs_nao']} {agree['kappa_relevante_ic95'] or ''}",
      f"- Kappa ponderado quadrático (0/1/2): {agree['kappa_ponderado_quadratico']} {agree['kappa_quadratico_ic95'] or ''}",
      f"- Divergências: {len(disagree)} (adjudicadas: {report['adjudicadas']})", '',
      '## Desempenho do sistema (positivo = nível ≥ 1; sem registro = negativo)', '',
      '| Recorte | Sensibilidade | Especificidade | VPP | VPN | Acurácia |', '|---|---|---|---|---|---|',
      f"| Amostra aleatória | {pct(s['sensibilidade'])}{ci(s.get('ic95', {}).get('sensibilidade'))} | {pct(s['especificidade'])}{ci(s.get('ic95', {}).get('especificidade'))} | {pct(s['vpp'])} | {pct(s['vpn'])} | {pct(s['acuracia'])} |",
      f"| Universo (ponderado) | {pct(u['sensibilidade'])} | {pct(u['especificidade'])} | {pct(u['vpp'])} | {pct(u['vpn'])} | {pct(u['acuracia'])} |",
      f"| Controles da literatura | {pct(c['sensibilidade'])}{ci(c.get('ic95', {}).get('sensibilidade'))} | — | — | — | — |", '',
      '## Matriz sistema × padrão de referência', '', '| Sistema \\ Referência | 0 | 1 | 2 |', '|---|---|---|---|',
      *[f'| {k} | ' + ' | '.join(str(matrix[k][g]) for g in VALID) + ' |' for k in VALID], '',
      f"Kappa quadrático sistema × padrão-ouro: {metrics['kappa_quadratico_sistema_x_padrao_ouro']}", '',
      '## Falsos negativos (sistema 0 ou sem registro; padrão de referência ≥ 1)', '',
      *[f"- {x['id']} {x['par']} (sistema {x['sistema'] if x['sistema'] is not None else 'sem registro'}, padrão-ouro {x['padrao_ouro']})" for x in metrics['falsos_negativos']]]
if pending: md.insert(2, f'> Atenção: {len(pending)} pares ainda sem padrão-ouro. Preencha a coluna "decisao" de adjudicacao.csv e rode de novo.\n')
open(KIT / 'relatorio_avaliacao.md', 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print('\n'.join(md))
