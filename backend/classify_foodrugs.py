"""Apply risk_rules to every FooDrugs text-mining record and store derived risk tables.

Run from backend: ../.venv/Scripts/python.exe classify_foodrugs.py [path/to/foodrugs-v4.sqlite]
Original FooDrugs tables are only read. Results go to _tm_signal, _pair_risk and _metadata.
"""
import argparse, json, sqlite3, time
from collections import Counter
from pathlib import Path
import risk_rules as R

DEFAULT = Path(__file__).resolve().parents[1] / '.local-data/foodrugs-v4.sqlite'

def classify_database(path):
    started = time.time()
    c = sqlite3.connect(path)
    c.execute('PRAGMA cache_size=-200000')
    # Build into staging tables and swap them in one transaction at the end, so the running
    # application never reads empty or half-built risk tables.
    c.executescript('''
        DROP TABLE IF EXISTS _tm_signal_new;
        DROP TABLE IF EXISTS _pair_risk_new;
        CREATE TABLE _tm_signal_new(source_id INTEGER PRIMARY KEY, category INTEGER NOT NULL, flags INTEGER NOT NULL,
            mechanisms TEXT NOT NULL, curated INTEGER, curated_label TEXT);
        CREATE TABLE _pair_risk_new(drug_id INTEGER NOT NULL, food_id INTEGER NOT NULL, level INTEGER NOT NULL,
            curated_level INTEGER, curated_label TEXT, records INTEGER NOT NULL, interaction_records INTEGER NOT NULL,
            interaction_docs INTEGER NOT NULL, strong_docs INTEGER NOT NULL, no_effect_docs INTEGER NOT NULL,
            pk_docs INTEGER NOT NULL, pd_docs INTEGER NOT NULL, mechanisms TEXT NOT NULL,
            PRIMARY KEY(drug_id, food_id)) WITHOUT ROWID;''')
    pairs, categories, signals = {}, Counter(), []
    last_text, document, curated_source = None, '', False
    rows = c.execute('''SELECT tm.TM_interactions_ID, tm.texts_ID, tm.start_index, tm.end_index, x.drug_id, x.food_id, tm.drug, tm.food
        FROM TM_interactions tm JOIN _tm x ON x.source_id = tm.TM_interactions_ID ORDER BY tm.texts_ID''')
    reader = sqlite3.connect(path)
    for n, (source_id, text_id, start, end, drug_id, food_id, drug, food) in enumerate(rows, 1):
        if text_id != last_text:
            doc = reader.execute('SELECT document, link FROM texts WHERE texts_ID=?', (text_id,)).fetchone()
            document, link = (doc[0] or '', doc[1] or '') if doc else ('', '')
            curated_source, last_text = 'drugs.com' in link, text_id
        start = start or 0
        end = end if end and end > start else start + 600
        sentence = document[start:min(end, start + 2000)]
        category, flags, mechanisms = R.classify(sentence)
        category = R.adjust_for_terms(category, flags, food, drug, sentence)
        curated, label = R.curated_severity(document, start, link, drug, food) if curated_source else (None, '')
        if curated is not None and category == R.MENTION:
            category = R.INTERACTION
        categories[category] += 1
        signals.append((source_id, category, flags, ','.join(mechanisms), curated, label))
        p = pairs.setdefault((drug_id, food_id), {'records': 0, 'inter': 0, 'idocs': set(), 'sdocs': set(), 'ndocs': set(),
                                                  'pk': set(), 'pd': set(), 'mech': Counter(), 'curated': None, 'label': ''})
        p['records'] += 1
        if curated is not None and (p['curated'] is None or curated > p['curated']):
            p['curated'], p['label'] = curated, label
        if category == R.INTERACTION:
            p['inter'] += 1; p['idocs'].add(text_id)
            if flags & R.STRONG: p['sdocs'].add(text_id)
            if flags & R.PK: p['pk'].add(text_id)
            if flags & R.PD: p['pd'].add(text_id)
            p['mech'].update(mechanisms)
        elif category == R.NO_EFFECT:
            p['ndocs'].add(text_id)
        if len(signals) >= 50000:
            c.executemany('INSERT INTO _tm_signal_new VALUES (?,?,?,?,?,?)', signals); signals.clear()
            print(f'{n:,} registros classificados', flush=True)
    c.executemany('INSERT INTO _tm_signal_new VALUES (?,?,?,?,?,?)', signals)
    levels = Counter()
    batch = []
    for (drug_id, food_id), p in pairs.items():
        level = R.pair_level(p['curated'], len(p['idocs']), len(p['sdocs']), len(p['ndocs']))
        levels[level] += 1
        batch.append((drug_id, food_id, level, p['curated'], p['label'], p['records'], p['inter'], len(p['idocs']),
                      len(p['sdocs']), len(p['ndocs']), len(p['pk']), len(p['pd']), ','.join(m for m, _ in p['mech'].most_common(3))))
    c.executemany('INSERT INTO _pair_risk_new VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', batch)
    summary = {'rules': R.RULES_VERSION, 'records': sum(categories.values()),
               'categories': {'mencao': categories[R.MENTION], 'interacao': categories[R.INTERACTION], 'sem_efeito': categories[R.NO_EFFECT]},
               'pairs': len(pairs), 'levels': {str(k): levels[k] for k in (0, 1, 2)},
               'curated_pairs': sum(1 for p in pairs.values() if p['curated'] is not None),
               'seconds': round(time.time() - started)}
    c.commit(); reader.close()
    c.isolation_level = None
    c.execute('BEGIN IMMEDIATE')
    c.execute('DROP TABLE IF EXISTS _tm_signal')
    c.execute('DROP TABLE IF EXISTS _pair_risk')
    c.execute('ALTER TABLE _tm_signal_new RENAME TO _tm_signal')
    c.execute('ALTER TABLE _pair_risk_new RENAME TO _pair_risk')
    c.execute("INSERT OR REPLACE INTO _metadata(key, value) VALUES ('risk_rules', ?)", (json.dumps(summary),))
    c.execute('COMMIT'); c.close()
    return summary

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('database', nargs='?', default=str(DEFAULT))
    print(json.dumps(classify_database(parser.parse_args().database), ensure_ascii=False, indent=2))
