import pytest
import risk_rules as R
from foodrugs_full import build
from index_foodrugs import index
from classify_foodrugs import classify_database
import foodrugs_store as store

PK_SENTENCE = ('Notwithstanding the mutual interference of theophylline and caffeine metabolism, the reduction in apparent total body '
               'clearance of theophylline by 29% indicated a pronounced influence of concomitant administration of caffeine.')

@pytest.mark.parametrize('sentence,category', [
    (PK_SENTENCE, R.INTERACTION),
    ('Aminophylline shortages led us to compare intravenous aminophylline with IV and oral caffeine during stress testing.', R.MENTION),
    ('Grapefruit juice did not alter the pharmacokinetics of fexofenadine in healthy volunteers.', R.NO_EFFECT),
    ('Patients taking warfarin should avoid large changes in vitamin K intake.', R.INTERACTION),
    ('The strengthened H-bonding interactions between positively charged amines and phosphonate group.', R.MENTION),
    ('The cortisol concentration decreased after surgery in the magnesium group but did not change in the control group.', R.MENTION),
    ('High-concentration oxygen vacancies enhance the diffusion coefficient of lithium ions in batteries.', R.MENTION),
    ('The extent of bioavailability of ciprofloxacin was reduced by 30% to 36% by milk and yogurt (p less than 0.05).', R.INTERACTION),
    ('It is well known that grapefruit juice (GFJ) elevates the blood tacrolimus (TAC) concentration.', R.INTERACTION),
    ('Warfarin has numerous potential drug interactions and modulation of effect by alcohol and foods containing vitamin K.', R.INTERACTION),
    ('A patient developed metformin-associated lactic acidosis due to the simultaneous ingestion of an overdose of metformin and alcohol.', R.INTERACTION),
    ('The CNS-depressant effect of propoxyphene is additive with that of other CNS depressants, including alcohol.', R.INTERACTION),
    ('In animals, buspirone has been shown to alter drinking preference from alcohol to water.', R.MENTION),
])
def test_sentence_rules(sentence, category):
    assert R.classify(sentence)[0] == category

def test_flags_and_mechanisms():
    category, flags, mechanisms = R.classify('Coadministration with grapefruit juice may increase the plasma concentrations of simvastatin via CYP3A4 inhibition.')
    assert category == R.INTERACTION and flags & R.PK and flags & R.INCREASE and 'cyp' in mechanisms
    _, flags, mechanisms = R.classify('Patients taking warfarin should avoid large changes in vitamin K intake.')
    assert flags & R.STRONG and 'vitamina_k' in mechanisms

def test_curated_severity_uses_the_section_header():
    doc = 'Moderate Food Interaction||MONITOR:  Food delays absorption. Major Food Interaction||GENERALLY AVOID:  Alcohol potentiates CNS depression.'
    assert R.curated_severity(doc, 10) == (1, 'Moderate · MONITOR')
    assert R.curated_severity(doc, doc.index('Alcohol')) == (2, 'Major · GENERALLY AVOID')
    assert R.curated_severity('Plain abstract text.', 0) == (None, '')

def test_curated_severity_only_for_the_monograph_drug_and_section_food():
    doc = 'Major Food Interaction||GENERALLY AVOID:  Grapefruit juice may increase the plasma concentrations of amiodarone. Patients should limit carbohydrate and monitor calcium.'
    link = 'https://www.drugs.com/food-interactions/amiodarone,pacerone.html'
    start = doc.index('Patients')
    assert R.curated_severity(doc, 10, link, 'Amiodarone', 'Grapefruit')[0] == 2
    assert R.curated_severity(doc, start, link, 'Amiodarone', 'carbohydrate') == (None, '')   # not the section's food
    assert R.curated_severity(doc, start, link, 'BUN', 'Grapefruit') == (None, '')            # not the monograph's drug

def test_pair_level_rules():
    assert R.pair_level(2, 0, 0, 0) == 2          # curated severity has priority
    assert R.pair_level(None, 0, 0, 0) == 0       # only mentions
    assert R.pair_level(None, 1, 0, 0) == 1       # one document describes an interaction
    assert R.pair_level(None, 3, 2, 0) == 2       # two documents with strong warnings
    assert R.pair_level(None, 1, 0, 2) == 0       # no-effect studies outnumber interaction documents

