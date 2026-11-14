"""Curated links between FooDrugs terms, used to answer a pair when the literal pair is missing or silent.

FooDrugs was built by text mining: the same substance appears under several spellings ("Alcohol", "Ethanol"),
studies often name a drug class ("Tetracyclines") instead of the drug, and a food is often studied through
its active component (spinach -> vitamin K, aged cheese -> tyramine). Three explicit, reviewable tables:

  SYNONYMS    equivalent terms: their records are pooled as one pair (direct evidence).
  CLASSES     drug -> pharmacological classes it belongs to (indirect evidence).
  COMPONENTS  food -> active components it is a known source of (indirect evidence).

Indirect evidence never raises a result above level 1 ("Atenção") and is always labelled as inferred.
All terms are FooDrugs normalized names (lower case, no accents); terms absent from the base are ignored.
"""

SYNONYMS = {
    'd': [
        ['levodopa', 'l-dopa', 'l dopa', 'ldopa', 'l-3,4-dihydroxyphenylalanine'],
        ['acetaminophen', 'paracetamol', 'apap'],
        ['aspirin', 'acetylsalicylic acid', 'asa'],
        ['warfarin', 'warfarin sodium', 'coumadin'],
        ['metamizole', 'dipyrone', 'metamizol'],
        ['tetracycline', 'tetracycline hydrochloride'],
        ['doxycycline', 'doxycycline hyclate', 'doxycycline monohydrate'],
        ['alendronate', 'alendronate sodium', 'alendronic acid'],
        ['levothyroxine', 'levothyroxine sodium', 'l-thyroxine', 'thyroxine', 'l-t4'],
        ['ciprofloxacin', 'ciprofloxacin hydrochloride'],
        ['metformin', 'metformin hydrochloride'],
        ['cyclosporine', 'cyclosporin', 'ciclosporin', 'cyclosporin a', 'cyclosporine a'],
        ['valproic acid', 'valproate', 'sodium valproate'],
        ['lithium', 'lithium carbonate'],
        ['phenytoin', 'diphenylhydantoin'],
        ['simvastatin', 'simvastatin acid'],
        ['iron', 'ferrous sulfate', 'ferrous sulphate'],
        ['ethinyl estradiol', 'ethinylestradiol', '17alpha-ethynylestradiol'],
    ],
    'f': [
        ['alcohol', 'ethanol', 'alcoholic beverages', 'alcoholic beverage', 'alcohol consumption', 'alcohol intake', 'etoh'],
        ['soy', 'soybean', 'soybeans', 'soya', 'soy products'],
        ['milk', "cow's milk", 'cow milk', 'whole milk', 'skim milk', 'skimmed milk', 'bovine milk'],
        ['dairy', 'dairy products', 'dairy product'],
        ['protein', 'proteins', 'dietary protein', 'protein intake'],
        ['vitamin k', 'vitamin k1', 'phylloquinone', 'phytomenadione', 'phytonadione'],
        ['grapefruit juice', 'grapefruit juices'],
        ['coffee', 'coffees'],
        ['tea', 'black tea'],
        ['green tea', 'green tea extract'],
        ['cranberry juice', 'cranberry juice cocktail'],
        ['calcium', 'dietary calcium', 'calcium intake'],
        ['potassium', 'dietary potassium', 'potassium intake'],
        ['sodium', 'dietary sodium', 'sodium intake', 'salt', 'sodium chloride', 'nacl'],
        ['caffeine', 'caffeinated beverages'],
        ['fiber', 'dietary fiber', 'dietary fibre', 'fibre'],
        ['high-fat meal', 'high fat meal', 'high-fat food', 'fatty meal'],
        ['licorice', 'liquorice', 'licorice root'],
        ['tyramine', 'p-tyramine'],
    ],
}

