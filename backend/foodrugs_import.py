"""Read the official MySQL dump as DATA, without executing SQL.

python foodrugs_import.py FinalFooDrugs_v4.sql --output ../data/foodrugs.json --limit 5000
The app accepts 10,000 normalized records per version through the admin UI.
No transcriptomic score or NLP association is converted into clinical severity.
"""
import argparse, json, re
from pathlib import Path
from schemas import ImportDataset

ROW = re.compile(r"\((\d+),(\d+),(?:\d+|NULL),(?:\d+|NULL),('(?:[^'\\]|\\.)*'|NULL),('(?:[^'\\]|\\.)*'|NULL)\)")

def sql_string(value):
    if value == 'NULL':
        return ''
    escapes = {'0':'\0','n':'\n','r':'\r','t':'\t','Z':'\x1a'}
    return re.sub(r'\\(.)', lambda m: escapes.get(m[1], m[1]), value[1:-1])

def normalized_rows(lines, limit):
    count = 0
    for line in lines:
        if not line.startswith('INSERT INTO `TM_interactions` VALUES '):
            continue
        for record_id, text_id, food, drug in ROW.findall(line):
            food, drug = sql_string(food).strip(), sql_string(drug).strip()
            if not food or not drug:
                continue
            yield dict(drug=drug,food=food,source_record_id=record_id,source_text_id=text_id,
                base_risk=None,reviewed=False,risk_basis='',
                evidence_status='Associação potencial extraída automaticamente por PLN; requer revisão humana',
                mechanism='Mecanismo não estabelecido por este registro de mineração de texto.',
                explanation='A FooDrugs identificou uma associação textual potencial entre estes termos. O registro pode conter erro de extração e não comprova uma interação clínica.',
                reference_title=f'FooDrugs 4.0.0 · TM_interactions {record_id} · texto {text_id}',
                reference_url='https://doi.org/10.5281/zenodo.8192515')
            count += 1
            if count >= limit:
                return

def convert(source, output, limit=5000, version='foodrugs-4.0.0-normalizada'):
    if not 1 <= limit <= 10000:
        raise ValueError('Limite deve ficar entre 1 e 10000 registros')
    with open(source, encoding='utf-8') as handle:
        rows = list(normalized_rows(handle, limit))
    if not rows:
        raise ValueError('Nenhum INSERT TM_interactions compatível encontrado')
    payload=ImportDataset(version=version, source='FooDrugs 4.0.0 · IMDEA Food Institute · CC BY 4.0 · https://doi.org/10.5281/zenodo.8192515',rows=rows)
    Path(output).write_text(payload.model_dump_json(indent=2),encoding='utf-8')
    return len(rows)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dump')
    parser.add_argument('--output', required=True)
    parser.add_argument('--limit', type=int, default=5000)
    parser.add_argument('--version', default='foodrugs-4.0.0-normalizada')
    args=parser.parse_args()
    print(f'{convert(args.dump,args.output,args.limit,args.version)} registros convertidos; revisar antes de ativar na interface.')