def test_drug_flags():
    assert R.drug_flags('Simvastatin', '') == {'cyp450': True, 'renal_excretion': False, 'hepatotoxic': False}
    assert R.drug_flags('unknown', 'cyp,absorcao')['cyp450']

DOCS = [
    ('Grapefruit juice increased the plasma concentrations of simvastatin in healthy volunteers.', 'https://pubmed.ncbi.nlm.nih.gov/1/', 'Grapefruit', 'simvastatin'),
    ('Simvastatin and grapefruit were both listed in the dietary questionnaire.', 'https://pubmed.ncbi.nlm.nih.gov/2/', 'grapefruit', 'Simvastatin'),
    ('Major Food Interaction||GENERALLY AVOID:  Alcohol may potentiate the CNS depressant effects of fentanyl.', 'https://www.drugs.com/food-interactions/fentanyl.html', 'Alcohol', 'fentanyl'),
    ('Milk did not alter the pharmacokinetics of drugx in healthy volunteers.', 'https://pubmed.ncbi.nlm.nih.gov/3/', 'milk', 'drugx'),
]

@pytest.fixture
def classified_db(tmp_path, monkeypatch):
    def q(v): return "'" + v.replace("'", "\\'") + "'"
    tm = ','.join(f'({i},{i},0,{len(d)},{q(food)},{q(drug)})' for i, (d, _, food, drug) in enumerate(DOCS))
    texts = ','.join(f'({i},{q(d)},{q(link)},NULL)' for i, (d, link, _, _) in enumerate(DOCS))
    dump = tmp_path / 'source.sql'; db = tmp_path / 'full.sqlite'
    dump.write_text(f'''CREATE TABLE `TM_interactions` (
  `TM_interactions_ID` int NOT NULL,
  `texts_ID` int NOT NULL,
  `start_index` int DEFAULT NULL,
  `end_index` int DEFAULT NULL,
  `food` varchar(150),
  `drug` varchar(150)
) ENGINE=InnoDB;
INSERT INTO `TM_interactions` VALUES {tm};
CREATE TABLE `texts` (
  `texts_ID` int,
  `document` text,
  `link` text,
  `citation` text
) ENGINE=InnoDB;
INSERT INTO `texts` VALUES {texts};
-- Dump completed on 2023-07-28 11:48:01
''', encoding='utf-8')
    build(dump, db, verify=False); index(db); summary = classify_database(db)
    monkeypatch.setattr(store, 'PATH', db)
    return summary

def ids(drug, food):
    return store.search('d', drug)[0]['id'], store.search('f', food)[0]['id']

def test_classification_summary(classified_db):
    assert classified_db['records'] == 4 and classified_db['curated_pairs'] == 1
    assert classified_db['categories'] == {'mencao': 1, 'interacao': 2, 'sem_efeito': 1}

def test_result_has_color_answer_reasons_and_interaction_first(classified_db):
    result = store.evidence(*ids('simvastatin', 'grapefruit'))
    assert result['risk'] == 1 and result['base_risk'] == 1 and result['verdict']['title'] == 'Atenção'
    assert result['evidence'][0]['signal'] == 'interacao' and result['evidence'][1]['signal'] == 'mencao'
    assert 'aumento da concentração no sangue' in result['explanation']
    assert result['rules_version'] == R.RULES_VERSION and result['personalization'] == {'requested': False, 'profile_filled': False}
    assert any('1 de 2 trechos (1 documento) descreve interação' in b for b in result['basis'])
    assert result['stats']['interaction_docs'] == 1 and not result['modifiers']

def test_curated_major_is_red(classified_db):
    result = store.evidence(*ids('fentanyl', 'alcohol'))
    assert result['risk'] == 2 and result['verdict']['title'] == 'Risco elevado'
    assert 'Major · GENERALLY AVOID' in result['basis'][0]

def test_no_effect_study_is_green(classified_db):
    result = store.evidence(*ids('drugx', 'milk'))
    assert result['risk'] == 0 and 'não observaram interação' in result['verdict']['answer']

def test_absent_pair_is_green_with_caveat_and_no_modifiers(classified_db):
    profile = {'age': 70, 'medications': ['a', 'b', 'c']}
    result = store.evidence(*ids('simvastatin', 'milk'), profile=profile)
    assert not result['found'] and result['risk'] == 0 and not result['modifiers']
    assert result['verdict']['title'] == 'Sem interação conhecida' and 'não garante' in result['verdict']['recommendation']

