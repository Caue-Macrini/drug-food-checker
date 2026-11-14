"""Brand-name search: commercial names from the ANVISA/CMED price list mapped to FooDrugs medicines.

FooDrugs uses the international (English) names found in scientific articles. People in Brazil usually know
the brand ("Marevan", "Puran T4", "Glifage"). The CMED list (Câmara de Regulação do Mercado de Medicamentos,
public data) links every marketed product to its active substances in Portuguese (DCB). This module:

  extrair   CMED .xlsx  -> data/cmed-marcas.csv (brand; substances; product types). Needs openpyxl.
  aplicar   data/cmed-marcas.csv -> search aliases in the installed FooDrugs database (source='cmed').
            Each substance is translated to candidate English names and accepted only when a candidate is
            an existing FooDrugs medicine term (exact match): unmatched substances are reported, never guessed.

Usage (from backend/):
  python cmed_marcas.py extrair ../.local-data/cmed/lista_pmc_AAAAMMDD.xlsx
  python cmed_marcas.py aplicar [caminho/do/foodrugs.sqlite]
"""
import csv, json, re, sqlite3, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / 'data/cmed-marcas.csv'
REPORT = ROOT / '.local-data/cmed/relatorio-mapeamento.json'

def plain(text):
    text = unicodedata.normalize('NFKD', str(text or '').lower())
    return ' '.join(''.join(c for c in text if not unicodedata.combining(c)).split())

# Salt, ester, hydrate and form words that do not change which medicine it is.
SALT_PREFIX = re.compile(r'^(?:(?:di|bis|hemi|mono)?(?:cloridrato|bromidrato|maleato|besilato|besilato|mesilato|succinato|tartarato|'
                         r'fumarato|citrato|sulfato|bissulfato|fosfato|acetato|valerato|propionato|dipropionato|oxalato|benzoato|'
                         r'nitrato|lactato|gluconato|carbonato|napsilato|pamoato|tosilato|esilato|estearato|palmitato|undecilato|'
                         r'decanoato|enantato|cipionato|furoato|xinafoato|brometo|iodeto|hiclato|edisilato|levomalato|dimesilato|'
                         r'cloridrato monoidratado))\s+de\s+')
SALT_WORDS = {'sodica', 'sodico', 'potassica', 'potassico', 'calcica', 'calcico', 'magnesica', 'magnesico', 'monoidratada',
              'monoidratado', 'di-hidratada', 'di-hidratado', 'tri-hidratada', 'tri-hidratado', 'hemi-hidratada',
              'hemi-hidratado', 'sesqui-hidratado', 'anidra', 'anidro', 'hidratada', 'hidratado', 'micronizada', 'micronizado',
              'base', 'dietilamonio', 'trometamol', 'racemica', 'racemico', 'sodio', 'potassio', 'cloridrato', 'l-lisina',
              'arginina', 'meglumina', 'colina', 'tromethamine', 'trihidratada', 'trihidratado', 'diidratada', 'diidratado',
              'tetraidratado', 'hexaidratado'}

# Names whose English form is not derivable by suffix rules.
MANUAL = {'varfarina': 'warfarin', 'dipirona': 'dipyrone', 'metamizol': 'metamizole', 'anlodipino': 'amlodipine',
          'acido acetilsalicilico': 'aspirin', 'paracetamol': 'acetaminophen', 'levotiroxina': 'levothyroxine',
          'colecalciferol': 'cholecalciferol', 'ergocalciferol': 'ergocalciferol', 'fenitoina': 'phenytoin',
          'fenobarbital': 'phenobarbital', 'fenelzina': 'phenelzine', 'tiamina': 'thiamine', 'piridoxina': 'pyridoxine',
          'cianocobalamina': 'cyanocobalamin', 'retinol': 'retinol', 'alopurinol': 'allopurinol', 'teofilina': 'theophylline',
          'aminofilina': 'aminophylline', 'clortalidona': 'chlorthalidone', 'hidroclorotiazida': 'hydrochlorothiazide',
          'espironolactona': 'spironolactone', 'cefalexina': 'cephalexin', 'ciclosporina': 'cyclosporine',
          'carbonato de litio': 'lithium carbonate', 'litio': 'lithium', 'ferro': 'iron', 'sulfato ferroso': 'ferrous sulfate',
          'cafeina': 'caffeine', 'nicotina': 'nicotine', 'morfina': 'morphine', 'codeina': 'codeine', 'insulina': 'insulin',
          'estradiol': 'estradiol', 'etinilestradiol': 'ethinyl estradiol', 'levonorgestrel': 'levonorgestrel',
          'prednisona': 'prednisone', 'prednisolona': 'prednisolone', 'dexametasona': 'dexamethasone',
          'hidrocortisona': 'hydrocortisone', 'betametasona': 'betamethasone', 'tetraciclina': 'tetracycline',
          'doxiciclina': 'doxycycline', 'eritromicina': 'erythromycin', 'claritromicina': 'clarithromycin',
          'azitromicina': 'azithromycin', 'sulfametoxazol': 'sulfamethoxazole', 'trimetoprima': 'trimethoprim',
          'metronidazol': 'metronidazole', 'tinidazol': 'tinidazole', 'omeprazol': 'omeprazole',
          'levodopa': 'levodopa', 'carbidopa': 'carbidopa', 'amitriptilina': 'amitriptyline', 'nortriptilina': 'nortriptyline',
          'haloperidol': 'haloperidol', 'clorpromazina': 'chlorpromazine', 'sinvastatina': 'simvastatin',
          'acido valproico': 'valproic acid', 'acido acetil salicilico': 'aspirin', 'acetilcisteina': 'acetylcysteine',
          'acetil cisteina': 'acetylcysteine', 'alendronato': 'alendronate', 'valproato': 'valproate', 'acido folico': 'folic acid',
          'acido ascorbico': 'ascorbic acid', 'ibuprofeno': 'ibuprofen', 'cetoprofeno': 'ketoprofen',
          'cetoconazol': 'ketoconazole', 'cetorolaco': 'ketorolac', 'diclofenaco': 'diclofenac', 'naproxeno': 'naproxen'}

