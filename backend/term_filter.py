"""Terms hidden from suggestions and searches because they are not foods (or not medicines).

FooDrugs was produced by automatic text mining, which labels some endogenous molecules, laboratory
markers, gases, drugs and extraction noise as "foods" (e.g. oxygen, cholesterol, insulin, "SAME").
Those records are preserved in the database and remain reachable by identifier (history, data explorer);
they are only removed from suggestions, autocomplete and the knowledge-base listing.
"""
from foodrugs_full import norm

# Noise, gases, ions, generic words, lab markers and organisms: hidden for both medicines and foods.
NOISE = {
 'same', 'act', 'acts', 'acting', 'acted', 'essential', 'spread', 'spreading', 'broad', 'broader', 'organic', 'crude',
 'extracted', 'coding', 'docking', 'date', 'major adverse cardiovascular events', 'major adverse cardiac events',
 'nephrotoxicity', 'microbiology', 'respiratory syncytial virus', 'p. gingivalis', 'porphyromonas gingivalis',
 'covid-19', 'hiv', 'polycystic ovary syndrome', 'non-alcoholic fatty liver disease', 'nonalcoholic fatty liver disease',
 'lps-induced', '-induced', 'a.', 'l.', 'p.', 's.', 'c.', 'h.', 'm.', 'arabidopsis', 'arabidopsis thaliana',
 'oxygen', 'o2', 'o', 'nitrogen', 'carbon', 'hydrogen', 'co2', 'carbon dioxide', 'co', 'carbon monoxide', 'nitric oxide', 'no',
 'nitrous oxide', 'n2o', 'ozone', 'methane', 'ch4', 'h2s', 'hydrogen sulfide', 'nahs', 'ammonia', 'nh4+', 'ammonium', 'h+',
 'ca++', 'calcium ions', 'mg2+', 'oh', 'hydroxyl', 'superoxide', 'superoxide anion', 'h2o2', 'h(2)o(2)', 'hydrogen peroxide',
 'peroxide', 'peroxides', 'peroxynitrite', 'reactive oxygen species', 'f', 'c', 'ci', 'na', 'se', 'mg', 'cho', 'mda', 'mtt',
 'trolox', 'l-name', 'pcpa', '8-ohdg', '6-ohda', '6-hydroxydopamine', 'r-chop', 'iia', 'ash', 'sap', 'cocktail',
 'aryl hydrocarbon', 'alkyl', 'carboxyl', 'carbonyl', 'thiol', 'thiols', 'sulfhydryl', 'disulfide', 'amine', 'amines', 'amino',
 'methyl', 'aromatic', 'ketone', 'aldehyde', 'aldehydes', 'esters', 'acids', 'chemical oxygen demand', 'urea nitrogen',
 'graphene oxide', 'tio2', 'platinum', 'gold', 'titanium', 'barium', 'strontium', 'paraquat', 'rotenone', 'chlorpyrifos',
 'organophosphate', 'carbamate', 'toluene', 'benzene', 'hexane', 'acetone', 'acetonitrile', 'chloroform', '2-propanol',
 'ethyl acetate', 'dimethyl sulfoxide', 'polyethylene glycol', 'tritium', 'xenobiotics', 'endotoxin', 'lipopolysaccharide',
 'lps', 'streptozotocin', 'monocrotaline', 'thiobarbituric acid', 'tetradecanoylphorbol-13-acetate',
 '12-o-tetradecanoylphorbol-13-acetate', 'phorbol ester', 'phorbol 12-myristate 13-acetate', 'cytochalasin b', 'staurosporine',
 'thapsigargin', 'ryanodine', 'ionomycin', 'veratridine', 'tetrodotoxin', 'cycloheximide', 'pertussis toxin', 'streptavidin',
 'rabbit', 'rabbits', 'horse', 'horses', 'lambs', 'agonists', 'muscarinic', 'nicotinic acetylcholine', 'vanilloid',
 'gabaergic', 'interleukin', 'agar', 'biochar', 'cadmium', 'arsenic', 'arsenic trioxide', 'lead', 'mercury', 'nickel',
 'aluminum', 'silver', 'vanadate', 'cyanide', 'epiestradiol',
}