CLASSES = {
    'tetracycline': ['tetracyclines', 'tetracycline antibiotics'], 'doxycycline': ['tetracyclines', 'tetracycline antibiotics'],
    'minocycline': ['tetracyclines', 'tetracycline antibiotics'], 'oxytetracycline': ['tetracyclines'],
    'ciprofloxacin': ['fluoroquinolones', 'quinolones'], 'levofloxacin': ['fluoroquinolones', 'quinolones'],
    'norfloxacin': ['fluoroquinolones', 'quinolones'], 'ofloxacin': ['fluoroquinolones', 'quinolones'],
    'moxifloxacin': ['fluoroquinolones', 'quinolones'],
    'phenelzine': ['maois', 'mao inhibitors', 'monoamine oxidase inhibitors', 'monoamine oxidase inhibitor', 'maoi'],
    'tranylcypromine': ['maois', 'mao inhibitors', 'monoamine oxidase inhibitors', 'monoamine oxidase inhibitor', 'maoi'],
    'isocarboxazid': ['maois', 'mao inhibitors', 'monoamine oxidase inhibitors', 'monoamine oxidase inhibitor', 'maoi'],
    'selegiline': ['maois', 'mao-b inhibitors', 'monoamine oxidase inhibitors'], 'moclobemide': ['maois', 'monoamine oxidase inhibitors'],
    'linezolid': ['monoamine oxidase inhibitors'], 'isoniazid': ['monoamine oxidase inhibitors'],
    'simvastatin': ['statins', 'hmg-coa reductase inhibitors'], 'atorvastatin': ['statins', 'hmg-coa reductase inhibitors'],
    'lovastatin': ['statins', 'hmg-coa reductase inhibitors'], 'rosuvastatin': ['statins'], 'pravastatin': ['statins'],
    'warfarin': ['coumarins', 'vitamin k antagonists', 'coumarin anticoagulants', 'oral anticoagulants'],
    'acenocoumarol': ['coumarins', 'vitamin k antagonists', 'coumarin anticoagulants', 'oral anticoagulants'],
    'phenprocoumon': ['coumarins', 'vitamin k antagonists', 'coumarin anticoagulants'],
    'nifedipine': ['calcium channel blockers', 'dihydropyridines', 'dihydropyridine calcium channel blockers'],
    'felodipine': ['calcium channel blockers', 'dihydropyridines', 'dihydropyridine calcium channel blockers'],
    'amlodipine': ['calcium channel blockers', 'dihydropyridines'], 'nisoldipine': ['calcium channel blockers', 'dihydropyridines'],
    'alendronate': ['bisphosphonates'], 'risedronate': ['bisphosphonates'], 'ibandronate': ['bisphosphonates'],
    'enalapril': ['ace inhibitors', 'angiotensin-converting enzyme inhibitors'],
    'captopril': ['ace inhibitors', 'angiotensin-converting enzyme inhibitors'],
    'lisinopril': ['ace inhibitors', 'angiotensin-converting enzyme inhibitors'],
    'ramipril': ['ace inhibitors', 'angiotensin-converting enzyme inhibitors'],
    'losartan': ['angiotensin ii receptor blockers', 'arbs', 'angiotensin receptor blockers'],
    'valsartan': ['angiotensin ii receptor blockers', 'arbs', 'angiotensin receptor blockers'],
    'spironolactone': ['potassium-sparing diuretics'], 'amiloride': ['potassium-sparing diuretics'],
    'sertraline': ['ssris', 'selective serotonin reuptake inhibitors'], 'fluoxetine': ['ssris', 'selective serotonin reuptake inhibitors'],
    'diazepam': ['benzodiazepines'], 'alprazolam': ['benzodiazepines'], 'clonazepam': ['benzodiazepines'], 'midazolam': ['benzodiazepines'],
    'ibuprofen': ['nsaids', 'non-steroidal anti-inflammatory drugs'], 'naproxen': ['nsaids', 'non-steroidal anti-inflammatory drugs'],
    'diclofenac': ['nsaids', 'non-steroidal anti-inflammatory drugs'],
    'cyclosporine': ['calcineurin inhibitors', 'immunosuppressants'], 'tacrolimus': ['calcineurin inhibitors', 'immunosuppressants'],
}

COMPONENTS = {
    # vitamin K sources
    'spinach': ['vitamin k', 'potassium'], 'kale': ['vitamin k'], 'broccoli': ['vitamin k'], 'cabbage': ['vitamin k'],
    'lettuce': ['vitamin k'], 'brussels sprouts': ['vitamin k'], 'collard greens': ['vitamin k'], 'parsley': ['vitamin k'],
    'green leafy vegetables': ['vitamin k'], 'leafy vegetables': ['vitamin k'], 'avocado': ['vitamin k', 'tyramine', 'potassium'],
    # tyramine sources
    'cheese': ['tyramine', 'calcium'], 'aged cheese': ['tyramine', 'calcium'], 'cheddar': ['tyramine', 'calcium'],
    'soy sauce': ['tyramine', 'sodium'], 'salami': ['tyramine', 'sodium'], 'sauerkraut': ['tyramine'],
    'beer': ['alcohol', 'tyramine'], 'wine': ['alcohol', 'tyramine'], 'red wine': ['alcohol', 'tyramine'],
    'white wine': ['alcohol'], 'spirits': ['alcohol'], 'vodka': ['alcohol'], 'whisky': ['alcohol'],
    # caffeine sources
    'coffee': ['caffeine'], 'tea': ['caffeine'], 'green tea': ['caffeine'], 'black tea': ['caffeine'], 'cola': ['caffeine'],
    'energy drinks': ['caffeine'], 'chocolate': ['caffeine'], 'cocoa': ['caffeine'], 'mate': ['caffeine'], 'guarana': ['caffeine'],
    # calcium / minerals
    'milk': ['calcium'], 'dairy': ['calcium'], 'yogurt': ['calcium'], 'yoghurt': ['calcium'], 'calcium-fortified orange juice': ['calcium'],
    'banana': ['potassium'], 'orange juice': ['potassium'], 'potatoes': ['potassium'], 'coconut water': ['potassium'],
    'salt substitutes': ['potassium'], 'spinach juice': ['vitamin k'],
    # others
    'grapefruit': ['grapefruit juice', 'bergamottin', 'naringin', 'furanocoumarins'],
    'grapefruit juice': ['grapefruit', 'bergamottin', 'naringin', 'furanocoumarins'],
    'licorice': ['glycyrrhizin', 'glycyrrhizic acid'], 'soy': ['isoflavones', 'genistein'],
    'oatmeal': ['fiber'], 'bran': ['fiber'], 'wheat bran': ['fiber'], 'beans': ['fiber'],
}

LEVEL_CAP = 1  # inferred evidence is shown as "Atenção" at most
