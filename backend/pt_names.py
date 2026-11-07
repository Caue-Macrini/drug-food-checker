"""Portuguese display names for the most frequent FooDrugs terms.

The original FooDrugs names are never rewritten in the database. These translations are used only
to display terms in Portuguese and as additional search aliases. Terms without a reviewed
translation (extraction noise, rare compounds) are shown with their original name.
"""

def _k(name):
    return ' '.join(str(name or '').replace('‐', '-').lower().split())

PT = {
 # Medicamentos e classes
 'acetaminophen':'paracetamol','paracetamol':'paracetamol','apap':'paracetamol','aspirin':'ácido acetilsalicílico (aspirina)',
 'acetylsalicylic acid':'ácido acetilsalicílico','metformin':'metformina','cisplatin':'cisplatina','simvastatin':'sinvastatina',
 'atorvastatin':'atorvastatina','lovastatin':'lovastatina','pravastatin':'pravastatina','rosuvastatin':'rosuvastatina',
 'fluvastatin':'fluvastatina','statin':'estatina','statins':'estatinas','nifedipine':'nifedipino','amlodipine':'anlodipino',
 'nimodipine':'nimodipino','diltiazem':'diltiazem','verapamil':'verapamil','felodipine':'felodipino','losartan':'losartana',
 'captopril':'captopril','enalapril':'enalapril','propranolol':'propranolol','atenolol':'atenolol','carvedilol':'carvedilol',
 'clonidine':'clonidina','prazosin':'prazosina','furosemide':'furosemida','hydrochlorothiazide':'hidroclorotiazida',
 'spironolactone':'espironolactona','amiloride':'amilorida','bumetanide':'bumetanida','acetazolamide':'acetazolamida',
 'diuretics':'diuréticos','digoxin':'digoxina','digitoxin':'digitoxina','amiodarone':'amiodarona','quinidine':'quinidina',
 'lidocaine':'lidocaína','procaine':'procaína','bupivacaine':'bupivacaína','warfarin':'varfarina','heparin':'heparina',
 'clopidogrel':'clopidogrel','dipyridamole':'dipiridamol','doxorubicin':'doxorrubicina','adriamycin':'doxorrubicina',
 'paclitaxel':'paclitaxel','taxol':'paclitaxel','docetaxel':'docetaxel','cyclophosphamide':'ciclofosfamida',
 'methotrexate':'metotrexato','5-fluorouracil':'5-fluorouracila','carboplatin':'carboplatina','oxaliplatin':'oxaliplatina',
 'gemcitabine':'gencitabina','etoposide':'etoposídeo','vincristine':'vincristina','vinblastine':'vimblastina',
 'irinotecan':'irinotecano','tamoxifen':'tamoxifeno','letrozole':'letrozol','imatinib':'imatinibe','gefitinib':'gefitinibe',
 'sorafenib':'sorafenibe','bortezomib':'bortezomibe','capecitabine':'capecitabina','temozolomide':'temozolomida',
 'bleomycin':'bleomicina','mitomycin c':'mitomicina C','camptothecin':'camptotecina','hydroxyurea':'hidroxiureia',
 'bevacizumab':'bevacizumabe','rituximab':'rituximabe','cetuximab':'cetuximabe','palivizumab':'palivizumabe',
 'dexamethasone':'dexametasona','prednisone':'prednisona','prednisolone':'prednisolona','hydrocortisone':'hidrocortisona',
 'corticosteroids':'corticosteroides','corticosteroid':'corticosteroide','glucocorticoid':'glicocorticoide',
 'glucocorticoids':'glicocorticoides','morphine':'morfina','codeine':'codeína','fentanyl':'fentanila','tramadol':'tramadol',
 'methadone':'metadona','buprenorphine':'buprenorfina','naloxone':'naloxona','naltrexone':'naltrexona','heroin':'heroína',
 'opioid':'opioide','opioids':'opioides','ketamine':'cetamina','propofol':'propofol','isoflurane':'isoflurano',
 'sevoflurane':'sevoflurano','halothane':'halotano','midazolam':'midazolam','diazepam':'diazepam',
 'benzodiazepine':'benzodiazepínico','benzodiazepines':'benzodiazepínicos','dexmedetomidine':'dexmedetomidina',
 'anesthetics':'anestésicos','anesthetic':'anestésico','fluoxetine':'fluoxetina','citalopram':'citalopram',
 'imipramine':'imipramina','amitriptyline':'amitriptilina','desipramine':'desipramina','bupropion':'bupropiona',
 'antidepressants':'antidepressivos','antidepressant':'antidepressivo','haloperidol':'haloperidol','clozapine':'clozapina',
 'olanzapine':'olanzapina','chlorpromazine':'clorpromazina','trifluoperazine':'trifluoperazina','sulpiride':'sulpirida',
 'lithium':'lítio','carbamazepine':'carbamazepina','phenytoin':'fenitoína','phenobarbital':'fenobarbital',
 'pentobarbital':'pentobarbital','valproic acid':'ácido valproico','gabapentin':'gabapentina','baclofen':'baclofeno',
 'donepezil':'donepezila','methylphenidate':'metilfenidato','amphetamine':'anfetamina','d-amphetamine':'dextroanfetamina',
 'methamphetamine':'metanfetamina','cocaine':'cocaína','nicotine':'nicotina','varenicline':'vareniclina','cotinine':'cotinina',
 'cannabidiol':'canabidiol','tetrahydrocannabinol':'tetra-hidrocanabinol (THC)','cannabis':'cannabis','cannabinoid':'canabinoide',
 'cannabinoids':'canabinoides','buspirone':'buspirona','ondansetron':'ondansetrona','omeprazole':'omeprazol',
 'ranitidine':'ranitidina','cimetidine':'cimetidina','ibuprofen':'ibuprofeno','diclofenac':'diclofenaco',
 'indomethacin':'indometacina','celecoxib':'celecoxibe','colchicine':'colchicina','allopurinol':'alopurinol',
 'probenecid':'probenecida','insulin':'insulina','glibenclamide':'glibenclamida','tolbutamide':'tolbutamida',
 'pioglitazone':'pioglitazona','rosiglitazone':'rosiglitazona','sitagliptin':'sitagliptina','liraglutide':'liraglutida',
 'dapagliflozin':'dapagliflozina','empagliflozin':'empagliflozina','acarbose':'acarbose','fenofibrate':'fenofibrato',
 'clofibrate':'clofibrato','ezetimibe':'ezetimiba','cholestyramine':'colestiramina','alendronate':'alendronato',
 'raloxifene':'raloxifeno','levothyroxine':'levotiroxina','thyroxine':'tiroxina','liothyronine':'liotironina',
 'cyclosporine':'ciclosporina','cyclosporine a':'ciclosporina A','cyclosporin a':'ciclosporina A','tacrolimus':'tacrolimo',
 'rapamycin':'rapamicina (sirolimo)','sildenafil':'sildenafila','theophylline':'teofilina','salbutamol':'salbutamol',
 'isoproterenol':'isoproterenol','isoprenaline':'isoprenalina','dobutamine':'dobutamina','phenylephrine':'fenilefrina',
 'ephedrine':'efedrina','atropine':'atropina','scopolamine':'escopolamina','pilocarpine':'pilocarpina',
 'neostigmine':'neostigmina','physostigmine':'fisostigmina','carbachol':'carbacol','methacholine':'metacolina',
 'reserpine':'reserpina','yohimbine':'ioimbina','phentolamine':'fentolamina','phenoxybenzamine':'fenoxibenzamina',
 'apomorphine':'apomorfina','bromocriptine':'bromocriptina','l-dopa':'levodopa','disulfiram':'dissulfiram',
 'ciprofloxacin':'ciprofloxacino','tetracycline':'tetraciclina','doxycycline':'doxiciclina','minocycline':'minociclina',
 'oxytetracycline':'oxitetraciclina','erythromycin':'eritromicina','clarithromycin':'claritromicina',
 'gentamicin':'gentamicina','neomycin':'neomicina','vancomycin':'vancomicina','colistin':'colistina',
 'ampicillin':'ampicilina','amoxycillin':'amoxicilina','amoxicillin':'amoxicilina','metronidazole':'metronidazol',
 'sulfamethoxazole':'sulfametoxazol','chloramphenicol':'cloranfenicol','rifampicin':'rifampicina','isoniazid':'isoniazida',
 'antibiotics':'antibióticos','antibiotic':'antibiótico','antimicrobials':'antimicrobianos','fluconazole':'fluconazol',
 'ketoconazole':'cetoconazol','amphotericin b':'anfotericina B','chloroquine':'cloroquina','quinine':'quinina',
 'artemisinine':'artemisinina','dihydroartemisinin':'di-hidroartemisinina','ivermectin':'ivermectina',
 'levamisole':'levamisol','antiretroviral':'antirretroviral','antiretroviral therapy':'terapia antirretroviral',
 'chlorhexidine':'clorexidina','deferoxamine':'deferoxamina','pentoxifylline':'pentoxifilina',
 'ursodeoxycholic acid':'ácido ursodesoxicólico','nitroglycerin':'nitroglicerina','sodium nitroprusside':'nitroprussiato de sódio',
 'erythropoietin':'eritropoetina','growth hormone':'hormônio do crescimento','parathyroid hormone':'paratormônio',
 'oxytocin':'ocitocina','vasopressin':'vasopressina','somatostatin':'somatostatina','calcitonin':'calcitonina',
 'acth':'hormônio adrenocorticotrófico','corticotropin':'corticotrofina','ghrelin':'grelina','leptin':'leptina',
 'adiponectin':'adiponectina','hepcidin':'hepcidina','metronidazol':'metronidazol','dantrolene':'dantroleno',
 # Hormônios e moléculas endógenas
 'testosterone':'testosterona','progesterone':'progesterona','estradiol':'estradiol','epiestradiol':'epiestradiol',
 'estriol':'estriol','estrone sulfate':'sulfato de estrona','17alpha-ethynylestradiol':'etinilestradiol',
 'estrogens':'estrogênios','androgen':'andrógeno','androgens':'andrógenos','androstenedione':'androstenediona',
 'dihydrotestosterone':'di-hidrotestosterona','dehydroepiandrosterone':'desidroepiandrosterona (DHEA)','dhea':'DHEA',
 'dehydroepiandrosterone sulfate':'sulfato de DHEA','pregnenolone':'pregnenolona','cortisol':'cortisol',
 'corticosterone':'corticosterona','aldosterone':'aldosterona','melatonin':'melatonina','serotonin':'serotonina',
 '5-hydroxytryptamine':'serotonina (5-HT)','dopamine':'dopamina','norepinephrine':'noradrenalina',
 'noradrenaline':'noradrenalina','epinephrine':'adrenalina','adrenaline':'adrenalina','acetylcholine':'acetilcolina',
 'histamine':'histamina','gaba':'GABA','gamma-aminobutyric acid':'ácido gama-aminobutírico (GABA)',
 'γ-aminobutyric acid':'ácido gama-aminobutírico (GABA)','glutamic acid':'ácido glutâmico','l-glutamic acid':'ácido glutâmico',
 'catecholamine':'catecolamina','catecholamines':'catecolaminas','angiotensin ii':'angiotensina II','angiotensin':'angiotensina',
 'bradykinin':'bradicinina','prostaglandin':'prostaglandina','prostaglandins':'prostaglandinas',
 'prostaglandin e2':'prostaglandina E2','thromboxane':'tromboxano','prostacyclin':'prostaciclina',
 'anandamide':'anandamida','adenosine':'adenosina','adenosine triphosphate':'trifosfato de adenosina (ATP)',
 'adenosine diphosphate':'difosfato de adenosina (ADP)','adenosine monophosphate':'monofosfato de adenosina (AMP)',
 'insulina':'insulina','bilirubin':'bilirrubina','creatinine':'creatinina','uric acid':'ácido úrico','urea':'ureia',
 'urea nitrogen':'nitrogênio ureico','homocysteine':'homocisteína','cholesterol':'colesterol','ldl-cholesterol':'colesterol LDL',
 'hdl-cholesterol':'colesterol HDL','triglyceride':'triglicerídeo','triglycerides':'triglicerídeos',
 'triacylglycerol':'triacilglicerol','ferritin':'ferritina','osteocalcin':'osteocalcina','kynurenine':'cinurenina',
 # Nutrientes, minerais e compostos alimentares
 'protein':'proteína','proteins':'proteínas','calcium':'cálcio','iron':'ferro','zinc':'zinco','sodium':'sódio',
 'potassium':'potássio','magnesium':'magnésio','copper':'cobre','selenium':'selênio','iodine':'iodo','phosphorus':'fósforo',
 'chromium':'cromo','manganese':'manganês','phosphate':'fosfato','chloride':'cloreto','salt':'sal','salts':'sais',
 'sodium chloride':'cloreto de sódio','nacl':'cloreto de sódio','kcl':'cloreto de potássio','calcium carbonate':'carbonato de cálcio',
 'calcium phosphate':'fosfato de cálcio','sodium bicarbonate':'bicarbonato de sódio','bicarbonate':'bicarbonato',
 'zinc sulfate':'sulfato de zinco','sodium selenite':'selenito de sódio','selenite':'selenito','water':'água',
 'drinking water':'água potável','tap water':'água da torneira','oxygen':'oxigênio','d-glucose':'glicose','glucose':'glicose',
 'd-fructose':'frutose','sucrose':'sacarose','d-galactose':'galactose','beta-lactose':'lactose','d-mannose':'manose',
 'd-xylose':'xilose','sorbitol':'sorbitol','xylitol':'xilitol','d-mannitol':'manitol','trehalose':'trealose',
 'maltodextrin':'maltodextrina','starch':'amido','sugars':'açúcares','carbohydrate':'carboidrato','carbohydrates':'carboidratos',
 'oligosaccharides':'oligossacarídeos','lactulose':'lactulose','fat':'gordura','fats':'gorduras','fatty acid':'ácido graxo',
 'fatty acids':'ácidos graxos','omega-3 fatty acids':'ácidos graxos ômega-3','n-3':'ômega-3','n-3 pufa':'ômega-3 (AGPI)',
 'polyunsaturated fatty acids':'ácidos graxos poli-insaturados','eicosapentaenoic acid':'ácido eicosapentaenoico (EPA)',
 'doconexent':'ácido docosa-hexaenoico (DHA)','alpha-linolenic acid':'ácido alfa-linolênico','arachidonic acid':'ácido araquidônico',
 'oleic acid':'ácido oleico','palmitic acid':'ácido palmítico','(z,z)-9,12-octadecadienoic acid':'ácido linoleico',
 'butyrate':'butirato','butyric acid':'ácido butírico','propionate':'propionato','propionic acid':'ácido propiônico',
 'acetate':'acetato','amino acid':'aminoácido','amino acids':'aminoácidos','glycine':'glicina','arginine':'arginina',
 'l-arginine':'arginina','l-tyrosine':'tirosina','l-serine':'serina','l-asparagine':'asparagina','l-methionine':'metionina',
 'l-histidine':'histidina','l-proline':'prolina','l-alanine':'alanina','l-cysteine':'cisteína','l-leucine':'leucina',
 'l-lysine':'lisina','l-threonine':'treonina','l-tryptophan':'triptofano','d-tryptophan':'D-triptofano',
 'l-citrulline':'citrulina','l-aspartic acid':'ácido aspártico','valine':'valina','phenylalanine':'fenilalanina',
 'levoglutamide':'glutamina','ornithine':'ornitina','taurine':'taurina','l-carnitine':'carnitina','creatine':'creatina',
 'betaine':'betaína','choline':'colina','l-theanine':'teanina','glutathione':'glutationa','n-acetylcysteine':'N-acetilcisteína',
 'nac':'N-acetilcisteína','vitamin':'vitamina','vitamins':'vitaminas','vitamin d3':'vitamina D3','vitamin d₃':'vitamina D3',
 '25-hydroxycholecalciferol':'25-hidroxivitamina D','25(oh)d':'25-hidroxivitamina D','calcitriol':'calcitriol',
 '24,25-dihydroxyvitamin d3':'24,25-di-hidroxivitamina D3','ascorbic acid':'ácido ascórbico (vitamina C)',
 'l-ascorbic acid':'ácido ascórbico (vitamina C)','ascorbate':'ascorbato (vitamina C)','alpha-tocopherol':'alfa-tocoferol (vitamina E)',
 'gamma-tocopherol':'gama-tocoferol','retinol':'retinol (vitamina A)','retinoic acid':'ácido retinoico','retinoid':'retinoide',
 'retinoids':'retinoides','beta-carotene':'betacaroteno','carotenoids':'carotenoides','carotenoid':'carotenoide',
 'folic acid':'ácido fólico','cobalamin':'cobalamina (vitamina B12)','pyridoxine':'piridoxina (vitamina B6)',
 'riboflavine':'riboflavina (vitamina B2)','thiamine':'tiamina (vitamina B1)','biotin':'biotina','nicotinic acid':'ácido nicotínico (niacina)',
 'nicotinamide':'nicotinamida','pantothenic acid':'ácido pantotênico','phytomenadione':'fitomenadiona (vitamina K1)',
 'menadione':'menadiona (vitamina K3)','vitamin k':'vitamina K','coenzyme q10':'coenzima Q10','myo-inositol':'mio-inositol',
 'lactic acid':'ácido lático','d-lactic acid':'ácido D-lático','citric acid':'ácido cítrico','malic acid':'ácido málico',
 'l-malic acid':'ácido málico','succinic acid':'ácido succínico','fumaric acid':'ácido fumárico','pyruvic acid':'ácido pirúvico',
 'salicylic acid':'ácido salicílico','salicylate':'salicilato','caffeine':'cafeína','theobromine':'teobromina',
 'polyphenols':'polifenóis','polyphenol':'polifenol','flavonoids':'flavonoides','isoflavones':'isoflavonas',
 'anthocyanins':'antocianinas','catechin':'catequina','catechins':'catequinas','epigallocatechin gallate':'galato de epigalocatequina',
 'quercetin':'quercetina','quercetin 3-rutinoside':'rutina','resveratrol':'resveratrol','curcumin':'curcumina',
 'genistein':'genisteína','daidzein':'daidzeína','kaempferol':'campferol','luteolin':'luteolina','apigenin':'apigenina',
 'myricetin':'miricetina','fisetin':'fisetina','chrysin':'crisina','naringin':'naringina','(s)-naringenin':'naringenina',
 'hesperidin':'hesperidina','diosmin':'diosmina','baicalin':'baicalina','baicalein':'baicaleína','puerarin':'puerarina',
 'berberine':'berberina','silymarin':'silimarina','silibinin':'silibinina','sulforaphane':'sulforafano','piperine':'piperina',
 'capsaicin':'capsaicina','allicin':'alicina','gingerol':'gingerol','lycopene':'licopeno','(9z)-lycopene':'licopeno',
 'lutein':'luteína','astaxanthine':'astaxantina','chlorogenic acid':'ácido clorogênico','caffeic acid':'ácido cafeico',
 'ferulic acid':'ácido ferúlico','gallic acid':'ácido gálico','ellagic acid':'ácido elágico','phenolic acids':'ácidos fenólicos',
 'chlorophyll':'clorofila','phytic acid':'ácido fítico','pectin':'pectina','chitosan':'quitosana','glucosamine':'glucosamina',
 'chondroitin sulfate':'sulfato de condroitina','tyramine':'tiramina','glycyrrhizin':'glicirrizina',
 'glycyrrhizic acid':'ácido glicirrízico','glycyrrhetinic acid':'ácido glicirretínico','eugenol':'eugenol','menthol':'mentol',
 'linalool':'linalol','vanillin':'vanilina','coumarin':'cumarina','saponin':'saponina','saponins':'saponinas',
 'alkaloids':'alcaloides','alkaloid':'alcaloide','thymoquinone':'timoquinona','emodin':'emodina','casein':'caseína',
 'whey':'soro de leite','whey protein':'proteína do soro do leite','gluten':'glúten','gelatin':'gelatina','probiotics':'probióticos',
 'antioxidants':'antioxidantes','antioxidant':'antioxidante','ethanol':'etanol (álcool)','alcohol':'álcool','methanol':'metanol',
 # Alimentos e bebidas
 'diet':'dieta','diets':'dietas','food':'alimento','foods':'alimentos','fish':'peixe','milk':'leite','human milk':'leite humano',
 'rice':'arroz','wheat':'trigo','soybean':'soja','soy':'soja','tea':'chá','green tea':'chá verde','green tea extract':'extrato de chá verde',
 'coffee':'café','cocoa':'cacau','chocolate':'chocolate','cream':'creme de leite','egg':'ovo','eggs':'ovos','tomato':'tomate',
 'meat':'carne','beef':'carne bovina','pork':'carne suína','chicken':'frango','chickens':'frangos','poultry':'aves',
 'juice':'suco','grapefruit':'toranja','grapefruit juice':'suco de toranja','orange':'laranja','orange juice':'suco de laranja',
 'apple':'maçã','apple juice':'suco de maçã','grape':'uva','banana':'banana','strawberry':'morango','citrus':'frutas cítricas',
 'fruit':'fruta','fruits':'frutas','fruits and vegetables':'frutas e hortaliças','vegetable':'hortaliça','vegetables':'hortaliças',
 'potato':'batata','spinach':'espinafre','lettuce':'alface','cucumber':'pepino','garlic':'alho','ginger':'gengibre',
 'pepper':'pimenta','mustard':'mostarda','horseradish':'raiz-forte','mushroom':'cogumelo','bean':'feijão','peanut':'amendoim',
 'pea':'ervilha','maize':'milho','corn':'milho','corn oil':'óleo de milho','barley':'cevada','oat':'aveia','sorghum':'sorgo',
 'bran':'farelo','flour':'farinha','bread':'pão','cereal':'cereal','seed':'semente','seeds':'sementes','oil':'óleo','oils':'óleos',
 'olive oil':'azeite de oliva','olive':'oliva','fish oil':'óleo de peixe','essential oil':'óleo essencial',
 'essential oils':'óleos essenciais','honey':'mel','propolis':'própolis','syrup':'xarope','yogurt':'iogurte','cheese':'queijo',
 'dairy':'laticínios','wine':'vinho','red wine':'vinho tinto','beer':'cerveja','beverage':'bebida','beverages':'bebidas',
 'shrimp':'camarão','salmon':'salmão','trout':'truta','rainbow trout':'truta-arco-íris','tilapia':'tilápia','cod':'bacalhau',
 'carp':'carpa','catfish':'bagre','eel':'enguia','crab':'caranguejo','crayfish':'lagostim','duck':'pato','quail':'codorna',
 'rabbit':'coelho','rabbits':'coelhos','horse':'cavalo','horses':'cavalos','lambs':'cordeiros','buffalo':'búfalo',
 'algae':'algas','microalgae':'microalgas','leaves':'folhas','leaf':'folha','leaf extract':'extrato de folha','extract':'extrato',
 'extracts':'extratos','aqueous extract':'extrato aquoso','crude extract':'extrato bruto','yeast extract':'extrato de levedura',
 'ginseng':'ginseng','alfalfa':'alfafa','peel':'casca','fermented':'fermentado','brassica':'brássicas','agar':'ágar',
 'total parenteral nutrition':'nutrição parenteral total','high-fat diet':'dieta rica em gordura','licorice':'alcaçuz',
 'cranberry':'oxicoco (cranberry)','pomegranate':'romã','turmeric':'cúrcuma','walnuts':'nozes','spices':'especiarias',
 'herbal':'fitoterápico','castor':'mamona','dressing':'molho','dressings':'molhos','snail':'caracol','bee':'abelha','bees':'abelhas',
 'sweet':'doce','date':'tâmara','waters':'águas',
 # Outros termos frequentes
 'hydrogen peroxide':'peróxido de hidrogênio','h2o2':'peróxido de hidrogênio','nitric oxide':'óxido nítrico',
 'carbon dioxide':'dióxido de carbono','co2':'dióxido de carbono','carbon monoxide':'monóxido de carbono',
 'nitrous oxide':'óxido nitroso','hydrogen sulfide':'sulfeto de hidrogênio','superoxide':'superóxido','nitrogen':'nitrogênio',
 'hydrogen':'hidrogênio','carbon':'carbono','ammonia':'amônia','nitrate':'nitrato','nitrite':'nitrito','sulfate':'sulfato',
 'cadmium':'cádmio','arsenic':'arsênio','lead':'chumbo','mercury':'mercúrio','aluminum':'alumínio','nickel':'níquel',
 'silver':'prata','cobalt':'cobalto','malondialdehyde':'malondialdeído','lipopolysaccharide':'lipopolissacarídeo',
 'lps':'lipopolissacarídeo','reactive oxygen species':'espécies reativas de oxigênio','glycerol':'glicerol','phenol':'fenol',
 'phenols':'fenóis','acetaldehyde':'acetaldeído','formaldehyde':'formaldeído','acrylamide':'acrilamida','glyphosate':'glifosato',
 'bisphenol a':'bisfenol A','steroid':'esteroide','steroids':'esteroides','sterols':'esteróis','phospholipids':'fosfolipídios',
 'phosphatidylcholine':'fosfatidilcolina','bile acids':'ácidos biliares','bile acid':'ácido biliar','polyamines':'poliaminas',
 'spermine':'espermina','spermidine':'espermidina','putrescine':'putrescina','xanthine':'xantina','hypoxanthine':'hipoxantina',
 'inosine':'inosina','purine':'purina','trypsin':'tripsina','pepsin':'pepsina','covid-19':'COVID-19',
 'polycystic ovary syndrome':'síndrome dos ovários policísticos','non-alcoholic fatty liver disease':'doença hepática gordurosa não alcoólica',
 'nonalcoholic fatty liver disease':'doença hepática gordurosa não alcoólica','nephrotoxicity':'nefrotoxicidade',
 'microbiology':'microbiologia','organic':'orgânico','smoking':'tabagismo',
 'glycosides':'glicosídeos','sulfide':'sulfeto','ethylene':'etileno','acids':'ácidos','papaverine':'papaverina',
 'bicuculline':'bicuculina','thapsigargin':'tapsigargina','epsilon-polylysine':'épsilon-polilisina','acetylglycine':'acetilglicina',
 'forskolin':'forscolina','carbon tetrachloride':'tetracloreto de carbono','streptozotocin':'estreptozotocina','endotoxin':'endotoxina',
 'vitamin d':'vitamina D','vitamin c':'vitamina C','vitamin e':'vitamina E','vitamin a':'vitamina A','vitamin b12':'vitamina B12',
 'omega-3':'ômega-3','fiber':'fibras','dietary fiber':'fibras alimentares','walnut':'noz','almond':'amêndoa','soy protein':'proteína de soja',
 'mevalonic acid':'ácido mevalônico','farnesyl pyrophosphate':'pirofosfato de farnesila','coenzyme a':'coenzima A','squalene':'esqualeno',
 'ubiquinone':'ubiquinona','lipoprotein':'lipoproteína','apolipoprotein':'apolipoproteína',
 'geranylgeraniol':'geranilgeraniol','berberine':'berberina','juice':'suco',
 'staurosporine':'estaurosporina','strychnine':'estricnina','muscimol':'muscimol','picrotoxin':'picrotoxina','tetrodotoxin':'tetrodotoxina',
}