# Endogenous molecules, hormones, lab markers and medicines that the extraction labelled as foods.
NOT_FOOD = {
 'insulin', 'cholesterol', 'ldl-cholesterol', 'hdl-cholesterol', 'triglyceride', 'triglycerides', 'triacylglycerol',
 'd-glucose', 'dopamine', 'serotonin', '5-hydroxytryptamine', 'norepinephrine', 'noradrenaline', 'epinephrine', 'adrenaline',
 'acetylcholine', 'histamine', 'gaba', 'gamma-aminobutyric acid', 'γ-aminobutyric acid', 'glutamic acid', 'l-glutamic acid',
 'testosterone', 'progesterone', 'estradiol', 'epiestradiol', 'estriol', 'estrone sulfate', '17alpha-ethynylestradiol',
 'diethylstilbesterol', 'cortisol', 'corticosterone', 'aldosterone', 'dehydroepiandrosterone', 'dhea', 'androstenedione',
 'androgen', 'melatonin', 'creatinine', 'urea', 'uric acid', 'bilirubin', 'homocysteine', 'malondialdehyde', 'angiotensin',
 'angiotensin ii', 'bradykinin', 'prostaglandin', 'prostaglandins', 'prostaglandin e2', 'thromboxane', 'prostacyclin',
 'vasopressin', 'oxytocin', 'somatostatin', 'calcitonin', 'corticotropin', 'ferritin', 'osteocalcin', 'glutathione',
 'adenosine triphosphate', 'adenosine diphosphate', 'adenosine monophosphate', 'adenosine', 'adp', 'cgmp',
 'cyclic adenosine monophosphate', 'cyclic guanosine monophosphate', 'nadph', 'nadh', 'nad+',
 'nicotinamide adenine dinucleotide', 'nicotinamide adenine dinucleotide phosphate', 'kynurenine', 'catecholamine',
 'catecholamines', 'monoamine', 'spermine', 'spermidine', 'putrescine', 'polyamine', 'uridine', 'inosine', 'xanthine',
 'hypoxanthine', 'guanine', 'guanosine', 'thymidine', 'purine', 'lactic acid', 'd-lactic acid', 'pyruvic acid',
 'glucose-6-phosphate', 'lysophosphatidic acid', 'phosphatidylinositol', 'inositol phosphate', 'inositol phosphates',
 'ceramide', 'farnesyl pyrophosphate', 'mevalonic acid', 'bile acid', 'bile acids', 'endocannabinoid', 'anandamide',
 'tryptamine', 'octopamine', 'agmatine', 'water', 'waters', 'h2o',
 'atropine', 'cocaine', 'nicotine', 'morphine', 'paclitaxel', 'digoxin', 'digitoxin', 'colchicine', 'reserpine', 'yohimbine',
 'scopolamine', 'vincristine', 'vinblastine', 'irinotecan', 'camptothecin', 'mitomycin c', 'mmc', 'physostigmine',
 'pilocarpine', 'neostigmine', 'bicuculline', 'quinidine', 'codeine', 'ephedrine', 'cisplatin', 'carboplatin', 'dexamethasone',
 'tetracycline', 'amoxycillin', 'chloroquine', 'papaverine', 'carbachol', 'tubocurarine', 'strychnine', 'emetine',
 'methyllycaconitine', 'apomorphine', 'liothyronine', 'phenylephrine', 'adrenaline', 'cannabis', 'cannabidiol',
 'cannabinoid', 'cannabinoids', 'tetrahydrocannabinol', 'dihydroartemisinin', 'artemisinine', 'benzodiazepine',
 'antiretroviral therapy', 'dimethyl sulfoxide', '8-oh-dpat', 'harmaline', 'cytisine', 'arecoline', 'carbenoxolone',
 'podophyllotoxin', 'shikonin', 'chelerythrine', 'theophylline', '(e)-aconitic acid', '24,25-dihydroxyvitamin d3',
 'd-tryptophan', 'chloride', 'phosphate', 'sulfate', 'sulfide', 'acetate', 'hydroquinone', 'resorcinol', 'phloroglucinol',
 'formic acid', 'trimethylamine oxide', 'acetaldehyde', 'formaldehyde', 'methanol', 'phenol',
 'geranylgeranyl pyrophosphate', 'farnesyl pyrophosphate', 'isopentenyl pyrophosphate', 'squalene epoxide',
}

# Endogenous molecules, lab markers, nutrient classes and generic chemistry listed as "medicines".
NOT_DRUG = {
 'd-glucose', 'cholesterol', 'ldl-cholesterol', 'hdl-cholesterol', 'triglyceride', 'triglycerides', 'triacylglycerol',
 'serotonin', '5-hydroxytryptamine', 'acetylcholine', 'histamine', 'gaba', 'gamma-aminobutyric acid', 'γ-aminobutyric acid',
 'glutamic acid', 'l-glutamic acid', 'creatinine', 'urea', 'uric acid', 'bilirubin', 'homocysteine', 'malondialdehyde',
 'angiotensin', 'angiotensin ii', 'bradykinin', 'prostaglandin', 'prostaglandins', 'prostaglandin e2', 'thromboxane',
 'ferritin', 'osteocalcin', 'glutathione', 'adenosine triphosphate', 'adp', 'cgmp', 'nadph', 'nadh', 'nad+',
 'nicotinamide adenine dinucleotide', 'nicotinamide adenine dinucleotide phosphate', 'kynurenine', 'catecholamine',
 'catecholamines', 'monoamine', 'spermine', 'spermidine', 'putrescine', 'polyamine', 'polyamines', 'xanthine',
 'hypoxanthine', 'purine', 'lactic acid', 'd-lactic acid', 'pyruvic acid', 'ceramide', 'bile acid', 'bile acids',
 'endocannabinoid', 'anandamide', 'amino acids', 'amino acid', 'fatty acids', 'fatty acid', 'carbohydrate', 'carbohydrates',
 'polyphenols', 'polyphenol', 'antioxidants', 'antioxidant', 'glycosides', 'phosphate', 'chloride', 'sulfide', 'sulfate',
 'nitrate', 'nitrite', 'acetate', 'citrate', 'bicarbonate', 'phospholipids', 'sterols', 'high-fat diet', 'ethylene',
 'methanol', 'phenol', 'phenols', 'carotenoids', 'carotenoid', 'flavonoids', 'alkaloids', 'alkaloid', 'oligosaccharides',
 'inositol phosphates', 'phosphatidylinositol', 'phosphatidylcholine', 'trimethylamine oxide', 'acetylglycine',
 'epsilon-polylysine', "cyanidin 3-(6'-acetyl-galactoside)", 'chlorophyll', 'lignin', 'hemin', 'water',
}

_NOISE = {norm(t) for t in NOISE}
_NOT_DRUG = _NOISE | {norm(t) for t in NOT_DRUG}
_NOT_FOOD = _NOISE | {norm(t) for t in NOT_FOOD}

def hidden(kind):
    """Normalized terms hidden for medicines ('d') or foods ('f')."""
    return _NOT_FOOD if kind == 'f' else _NOT_DRUG

def sql(kind, column):
    """SQL fragment and parameters that exclude hidden terms from a normalized-name column."""
    terms = sorted(hidden(kind))
    return f' AND {column} NOT IN ({",".join("?" * len(terms))})', terms
