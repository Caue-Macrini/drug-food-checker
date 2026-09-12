import uuid, unicodedata
from sqlalchemy import select
from rapidfuzz import fuzz
from models import Drug, Food, Dataset, Interaction

def uid():
    return str(uuid.uuid4())

def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.lower().strip()) if not unicodedata.combining(c))

def search_catalog(db, model, term):
    # Catalog is cached by the application per dataset; only suggestions are fuzzy,
    # the submitted consultation must use an explicitly selected entity ID.
    term = normalize(term)
    found = []
    for row in db.scalars(select(model)):
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
    if (profile.get('age') or 0) >= 65 and len(set(profile.get('medications', []))) >= 3:
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
        food = db.scalar(select(Food).where(Food.name == row.food.strip()))
        if not food:
            food = Food(id=uid(), name=row.food.strip(), aliases=row.food_aliases)
            db.add(food)
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
    return {'drug': drug.name, 'food': food.name, 'drug_id': drug.id, 'food_id': food.id, 'found': bool(evidence), 'risk': max(known) if known else None, 'unclassified': any(e['adjusted_risk'] is None for e in evidence), 'evidence': evidence, 'personalized': bool(profile), 'heuristic': 'Regras acadêmicas do TCC, não validadas clinicamente.', 'notice': 'Ausência de registro ou classificação não comprova segurança. Não altere seu tratamento sem orientação profissional.'}
