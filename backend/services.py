import uuid, unicodedata
from sqlalchemy import select
from rapidfuzz import fuzz
from models import Drug, Food, Dataset, Interaction

def uid():
    return str(uuid.uuid4())

def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.lower().strip()) if not unicodedata.combining(c))

def library(db, term='', drug_id=None, offset=0, limit=12):
    rows = db.execute(select(Interaction, Drug, Food, Dataset)
        .join(Drug, Interaction.drug_id == Drug.id)
        .join(Food, Interaction.food_id == Food.id)
        .join(Dataset, Interaction.dataset_id == Dataset.id)
        .where(Dataset.active == True)).all()
    groups, foods, sources = {}, set(), set()
    for item, drug, food, dataset in rows:
        foods.add(food.id)
        sources.add(item.data.get('reference_url', ''))
        group = groups.setdefault(drug.id, {'id':drug.id, 'name':drug.name,
            'aliases':drug.aliases, 'foods':{}, 'search':[drug.name, *drug.aliases]})
        group['foods'][food.id] = {'id':food.id, 'name':food.name}
        group['search'].extend([food.name, *food.aliases])
    counts = {'drugs':len(groups), 'foods':len(foods), 'associations':len(rows), 'sources':len(sources - {''})}
    term = normalize(term)
    found = [g for g in groups.values() if (not drug_id or g['id'] == drug_id)
             and (not term or any(term in normalize(s) for s in g['search']))]
    found.sort(key=lambda g:normalize(g['name']))
    return {'counts':counts, 'total':len(found), 'offset':offset, 'limit':limit,
        'items':[{'id':g['id'], 'name':g['name'], 'aliases':g['aliases'],
            'foods':sorted(g['foods'].values(), key=lambda f:normalize(f['name']))}
            for g in found[offset:offset+limit]]}

def search_catalog(db, model, term):
    # Suggestions contain only entities linked to the active dataset.
    term = normalize(term)
    found = []
    entity_column = Interaction.drug_id if model is Drug else Interaction.food_id
    active_ids = select(entity_column).join(Dataset).where(Dataset.active == True)
    for row in db.scalars(select(model).where(model.id.in_(active_ids))):
        score = max((100 if term in normalize(x) else fuzz.WRatio(term, normalize(x))) for x in [row.name, *row.aliases]) if term else 100
        if score >= 65:
            found.append({'id': row.id, 'name': row.name, 'score': round(score)})
    return sorted(found, key=lambda x: (-x['score'], x['name']))[:12]

def adjusted_risk(base, profile, flags):
    if base is None:
        return None, []
    reasons = []
    if profile.get('hepatic_insufficiency') and flags.get('cyp450'):
        reasons.append('Insuficiência hepática e metabolismo por CYP450 (+1)')
    if profile.get('renal_stage', 0) >= 3 and flags.get('renal_excretion'):
        reasons.append('Doença renal em estágio ≥ 3 e excreção renal (+1)')
    if (profile.get('age') or 0) >= 65 and len({normalize(x) for x in profile.get('medications', []) if x.strip()}) >= 3:
        reasons.append('Idade ≥ 65 anos e uso de pelo menos 3 medicamentos (+1)')
    if profile.get('alcohol_frequency', 0) >= 4 and flags.get('hepatotoxic'):
        reasons.append('Álcool ≥ 4 vezes/semana e medicamento hepatotóxico (+1)')
    return min(2, max(0, base + len(reasons))), reasons

def import_dataset(db, payload):
    dataset = Dataset(id=uid(), version=payload.version, source=payload.source, count=len(payload.rows))
    for old in db.scalars(select(Dataset).where(Dataset.active == True)):
        old.active = False
    db.add(dataset)
    db.flush()
    for row in payload.rows:
        drug = db.scalar(select(Drug).where(Drug.name == row.drug.strip()))
        if not drug:
            drug = Drug(id=uid(), name=row.drug.strip(), aliases=row.drug_aliases, flags={})
            db.add(drug)
        else:
            drug.aliases = list(dict.fromkeys([*drug.aliases, *row.drug_aliases]))
        food = db.scalar(select(Food).where(Food.name == row.food.strip()))
        if not food:
            food = Food(id=uid(), name=row.food.strip(), aliases=row.food_aliases)
            db.add(food)
        else:
            food.aliases = list(dict.fromkeys([*food.aliases, *row.food_aliases]))
        db.flush()
        data = row.model_dump()
        if not row.reviewed or not row.risk_basis.strip():
            data['base_risk'] = None
        db.add(Interaction(id=uid(), drug_id=drug.id, food_id=food.id, dataset_id=dataset.id, data=data))
    db.flush()
    return dataset

def build_result(db, drug, food, profile):
    rows = db.execute(select(Interaction, Dataset).join(Dataset).where(Interaction.drug_id == drug.id, Interaction.food_id == food.id, Dataset.active == True)).all()
    evidence = []
    for item, dataset in rows:
        data = item.data
        risk, reasons = adjusted_risk(data.get('base_risk'), profile, data)
        evidence.append({**data, 'id': item.id, 'adjusted_risk': risk, 'modifiers': reasons, 'version': dataset.version, 'source': dataset.source})
    known = [e['adjusted_risk'] for e in evidence if e['adjusted_risk'] is not None]
    return {'drug': drug.name, 'food': food.name, 'drug_id': drug.id, 'food_id': food.id, 'found': bool(evidence), 'risk': max(known) if known else None, 'unclassified': any(e['adjusted_risk'] is None for e in evidence), 'evidence': evidence, 'personalized': any(e['modifiers'] for e in evidence), 'heuristic': 'Regras acadêmicas do TCC, não validadas clinicamente.', 'notice': 'Ausência de registro ou classificação não comprova segurança. Não altere seu tratamento sem orientação profissional.'}