def test_profile_modifiers_follow_tcc_table_2(classified_db):
    elderly = {'age': 70, 'medications': ['a', 'b', 'c']}
    result = store.evidence(*ids('simvastatin', 'grapefruit'), profile=elderly)
    assert result['base_risk'] == 1 and result['risk'] == 2 and result['personalized']
    assert any('Idade' in m for m in result['modifiers'])
    assert result['basis'][-1] == 'Perfil clínico (Tabela 2 do TCC): +1 → Risco elevado.'
    hepatic = {'hepatic_insufficiency': True}
    assert store.evidence(*ids('simvastatin', 'grapefruit'), profile=hepatic)['risk'] == 2   # simvastatin: CYP450
    capped = store.evidence(*ids('fentanyl', 'alcohol'), profile={**elderly, **hepatic})
    assert capped['risk'] == 2                                                               # limited to 0-2

def test_biomarker_terms_need_explicit_interaction_wording():
    sentence = 'Simvastatin reduced plasma cholesterol levels in patients with hyperlipidemia.'
    category, flags, _ = R.classify(sentence)
    assert category == R.INTERACTION
    assert R.adjust_for_terms(category, flags, 'CHOLESTEROL') == R.MENTION
    assert R.adjust_for_terms(category, flags, 'Grapefruit') == R.INTERACTION
    category, flags, _ = R.classify('Metformin should be taken with meals to reduce interaction with glucose absorption.')
    assert R.adjust_for_terms(category, flags, 'D-Glucose') == R.INTERACTION

def test_modifiers_do_not_create_an_interaction(classified_db):
    elderly = {'age': 70, 'medications': ['a', 'b', 'c'], 'hepatic_insufficiency': True}
    result = store.evidence(*ids('drugx', 'milk'), profile=elderly, personalize=True)
    assert result['base_risk'] == 0 and result['risk'] == 0 and not result['modifiers']
    assert result['personalization'] == {'requested': True, 'profile_filled': True}

def test_pair_missing_from_risk_tables_is_shown_unclassified(classified_db):
    import sqlite3
    with sqlite3.connect(store.PATH) as c:
        c.execute('DELETE FROM _pair_risk')
    result = store.evidence(*ids('simvastatin', 'grapefruit'))
    assert result['found'] and result['risk'] is None and result['unclassified']

@pytest.mark.parametrize('sentence,category', [
    ('Taken together, these results suggest a role for caffeine and taurine in memory in adults.', R.MENTION),
    ('A randomized double-blind trial of beta-blockers and raisins in patients.', R.MENTION),
    ('Patients were monitored weekly and samples were analysed separately.', R.MENTION),
    ('Rats were tested in the passive avoidance task after ethanol and the drug.', R.MENTION),
    ('There was no effect of TI or exogenous protease or their interaction on the digestibility of phosphorus.', R.MENTION),
    ('Pretreatment with enoxacin decreased the total clearance of theophylline by 50%, but there were no significant changes in volume of distribution.', R.INTERACTION),
    ('Garlic may enhance the pharmacological effect of anticoagulants such as warfarin.', R.INTERACTION),
    ('Simvastatin should not be coadministered with grapefruit juice.', R.INTERACTION),
])
def test_review_regressions(sentence, category):
    assert R.classify(sentence)[0] == category

def test_listed_terms_are_not_an_interaction_between_them():
    sentence = 'One of them is to avoid coffee and caffeine prior the test in patients.'
    category, flags, _ = R.classify(sentence)
    assert category == R.INTERACTION
    assert R.adjust_for_terms(category, flags, 'Coffee', 'Caffeine', sentence) == R.MENTION
    pk = 'Grapefruit juice and simvastatin: grapefruit increased the plasma concentrations of simvastatin in volunteers.'
    category, flags, _ = R.classify(pk)
    assert R.adjust_for_terms(category, flags, 'Grapefruit', 'Simvastatin', pk) == R.INTERACTION

def test_food_that_contains_the_drug_is_not_an_interaction():
    sentence = 'Caffeine intake should be limited to 200 mg per day (about two small cups of coffee) in pregnant women.'
    category, flags, _ = R.classify(sentence)
    assert R.adjust_for_terms(category, flags, 'Coffee', 'Caffeine', sentence) == R.MENTION
    assert R.adjust_for_terms(category, flags, 'Coffee', 'Lithium', sentence) == category