SUFFIXES = [  # (Portuguese ending, English replacements) - first matching rule wins
    ('cilina', ['cillin']), ('micina', ['mycin']), ('ciclina', ['cycline']), ('floxacino', ['floxacin']),
    ('oxacino', ['oxacin']), ('sartana', ['sartan']), ('statina', ['statin']), ('dipino', ['dipine']),
    ('prazol', ['prazole']), ('azol', ['azole']), ('zol', ['zole']), ('tidina', ['tidine']), ('triptilina', ['triptyline']),
    ('umabe', ['umab']), ('imabe', ['imab']), ('ximabe', ['ximab']), ('mabe', ['mab']), ('inibe', ['inib']),
    ('cept', ['cept']), ('afila', ['afil']), ('gliptina', ['gliptin']), ('glifozina', ['gliflozin']),
    ('ina', ['ine', 'in']), ('ona', ['one']), ('ida', ['ide']), ('ato', ['ate']), ('eno', ['en']), ('ano', ['an']),
    ('ana', ['an']), ('ila', ['il']), ('ol', ['ol']), ('am', ['am']), ('il', ['il']), ('o', ['', 'e']), ('a', ['', 'e']),
    ('e', ['', 'e'])]

def core(substance):
    """'CLORIDRATO DE METFORMINA' -> 'metformina'; 'LOSARTANA POTÁSSICA' -> 'losartana'."""
    s = plain(substance)
    s = re.sub(r'\(.*?\)', ' ', s)
    s = SALT_PREFIX.sub('', s)
    words = [w for w in s.split() if w not in SALT_WORDS and not re.search(r'\d', w)]
    while words and words[-1] in ('de', 'e'): words.pop()  # 'alendronato de [sodio]' -> 'alendronato'
    return ' '.join(words).strip()

def word_candidates(word):
    out = set()
    for pt, en in SUFFIXES:
        if word.endswith(pt):
            for e in en: out.add(word[: len(word) - len(pt)] + e)
            break
    out.add(word)
    more = set()
    for w in out:  # common orthographic differences
        more |= {w.replace('f', 'ph'), w.replace('ti', 'thy') if 'tilin' in w else w, w.replace('i', 'y', 1) if w.startswith('ci') else w,
                 w.replace('qu', 'qu'), w.replace('c', 'k', 1) if w.startswith('ce') else w}
    return out | more

def candidates(substance):
    """Candidate English names (best first) for one CMED substance."""
    import pt_names
    c = core(substance)
    if not c: return []
    found = []
    for key in (c, plain(substance)):
        if key in MANUAL: found.append(MANUAL[key])
        en = pt_names.english(key)
        if en: found.append(en)
    words = c.split()
    if len(words) == 2 and words[0] == 'acido':  # 'acido valproico' -> 'valproic acid'
        found.append(re.sub(r'ico$', 'ic', words[1]) + ' acid')
    if len(words) == 1:
        found += sorted(word_candidates(words[0]), key=len)
    else:
        found.append(c)
    seen, ordered = set(), []
    for f in found:
        if f and f not in seen: seen.add(f); ordered.append(f)
    return ordered

