"""Explicit, auditable rules that derive the TCC risk scale (0-2) from FooDrugs evidence.

FooDrugs records where a drug and a food co-occur in a sentence; it does not grade
severity. These rules read each source sentence and classify what it says. They are
deterministic regular expressions, not a trained model, so every color can be traced
back to the sentences and the rule that produced it (TCC, p. 31).
"""
import re

RULES_VERSION = 'regras-evidencia-1.5'

# Sentence categories stored in _tm_signal.category.
MENTION, INTERACTION, NO_EFFECT = 0, 1, 2
# Bit flags stored in _tm_signal.flags.
PK, PD, WARNING, STRONG, EXPLICIT, HARM, INCREASE, DECREASE = 1, 2, 4, 8, 16, 32, 64, 128

def _rx(pattern):
    return re.compile(pattern, re.I)

# Change verbs with explicit word endings, so "double-blind", "beta-blockers" or "raisins" do not match.
_UP = r'increas(e|es|ed|ing)|elevat(e|es|ed|ing|ion)|rais(e|es|ed|ing)|enhanc(e|es|ed|ing|ement)|doubl(e|es|ed|ing)(?!-blind)|prolong(s|ed|ing|ation)?'
_DOWN = (r'decreas(e|es|ed|ing)|reduc(e|es|ed|ing|tion|tions)|lower(s|ed|ing)?|diminish(es|ed|ing)?|impair(s|ed|ing|ment)?|'
         r'halv(e|es|ed|ing)|chelat(e|es|ed|ing|ion)|block(s|ed|ing)?|accelerat(e|es|ed|ing|ion)')
_OTHER = (r'alter(s|ed|ing|ation|ations)?|affect(s|ed|ing)?|inhibit(s|ed|ing|ion)?|induc(e|es|ed|ing|tion)|delay(s|ed|ing)?|'
          r'interfer(e|es|ed|ing|ence)|slow(s|ed|ing)?')