def pt(name):
    """Portuguese name when reviewed, otherwise None."""
    return PT.get(_k(name))

def display(name):
    """Name to show in the interface: Portuguese when available, otherwise the original term."""
    value = pt(name)
    if not value:
        return name
    return value[0].upper() + value[1:] if value[0].isalpha() and value[0].islower() and not value.startswith(('l-', 'd-')) else value

def labels():
    """(Portuguese label, original English term) pairs used as additional search aliases."""
    seen = set()
    for en, pt_name in PT.items():
        base = pt_name.split(' (')[0].strip()
        for label in {pt_name, base}:
            if (label, en) not in seen:
                seen.add((label, en))
                yield label, en

SEVERITY = {'major': 'grave', 'moderate': 'moderada', 'minor': 'leve'}
ACTIONS = {'GENERALLY AVOID': 'geralmente evitar', 'MONITOR': 'monitorar', 'ADJUST DOSING INTERVAL': 'ajustar intervalo entre doses',
           'ADJUST DOSE': 'ajustar dose', 'CONTRAINDICATED': 'contraindicado'}

def severity(label):
    """Translate Drugs.com severity labels such as 'Major · GENERALLY AVOID'."""
    if not label:
        return label
    parts = [p.strip() for p in str(label).replace('┬À', '·').split('·')]
    out = [SEVERITY.get(parts[0].lower(), parts[0])]
    out += [ACTIONS.get(p.upper(), p.lower()) for p in parts[1:] if p]
    return ' · '.join(out)

def _strip(s):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFKD', _k(s)) if not unicodedata.combining(c))

_REVERSE = {}
for _en, _pt in PT.items():
    for _label in (_pt, _pt.split(' (')[0]):
        _REVERSE.setdefault(_strip(_label), _en)

def english(term):
    """Original English term for a reviewed Portuguese name (used to search source-language tables)."""
    return _REVERSE.get(_strip(term))
