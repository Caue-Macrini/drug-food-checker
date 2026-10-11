"""Measure the risk rules against independent references and export a sample for human review.

Run from backend after classify_foodrugs.py: ../.venv/Scripts/python.exe validate_risk.py
Writes data/validacao-classificacao.json and data/amostra-revisao-trechos.csv.
"""
import csv, json, random, sqlite3
from collections import Counter
from pathlib import Path
import risk_rules as R
import foodrugs_store as store

ROOT = Path(__file__).resolve().parents[1]

def drugs_com_agreement(c):
    """Hide the Drugs.com sentence and classify the pair from the literature only."""
    curated = c.execute('SELECT drug_id, food_id, curated_level FROM _pair_risk WHERE curated_level IS NOT NULL').fetchall()
    matrix, compared = Counter(), 0
    for drug_id, food_id, reference in curated:
        rows = c.execute('''SELECT t.text_id, s.category, s.flags FROM _tm t JOIN _tm_signal s ON s.source_id = t.source_id
            WHERE t.drug_id = ? AND t.food_id = ? AND s.curated IS NULL''', (drug_id, food_id)).fetchall()
        if not rows:
            continue
        compared += 1
        idocs = {t for t, cat, _ in rows if cat == R.INTERACTION}
        sdocs = {t for t, cat, f in rows if cat == R.INTERACTION and f & R.STRONG}
        ndocs = {t for t, cat, _ in rows if cat == R.NO_EFFECT}
        matrix[(reference, R.pair_level(None, len(idocs), len(sdocs), len(ndocs)))] += 1
    flagged = sum(v for (ref, pred), v in matrix.items() if pred >= 1)
    return {'curated_pairs': len(curated), 'pairs_with_literature': compared,
            'confusion': {f'drugs.com {ref} -> regras {pred}': v for (ref, pred), v in sorted(matrix.items())},
            'detected_as_interaction': flagged, 'sensitivity': round(flagged / compared, 3) if compared else None}

def catalog_control(c):
    """FDA/MedlinePlus catalog pairs are documented interactions: they should not come out green."""
    rows = json.loads((ROOT / 'data/catalogo-oficial.json').read_text(encoding='utf-8'))['rows']
    results = []
    for row in rows:
        drugs = {d['id'] for term in [row['drug'], *row['drug_aliases']] for d in store.search('d', term)[:3]}
        foods = {f['id'] for term in [row['food'], *row['food_aliases']] for f in store.search('f', term)[:3]}
        best = None
        for d in drugs:
            for f in foods:
                hit = c.execute('SELECT level, records, interaction_docs FROM _pair_risk WHERE drug_id = ? AND food_id = ?',
                                (store.entity_id(d, 'd'), store.entity_id(f, 'f'))).fetchone()
                if hit and (best is None or hit[1] > best[1]):
                    best = hit
        results.append({'drug': row['drug'], 'food': row['food'], 'found': best is not None,
                        'level': best[0] if best else None, 'records': best[1] if best else 0})
    found = [r for r in results if r['found']]
    return {'pairs': len(results), 'found_in_foodrugs': len(found),
            'levels_when_found': dict(Counter(R.LEVEL_NAMES[r['level']] for r in found)),
            'not_green_when_found': round(sum(r['level'] >= 1 for r in found) / len(found), 3) if found else None,
            'details': results}

def review_sample(c, size=60, seed=20261010):
    """Random sentences per category, with an empty column for the human reviewer."""
    random.seed(seed)
    out = []
    for category in (R.INTERACTION, R.MENTION, R.NO_EFFECT):
        ids = [r[0] for r in c.execute('SELECT source_id FROM _tm_signal WHERE category = ?', (category,))]
        for source_id in random.sample(ids, min(size, len(ids))):
            tm = c.execute('SELECT texts_ID, start_index, end_index, drug, food FROM TM_interactions WHERE TM_interactions_ID = ?', (source_id,)).fetchone()
            doc = c.execute('SELECT document FROM texts WHERE texts_ID = ?', (tm[0],)).fetchone()[0] or ''
            out.append({'registro': source_id, 'medicamento': tm[3], 'alimento': tm[4], 'trecho': doc[tm[1]:min(tm[2] or tm[1] + 600, tm[1] + 600)],
                        'classificacao_regras': R.SIGNAL_LABELS[category], 'revisor_concorda (sim/nao)': '', 'observacao': ''})
    return out

def main():
    c = sqlite3.connect(store.PATH.resolve().as_uri() + '?mode=ro', uri=True)
    summary = json.loads(c.execute("SELECT value FROM _metadata WHERE key = 'risk_rules'").fetchone()[0])
    report = {'rules': R.RULES_VERSION, 'classification': summary,
              'drugs_com_agreement': drugs_com_agreement(c), 'catalog_positive_control': catalog_control(c)}
    sample = review_sample(c)
    (ROOT / 'data/validacao-classificacao.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with open(ROOT / 'data/amostra-revisao-trechos.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(sample[0]), delimiter=';')
        writer.writeheader(); writer.writerows(sample)
    brief = {k: v for k, v in report['catalog_positive_control'].items() if k != 'details'}
    print(json.dumps({**report, 'catalog_positive_control': brief}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