PK_CHANGE = _rx(rf'\b({_UP}|{_DOWN}|{_OTHER})\b')
INCREASE_WORDS = _rx(rf'\b({_UP}|inhibit(s|ed|ing|ion)?)\b')
DECREASE_WORDS = _rx(rf'\b({_DOWN}|induc(e|es|ed|ing|tion))\b')
# Pharmacokinetic terms specific enough to stand on their own (no human-use context word needed).
PK_STRONG = _rx(r'\b(bioavailab\w*|clearance|auc\d*|c\s?max|half-?\s?li[fv]e|pharmacokinetic\w*|area under the (plasma )?concentration)\b')
PK_TARGET = _rx(r'\b((plasma|serum|blood|peak|trough|steady[- ]state|maximum|systemic|drug)\s+([\w()-]+\s+){0,3}(concentrations?|levels?)|bioavailab\w*|clearance|auc\d*|c\s?max|half-?\s?li[fv]e|absorption|absorbed|exposure|cyp\s?\d\w*|cytochrome p-?450|p-?glycoprotein|p-?gp|oatp\w*|first-?pass|pharmacokinetic\w*|metabolism of)\b')
PD_CHANGE = _rx(r'\b(potentiat\w*|additive|synergi\w*|antagoni[sz](e|es|ed|ing)|antagonism|counteract\w*|(enhanc|reduc|diminish|decreas|block|revers|inhibit|abolish|attenuat|blunt|increas|modulat)\w*\s+(the\s+|its\s+|their\s+)?(\w+[\s-]+){0,3}(effects?|actions?|efficacy|activity|response))\b')
HARM_RX = _rx(r'\b(bleeding|ha?emorrhag\w*|toxicity|hepatotox\w*|nephrotox\w*|hypotension|hypertensive (crisis|reaction)|hyperkalemi\w*|hyperkalaemi\w*|serotonin syndrome|qt[- ]prolong\w*|cns depression|central nervous system depression|respiratory depression|disulfiram|lactic acidosis|arrhythmi\w*|seizures?|rhabdomyolysis)\b')
RISK_RX = _rx(r'\b(risk of|may (cause|result in|lead to)|can (cause|result in|lead to)|resulting in|leading to|associated with)\b')
# Explicit combined-use wording. "Taken together" and "together with" are left out: in abstracts
# they usually mean "in summary" or "along with".
EXPLICIT_RX = _rx(r'\b(interact(ion|ions|s|ed)?\s+(with|between)|(drug|food)[- ](food|drug|nutrient)[- ]interactions?|co-?administ\w*|concomitant\w*|co-?ingest\w*|when (taken|given|administered|combined|consumed) (with|together)|(taken|given|administered) together with|in combination with|food effect|(simultaneous|concurrent|combined|joint)\w*\s+(\w+\s+){0,2}(use|intake|ingestion|administration|consumption))')
# Usage recommendations about the combination. Study-method words ("patients were monitored",
# "analysed separately") are excluded on purpose.
WARNING_RX = _rx(r'\b(avoid(s|ed|ing)?\b(?! avoidance)|should not|must not|contraindicat\w*|do not (take|consume|drink|eat|use|combine)|not be (taken|used|combined|given)|is recommended|are recommended|should be (taken|avoided|monitored|separated|limited|restricted)|with caution|caution\w* (is|should|when)|close(ly)? monitor\w*|monitor\w* (of )?(the )?(plasma|serum|blood|inr|levels?|concentrations?|potassium|glucose)|separate (the )?(doses?|administration|intake)|taken separately|\d+\s*(hours?|h) (apart|before|after)|empty stomach|dose adjustment|adjust\w* (the )?dos\w*)')
NEGATED_ADVICE_RX = _rx(r'\b(need not|no need to|not necessary to|does not need to|do not need to|unnecessary to|passive avoidance|avoidance (test|task|learning|behaviou?r|response))\b')
STRONG_RX = _rx(r'\b(serious|severe|fatal|life-?threatening|dangerous|death|deaths)\b')
RECOMMEND_STRONG_RX = _rx(r'\b(avoid(s|ed|ing)?\b(?! avoidance)|contraindicat\w*|should not|must not|do not (take|consume|drink|combine)|not be (taken|used|combined|given))')
NO_EFFECT_RX = _rx(r'\b(no (statistically |clinically |significant |relevant |important |major |apparent |meaningful |detectable )*(effect|interaction|change|difference|influence|alteration|impact)s?|did not (significantly |substantially |markedly )?(affect|alter|change|influence|modify|increase|decrease|reduce|interact)|(was|were|is|are) not (significantly |substantially )?(affected|altered|changed|influenced|modified)|unaffected|unaltered|unchanged|not clinically (significant|relevant|important)|no evidence (of|for) (an? )?interaction|lack of (an? )?(significant )?interaction|without (significantly )?(changing|altering|affecting))\b')

# Human-use context: separates intake/clinical sentences from bench biology (cells, batteries...).
CONTEXT_RX = _rx(r'\b(patients?|subjects?|volunteers?|participants?|healthy|clinical\w*|men|women|humans?|adults?|elderly|children|dos(e|es|ing|age)|mg|g/day|oral\w*|administ\w*|intake|consum\w*|ingest\w*|juices?|meals?|diet\w*|foods?|fed|fasting|fasted|supplement\w*|drink\w*|beverages?|users?|therapy|tablets?|capsules?|alcohol|ethanol|wine|beer|grapefruit|coffee|tea|milk|dairy|cheese|yog[h]?urt|fruits?|vegetables?)\b')
# Drug-label style modal statements ("X may increase the plasma concentrations of Y") are
# pharmacological claims about combined use even without a context word.
MODAL_RX = _rx(r'\b(may|might|can|could) (significantly |substantially |markedly )?(increase|decrease|enhance|reduce|potentiate|antagoni[sz]e|inhibit|impair|alter|affect|delay|diminish|interfere)\b')
# Animal or in vitro experiments with no human subject are not evidence about combined use by people.
ANIMAL_RX = _rx(r'\b(rats?|mice|mouse|murine|rabbits?|dogs?|pigs?|piglets?|cattle|cows?|sheep|chickens?|hens?|broilers?|fish|zebrafish|monkeys?|guinea pigs?|hamsters?|in vitro|cultured|cell lines?|cells|neurons?|slices|homogenates?|explants?|bacteria|strains?|larvae|insects?|bees?|plants?|seedlings?|leaves|animals?|livestock|poultry|calves|lambs|pups|weaned|laying|feed intake|algae|daphnia|worms?|nematodes?|yeast)\b')
HUMAN_RX = _rx(r'\b(patients?|volunteers?|humans?|men|women|subjects?|participants?|children|adults?|elderly|healthy|clinical\w*|case reports?|users?)\b')
# Chemistry/materials vocabulary: "interaction" here is molecular bonding, not drug-food use.
BENCH_RX = _rx(r'\b(h-?bond\w*|hydrogen[- ]bond\w*|electrostatic|hydrophobic|van der waals|crystal\w*|docking|nanoparticles?|-nps|adsorption|polymer\w*|density functional|conductivity|batter(y|ies)|membrane potential|binding energy)\b')
INTERACT_RX = _rx(r'\binteract\w*')
# Statistical interaction (ANOVA factors) is not a pharmacological interaction.
STATS_RX = _rx(r'\b(their interactions?|interaction (terms?|effects?)|two-way|three-way|anova|interactions? between [\w-]+ (source|treatment|group|level|factor|sex|time)s?)\b')