def extrair(xlsx):
    from openpyxl import load_workbook
    wb = load_workbook(xlsx, read_only=True)
    header = [r for r in wb['Cabeçalho'].iter_rows(values_only=True) if r and r[0]]
    published = next((str(r[0]) for r in header if 'Publicada' in str(r[0])), '')
    rows = wb['Lista PMC'].iter_rows(values_only=True)
    head = {h: i for i, h in enumerate(next(rows))}
    brands = {}
    for r in rows:
        product, substance = (r[head['PRODUTO']] or '').strip(), (r[head['SUBSTÂNCIA']] or '').strip()
        kind = (r[head['TIPO DE PRODUTO (STATUS DO PRODUTO)']] or '').strip()
        if not product or not substance or plain(product) == plain(substance) or kind == 'Genérico': continue
        entry = brands.setdefault(plain(product), {'marca': ' '.join(product.split()).title(), 'substancias': set(), 'tipos': set()})
        entry['substancias'].update(s.strip() for s in substance.split(';') if s.strip())
        entry['tipos'].add(kind)
    CSV.parent.mkdir(exist_ok=True)
    with open(CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow([f'# Fonte: ANVISA/CMED, Lista de preços de medicamentos (PMC). {published} Dados públicos.'])
        w.writerow(['marca', 'substancias', 'tipos'])
        for key in sorted(brands):
            b = brands[key]
            w.writerow([b['marca'], '|'.join(sorted(b['substancias'])), '|'.join(sorted(b['tipos']))])
    print(f'{len(brands)} marcas gravadas em {CSV}')

def load():
    with open(CSV, encoding='utf-8') as f:
        rows = [r for r in csv.reader(f, delimiter=';') if r and not r[0].startswith('#')]
    return [dict(zip(rows[0], r)) for r in rows[1:]]

def pick(substance, entity, hidden, norm):
    """Reviewed translation first (manual list or pt_names); otherwise the most frequent existing candidate."""
    import pt_names
    ok = lambda x: x in entity and x not in hidden
    key = core(substance)
    for reviewed in (MANUAL.get(key), pt_names.english(key)):
        if reviewed and ok(norm(reviewed)): return norm(reviewed), entity[norm(reviewed)]
    found = [norm(x) for x in candidates(substance) if ok(norm(x))]
    if not found: return None
    best = max(found, key=lambda x: entity[x][1])
    return best, entity[best]

def aplicar(db_path):
    sys.path.insert(0, str(Path(__file__).parent))
    from foodrugs_full import norm
    import term_filter as TF
    hidden = TF.hidden('d')
    c = sqlite3.connect(db_path)
    columns = [r[1] for r in c.execute('PRAGMA table_info(_aliases)')]
    if 'source' not in columns: c.execute('ALTER TABLE _aliases ADD COLUMN source TEXT')
    c.execute("DELETE FROM _aliases WHERE source='cmed'")
    entity = {}
    for i, n, occ in c.execute('SELECT id, norm, occurrences FROM _drugs'):
        entity[n] = (i, occ)
    mapped, unmatched, added, brands_ok = {}, {}, 0, 0
    for row in load():
        brand, term = row['marca'], norm(row['marca'])
        if len(term) < 3: continue  # too short to be a safe search alias
        ids = []
        for substance in row['substancias'].split('|'):
            if substance not in mapped:
                hit = pick(substance, entity, hidden, norm)
                mapped[substance] = hit
                if not hit: unmatched[substance] = core(substance)
            if mapped[substance]: ids.append(mapped[substance][1][0])
        for i in dict.fromkeys(ids):
            added += c.execute('INSERT OR IGNORE INTO _aliases(kind, term, label, entity_id, source) VALUES (?,?,?,?,?)',
                               ('d', term, brand, i, 'cmed')).rowcount
        brands_ok += bool(ids)
    c.execute('CREATE INDEX IF NOT EXISTS _aliases_prefix ON _aliases(kind, term)')
    c.execute("INSERT OR REPLACE INTO _metadata VALUES ('cmed_brands', ?)",
              (json.dumps({'brands': brands_ok, 'aliases': added, 'substances_mapped': sum(bool(v) for v in mapped.values()),
                           'substances_unmatched': len(unmatched), 'source': 'ANVISA/CMED lista PMC'}),))
    c.commit(); c.close()
    total = len(load())
    report = {'marcas_no_csv': total, 'marcas_pesquisaveis': brands_ok, 'aliases_inseridos': added,
              'substancias_mapeadas': sum(bool(v) for v in mapped.values()), 'substancias_sem_correspondencia': len(unmatched),
              'exemplos_sem_correspondencia': sorted(unmatched.values())[:200]}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'exemplos_sem_correspondencia'}, ensure_ascii=False))
    return report

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if len(sys.argv) < 2 or sys.argv[1] not in ('extrair', 'aplicar'): raise SystemExit(__doc__)
    if sys.argv[1] == 'extrair': extrair(sys.argv[2])
    else:
        sys.path.insert(0, str(Path(__file__).parent))
        import foodrugs_store
        aplicar(sys.argv[2] if len(sys.argv) > 2 else foodrugs_store.PATH)