# Mechanism detectors: (code, pattern, plain-language explanation in Portuguese).
MECHANISMS = [
    ('cyp', _rx(r'\b(cyp\s?\d\w*|cytochrome p-?450|cyp450)'), 'interferência nas enzimas do fígado e do intestino (citocromo P450) que processam o medicamento'),
    ('transporte', _rx(r'\b(p-?glycoprotein|p-?gp|oatp\w*|transporters?)\b'), 'interferência nas proteínas que transportam o medicamento para dentro ou para fora das células'),
    ('quelacao', _rx(r'\b(chelat\w*|complex(es|ation)? with (calcium|iron|magnesium|zinc)|divalent|polyvalent cations?)'), 'minerais (como cálcio, ferro ou magnésio) se ligam ao medicamento no intestino e reduzem sua absorção'),
    ('absorcao', _rx(r'\b(absorption|absorbed|bioavailab\w*|gastric emptying|empty stomach)'), 'mudança na quantidade do medicamento que o corpo consegue absorver'),
    ('vitamina_k', _rx(r'\bvitamin k\b'), 'a vitamina K se opõe ao efeito de anticoagulantes como a varfarina'),
    ('tiramina', _rx(r'\btyramine\b'), 'a tiramina pode elevar muito a pressão arterial com certos medicamentos'),
    ('potassio', _rx(r'\b(potassium|hyperkal\w*)'), 'a combinação pode elevar o potássio no sangue'),
    ('snc', _rx(r'\b(cns|central nervous system|sedat\w*|drowsiness)\b'), 'os dois agem sobre o sistema nervoso central e seus efeitos podem se somar'),
    ('sangramento', _rx(r'\b(bleeding|ha?emorrhag\w*|anticoagul\w*|antiplatelet|inr)\b'), 'a combinação pode alterar a coagulação do sangue'),
]

PK_MECHANISMS = {'cyp', 'transporte', 'quelacao', 'absorcao'}
PD_MECHANISMS = {'vitamina_k', 'tiramina', 'potassio', 'snc', 'sangramento'}

SEVERITY_HEADER = re.compile(r'(Major|Moderate|Minor) (Food|Drug) Interaction\|\|([A-Z][A-Z ]+:)?')
CURATED_LEVEL = {'Major': 2, 'Moderate': 1, 'Minor': 1}

def _words(term):
    return [w for w in re.split(r'[^a-z0-9]+', (term or '').lower()) if len(w) >= 3]

def curated_severity(document, start, link='', drug='', food=''):
    """Severity of the Drugs.com monograph section that contains the sentence, if any.

    The declared severity concerns the monograph's drug (in the page address) and the food
    named in the opening sentence of the section. Other terms extracted from the same text
    (lab values, other nutrients) do not inherit it. Matching is by whole words.
    """
    headers = list(SEVERITY_HEADER.finditer(document or ''))
    found = None
    for i, m in enumerate(headers):
        if m.start() > max(start, 0):
            break
        found = (m, headers[i + 1].start() if i + 1 < len(headers) else len(document))
    if not found:
        return None, ''
    m, section_end = found
    slug = set(re.split(r'[^a-z0-9]+', (link or '').lower().rsplit('/', 1)[-1]))
    opening = set(re.split(r'[^a-z0-9]+', document[m.end():section_end].split('. ', 1)[0].lower()))
    if drug and not any(w in slug for w in _words(drug)):
        return None, ''
    if food and not any(w in opening or w + 's' in opening for w in _words(food)):
        return None, ''
    return CURATED_LEVEL[m.group(1)], (m.group(1) + ' · ' + (m.group(3) or '').strip(' :')).strip(' ·')

def _signals(s):
    """Positive evidence in a text fragment: (flags, pk, explicit, warning)."""
    flags = 0
    pk = bool(PK_CHANGE.search(s) and PK_TARGET.search(s))
    if pk:
        flags |= PK
        if INCREASE_WORDS.search(s): flags |= INCREASE
        if DECREASE_WORDS.search(s): flags |= DECREASE
    explicit = bool(EXPLICIT_RX.search(s))
    context = bool(CONTEXT_RX.search(s) or MODAL_RX.search(s))
    if PD_CHANGE.search(s) and (context or explicit): flags |= PD
    if explicit: flags |= EXPLICIT
    if HARM_RX.search(s) and (explicit or pk or flags & PD or (RISK_RX.search(s) and context)): flags |= HARM
    warning = bool(WARNING_RX.search(s)) and not NEGATED_ADVICE_RX.search(s)
    if warning: flags |= WARNING
    # Strong warning: an explicit "avoid/contraindicated/should not" recommendation, or a
    # serious/fatal adverse effect. "Severe" alone often qualifies the disease, not the interaction.
    if (warning and RECOMMEND_STRONG_RX.search(s)) or (flags & HARM and STRONG_RX.search(s)): flags |= STRONG
    return flags, pk, explicit, warning

def classify(sentence):
    """Return (category, flags, mechanism codes) for one source sentence."""
    s = sentence or ''
    mechanisms = [code for code, rx, _ in MECHANISMS if rx.search(s)]
    context = bool(CONTEXT_RX.search(s) or MODAL_RX.search(s))
    bench = bool(BENCH_RX.search(s) or STATS_RX.search(s))
    animal_only = bool(ANIMAL_RX.search(s)) and not HUMAN_RX.search(s)
    negated = bool(NO_EFFECT_RX.search(s))
    # Mixed sentences ("decreased the clearance by 50% ... without changing the volume of
    # distribution"): look for positive evidence after removing the negated clauses.
    remainder = NO_EFFECT_RX.sub(' ', s) if negated else s
    flags, pk, explicit, warning = _signals(remainder)
    framed = (explicit or context) and not bench and INTERACT_RX.search(remainder)
    positive = framed or (not bench and (
        (pk and PK_STRONG.search(remainder)) or (warning and (context or explicit))
        or (flags & (PK | PD | HARM) and (context or explicit))))
    if animal_only and not warning:
        positive = False
    if positive:
        return INTERACTION, flags, mechanisms
    # "No effect" only counts when the sentence is about the interaction or pharmacokinetics.
    if (negated and not animal_only and not bench and (INTERACT_RX.search(s) or PK_TARGET.search(s))
            and (context or explicit or PK_STRONG.search(s))):
        return NO_EFFECT, flags, mechanisms
    return MENTION, flags, mechanisms

def pair_level(curated_level, interaction_docs, strong_docs, no_effect_docs):
    """Base risk (0-2) for a pair, from aggregated sentence classifications."""
    if curated_level is not None:
        return curated_level
    if interaction_docs == 0 or no_effect_docs > interaction_docs:
        return 0
    if strong_docs >= 2:
        return 2
    return 1

def strength(curated_level, interaction_docs):
    if curated_level is not None:
        return 'Fonte de referência com gravidade (Drugs.com)'
    if interaction_docs >= 5:
        return 'Ampla: 5 ou mais documentos descrevem a interação'
    if interaction_docs >= 2:
        return 'Moderada: 2 a 4 documentos descrevem a interação'
    if interaction_docs == 1:
        return 'Limitada: 1 documento descreve a interação'
    return 'Nenhum documento descreve interação'

def mechanism_text(codes):
    return [text for code, _, text in MECHANISMS if code in codes]

# Drug properties used by the TCC profile modifiers (Table 2). Short, explicit reference
# lists of well-known cases; a drug absent from a list simply does not trigger the modifier.
CYP450_SUBSTRATES = {'simvastatin', 'atorvastatin', 'lovastatin', 'warfarin', 'amiodarone', 'cyclosporine', 'ciclosporin',
    'tacrolimus', 'sirolimus', 'sildenafil', 'midazolam', 'triazolam', 'nifedipine', 'felodipine', 'amlodipine', 'verapamil',
    'carbamazepine', 'buspirone', 'clopidogrel', 'omeprazole', 'theophylline', 'caffeine', 'clozapine', 'quetiapine',
    'fentanyl', 'oxycodone', 'methadone', 'dronedarone', 'ivabradine', 'colchicine', 'diazepam', 'phenytoin', 'losartan'}
RENAL_EXCRETION = {'metformin', 'lithium', 'digoxin', 'gabapentin', 'pregabalin', 'allopurinol', 'enalapril', 'lisinopril',
    'captopril', 'ramipril', 'spironolactone', 'furosemide', 'hydrochlorothiazide', 'ciprofloxacin', 'levofloxacin',
    'amoxicillin', 'vancomycin', 'gentamicin', 'methotrexate', 'dabigatran', 'atenolol', 'sotalol', 'acyclovir',
    'valacyclovir', 'tenofovir', 'sitagliptin'}
HEPATOTOXIC = {'acetaminophen', 'paracetamol', 'isoniazid', 'rifampicin', 'rifampin', 'methotrexate', 'ketoconazole',
    'valproate', 'valproic acid', 'amiodarone', 'nitrofurantoin', 'diclofenac', 'leflunomide', 'azathioprine', 'terbinafine',
    'carbamazepine', 'phenytoin', 'nevirapine', 'sulfasalazine', 'duloxetine', 'naltrexone', 'tolcapone', 'disulfiram'}

def drug_flags(name, mechanisms):
    n = (name or '').strip().lower()
    return {'cyp450': n in CYP450_SUBSTRATES or 'cyp' in mechanisms,
            'renal_excretion': n in RENAL_EXCRETION, 'hepatotoxic': n in HEPATOTOXIC}

LEVEL_NAMES = {0: 'Sem interação identificada', 1: 'Atenção', 2: 'Risco elevado'}

def verdict(level, base, found, drug, food, stats):
    """Plain-language answer shown at the top of the result."""
    if not found:
        return {'title': 'Sem interação conhecida',
                'answer': f'A base FooDrugs não tem registros de {drug} com {food}.',
                'recommendation': 'Não encontrar registro não garante que a combinação seja segura. Em caso de dúvida, pergunte a um médico ou farmacêutico.'}
    if level == 2:
        return {'title': 'Risco elevado',
                'answer': f'Evite consumir {food} durante o uso de {drug} sem orientação profissional.',
                'recommendation': 'Fale com seu médico ou farmacêutico antes de combinar. Não interrompa nem altere o medicamento por conta própria.'}
    if level == 1:
        return {'title': 'Atenção',
                'answer': f'Pode haver interação entre {drug} e {food}.',
                'recommendation': f'Pergunte ao seu médico ou farmacêutico se e como você pode consumir {food} durante o tratamento. Não interrompa o medicamento por conta própria.'}
    records = stats.get('records', 0)
    if stats.get('no_effect_docs'):
        answer = f'Os estudos encontrados não observaram interação relevante entre {drug} e {food}.'
    elif records == 1:
        answer = f'O único registro cita {drug} e {food} juntos, mas não descreve uma interação.'
    else:
        answer = f'Os {records} registros citam {drug} e {food} juntos, mas nenhum descreve uma interação.'
    return {'title': 'Sem interação identificada', 'answer': answer,
            'recommendation': 'Isso não garante segurança: a base pode não cobrir todos os estudos. Em caso de dúvida, pergunte a um médico ou farmacêutico.'}

SIGNAL_LABELS = {MENTION: 'Apenas menciona os dois', INTERACTION: 'Indica interação', NO_EFFECT: 'Sem efeito observado'}

def signal_detail(category, flags, curated_label):
    parts = []
    if curated_label: parts.append('Gravidade na fonte: ' + curated_label)
    if category == INTERACTION:
        if flags & PK: parts.append('altera concentração, absorção ou metabolismo (farmacocinética)')
        if flags & PD: parts.append('altera o efeito do medicamento (farmacodinâmica)')
        if flags & HARM: parts.append('cita efeito adverso')
        if flags & WARNING: parts.append('traz recomendação de uso')
        if flags & STRONG: parts.append('aviso forte (evitar, contraindicado ou grave)')
        if not parts: parts.append('menciona explicitamente a interação')
    elif category == NO_EFFECT:
        parts.append('o estudo relata ausência de efeito relevante')
    elif not parts:
        parts.append('o trecho cita os dois termos sem descrever interação')
    return '; '.join(parts)

# FooDrugs labels some endogenous molecules, lab markers and extraction noise as "foods".
# In those sentences a change ("simvastatin lowers plasma cholesterol") is usually the drug's
# own effect, not a food interaction, so they count only with explicit interaction wording
# or a usage recommendation.
NON_FOOD_TERMS = {
    'protein', 'proteins', 'insulin', 'glucose', 'd-glucose', 'oxygen', 'cholesterol', 'ldl', 'hdl', 'ldl-cholesterol',
    'hdl-cholesterol', 'triglyceride', 'triglycerides', 'dopamine', 'serotonin', '5-hydroxytryptamine', 'norepinephrine',
    'nitric oxide', 'no', 'glutathione', 'testosterone', 'histamine', 'melatonin', 'adenosine', 'adenosine triphosphate',
    'atp', 'h2o2', 'superoxide', 'nitrogen', 'carbon', 'hydrogen', 'co2', 'malondialdehyde', 'creatinine', 'uric acid',
    'urea', 'bun', 'nephrotoxicity', 'lactic acid', 'cortisol', 'progesterone', 'dehydroepiandrosterone',
    'estrone sulfate', 'androgen', 'steroid', 'hemoglobin', 'albumin', 'bilirubin', 'aspartate', 'alanine',
    'arachidonic acid', 'mevalonic acid', 'same', 'act', 'acts', 'acting', 'spread', 'broad', 'essential', 'organic',
    'microbiology', 'rabbit', '(e)-aconitic acid',
}

def _coordinated(sentence, drug, food):
    """True when the two terms are only listed together ("avoid coffee and caffeine")."""
    a, b = _words(drug)[:1], _words(food)[:1]
    if not a or not b:
        return False
    a, b = re.escape(a[0]), re.escape(b[0])
    link = r'\w*\W{0,3}\s*(,|and|or|and/or|e|ou)\s+(\w+\s+){0,2}'
    return bool(re.search(rf'\b{a}{link}{b}|\b{b}{link}{a}', sentence or '', re.I))

# Foods that naturally contain the "drug" of the pair: advice about coffee and caffeine is
# about the same substance, not an interaction between two different ones.
CONSTITUENTS = {
    'caffeine': {'coffee', 'tea', 'green tea', 'black tea', 'cola', 'chocolate', 'cocoa', 'energy drinks', 'guarana', 'mate'},
    'theophylline': {'tea', 'green tea', 'black tea', 'cocoa'},
    'theobromine': {'cocoa', 'chocolate', 'tea'},
    'ethanol': {'alcohol', 'wine', 'red wine', 'beer', 'spirits', 'alcoholic beverages'},
    'alcohol': {'ethanol', 'wine', 'red wine', 'beer', 'spirits', 'alcoholic beverages'},
}

def adjust_for_terms(category, flags, food, drug='', sentence=''):
    """Downgrade sentences whose signal does not concern the pair itself.

    - Non-food terms (see NON_FOOD_TERMS): drug effect on a biomarker, unless explicit.
    - Listed terms: a recommendation about "coffee and caffeine" applies to both items of the
      list; it is not an interaction between them unless a change between them is described.
    - Constituents (see CONSTITUENTS): the food contains the drug; only explicit interaction counts.
    """
    if category != INTERACTION:
        return category
    if (food or '').strip().lower() in CONSTITUENTS.get((drug or '').strip().lower(), ()) and not INTERACT_RX.search(sentence or ''):
        return MENTION
    if (food or '').strip().lower() in NON_FOOD_TERMS and not flags & (EXPLICIT | WARNING):
        return MENTION
    if not flags & (PK | PD | HARM) and _coordinated(sentence, drug, food) and not INTERACT_RX.search(sentence or ''):
        return MENTION
    return category
