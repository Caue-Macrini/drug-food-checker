"""Build one blinded spreadsheet per evaluator from amostra_cega.json (needs openpyxl).

Usage:  python avaliacao/kit_planilhas.py avaliacao/kit [A B C]
        python avaliacao/kit_planilhas.py avaliacao/kit-bulas A B --bulas   (reference standard = official labels)
Each evaluator gets the same pairs in a different order (reduces fatigue/order effects) and never sees
the system output. Answer cells are unlocked; the rest of the sheet is protected (no password) to avoid
accidental edits.
"""
import json, random, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side, Protection
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule

BULAS = '--bulas' in sys.argv
ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
KIT = Path(ARGS[0] if ARGS else 'avaliacao/kit')
EVALUATORS = ARGS[1:] or ['A', 'B']
data = json.load(open(KIT / 'amostra_cega.json', encoding='utf-8'))

CLASSES = ['0 - Sem interação clinicamente relevante',
           '1 - Interação possível: orientar ou monitorar',
           '2 - Interação relevante: evitar, espaçar ou ajustar dose',
           'NS - Evidência insuficiente para julgar',
           'INV - Par inválido (termo não é medicamento ou alimento)']
CONFIDENCE = ['Alta', 'Média', 'Baixa']
SOURCES = ['Micromedex', 'Lexicomp', 'UpToDate', 'Stockley', 'Medscape', 'Drugs.com', 'Bula (ANVISA/FDA/EMA)',
           'Artigo científico', 'Conhecimento clínico', 'Outra']
HEAD = ['ID', 'Medicamento', 'Alimento', 'Termos originais da base', 'Artigo 1', 'Artigo 2', 'Artigo 3',
        'Classificação', 'Confiança', 'Fonte principal', 'Comentário (mecanismo, condição, dose)']
WIDTH = [7, 22, 22, 34, 11, 11, 11, 46, 11, 22, 46]

ink, muted, line = '1F2937', '6B7280', 'D1D5DB'
head_fill = PatternFill('solid', fgColor='1E3A5F')
answer_fill = PatternFill('solid', fgColor='FFF8E1')
thin = Border(*(Side(style='thin', color=line),) * 4)
wrap = Alignment(wrap_text=True, vertical='top')

INSTRUCTIONS = [
    ('Avaliação de interações medicamento–alimento', 'title'),
    ('Objetivo', 'h'),
    ('Construir um padrão-ouro independente para medir o desempenho do Drug-Food Checker. Você não verá a '
     'classificação do sistema; julgue cada par com base nas suas fontes de referência.', 'p'),
    ('Como preencher', 'h'),
    ('1. Abra a aba "Avaliação". Para cada linha, escolha a Classificação, a Confiança e a Fonte principal nas '
     'listas (células amarelas). O comentário é opcional, mas ajuda na adjudicação.', 'p'),
    ('2. Julgue o par em uso clínico habitual (dose usual, adulto, via oral) e a ingestão alimentar comum. '
     'Se a interação só ocorre em condição específica (dose alta, suplemento, jejum), registre no comentário.', 'p'),
    ('3. Os artigos são material de apoio opcional, sorteados da base FooDrugs; não indicam que a interação existe.', 'p'),
    ('4. Não consulte o Drug-Food Checker nem outro avaliador. Trabalhe de forma independente.', 'p'),
    ('5. Pode salvar e continuar depois. Ao terminar, devolva o arquivo sem renomear as colunas.', 'p'),
    ('Definições das classes', 'h'),
    ('0 — Sem interação clinicamente relevante: não há interação documentada ou ela não muda a conduta.', 'p'),
    ('1 — Interação possível: há evidência de interação de pequena magnitude ou incerta; cabe orientar o paciente '
     'ou monitorar (ex.: efeito modesto na absorção).', 'p'),
    ('2 — Interação relevante: exige evitar o alimento, espaçar a tomada ou ajustar a dose (ex.: risco de '
     'toxicidade, falha terapêutica, crise hipertensiva).', 'p'),
    ('NS — Use quando nenhuma fonte disponível permite decidir. Não é o mesmo que 0.', 'p'),
    ('INV — Use quando um dos termos não é um medicamento ou um alimento real (erro da extração automática).', 'p'),
    ('Confiança', 'h'),
    ('Alta: fontes concordantes e explícitas. Média: fonte única ou evidência indireta. Baixa: inferência.', 'p'),
    ('Tempo estimado', 'h'),
    ('Cerca de 1 a 2 minutos por par. Total de {n} pares.', 'p'),
    ('Privacidade', 'h'),
    ('A planilha não contém dados de pacientes. Seu nome aparece apenas no relatório de concordância como '
     '"Avaliador {ev}".', 'p'),
]

BULA_CLASSES = ['0 - A bula não descreve interação com este alimento',
                '1 - A bula orienta ou pede monitorar (efeito possível, sem restrição)',
                '2 - A bula manda evitar, espaçar a tomada ou ajustar a dose',
                'NS - Bula não encontrada ou sem a seção de interações',
                'INV - Par inválido (termo não é medicamento ou alimento)']
BULA_SOURCES = ['Bula ANVISA - profissional', 'Bula ANVISA - paciente', 'Bula FDA (DailyMed)', 'Bula EMA', 'Outra bula oficial']
BULA_HEAD = ['ID', 'Medicamento', 'Alimento', 'Termos originais da base', 'Buscar no Bulário (princípio ativo)', 'Bula FDA',
             'Classificação', 'Confiança', 'Fonte principal', 'Trecho da bula (copie a frase que justifica)']
BULA_WIDTH = [7, 22, 22, 30, 26, 12, 46, 11, 24, 60]
BULA_INSTRUCTIONS = [
    ('Extração documental: interações medicamento–alimento nas bulas oficiais', 'title'),
    ('Objetivo', 'h'),
    ('Construir um padrão de referência a partir das bulas oficiais para medir o desempenho do Drug-Food Checker. '
     'A RDC 47/2009 da ANVISA exige que a bula descreva as interações medicamento-alimento (item 4 da bula do paciente '
     'e item 6 da bula do profissional). Você não verá a classificação do sistema; classifique apenas pelo que a bula diz.', 'p'),
    ('Como preencher', 'h'),
    ('1. Para cada linha, abra o Bulário Eletrônico da ANVISA (consultas.anvisa.gov.br/#/bulario) e busque pelo princípio '
     'ativo da coluna E. Prefira a bula do PROFISSIONAL do medicamento de referência; na falta, a do paciente.', 'p'),
    ('2. Se o medicamento não for registrado no Brasil, use o link "Bula FDA" (DailyMed): seções Drug Interactions e '
     'Dosage and Administration.', 'p'),
    ('3. Procure o alimento ou o grupo que o contém. Conta como menção: o próprio alimento, a bebida, o grupo ("laticínios", '
     '"bebidas alcoólicas") ou o componente nomeado ("alimentos ricos em vitamina K", "alimentos com tiramina").', 'p'),
    ('4. Escolha a Classificação, a Confiança e a Fonte nas listas e cole no fim da linha a frase da bula que justifica '
     '(obrigatório para 1 e 2). Para 0, deixe vazio ou escreva "não consta".', 'p'),
    ('5. Não abra o Drug-Food Checker nem a planilha do outro extrator até terminar. As divergências serão decididas '
     'pela orientadora.', 'p'),
    ('Critérios das classes', 'h'),
    ('2 — a bula manda evitar o alimento, contraindica, manda espaçar a tomada (ex.: "tomar 2 horas antes de leite"), '
     'ou ajustar dose/monitorar exames por causa do alimento.', 'p'),
    ('1 — a bula cita efeito possível ou pequeno, ou orienta a tomada (ex.: "pode reduzir a absorção", "pode aumentar '
     'a sonolência"), sem ordem de evitar ou espaçar.', 'p'),
    ('0 — a bula não menciona o alimento, o grupo nem o componente. Atenção: isso significa "não consta na bula", '
     'não que a combinação seja segura.', 'p'),
    ('Orientações genéricas como "tomar com ou sem alimentos" ou "tomar após as refeições" não contam para alimentos '
     'específicos (classe 0), exceto quando o par é com "alimento"/"refeição".', 'p'),
    ('NS — bula não encontrada ou sem seção de interações. INV — um dos termos não é medicamento ou alimento real.', 'p'),
    ('Tempo estimado', 'h'),
    ('Cerca de 1 a 2 minutos por par; muitos pares repetem o mesmo medicamento. Total de {n} pares.', 'p'),
]

def build(ev, seed):
    items = list(data['itens'])
    random.Random(seed).shuffle(items)
    head, width = (BULA_HEAD, BULA_WIDTH) if BULAS else (HEAD, WIDTH)
    answer_col = head.index('Classificação') + 1
    last_col = len(head)
    wb = Workbook()
    info = wb.active; info.title = 'Instruções'
    info.column_dimensions['A'].width = 110
    info.sheet_view.showGridLines = False
    r = 1
    for text, kind in (BULA_INSTRUCTIONS if BULAS else INSTRUCTIONS):
        cell = info.cell(r, 1, text.format(n=len(items), ev=ev))
        cell.alignment = Alignment(wrap_text=True, vertical='top')
        if kind == 'title': cell.font = Font(size=16, bold=True, color=ink); r += 1
        elif kind == 'h': cell.font = Font(size=12, bold=True, color='1E3A5F')
        else: cell.font = Font(size=11, color=ink)
        r += 1
    info.cell(r + 1, 1, 'Avaliador:').font = Font(bold=True)
    name = info.cell(r + 2, 1, f'Avaliador {ev} — escreva aqui seu nome e registro profissional (CRF)')
    name.fill = answer_fill; name.protection = Protection(locked=False)
    col_letter = 'G' if BULAS else 'H'
    progress = info.cell(r + 4, 1, f'=CONCATENATE("Respondidos: ",COUNTA(Avaliação!{col_letter}2:{col_letter}{len(items) + 1})," de {len(items)}")')
    progress.font = Font(bold=True, color='1E3A5F')
    info.protection.sheet = True

    ws = wb.create_sheet('Avaliação')
    ws.append(head)
    for col, (h, w) in enumerate(zip(head, width), 1):
        c = ws.cell(1, col); c.fill = head_fill; c.font = Font(bold=True, color='FFFFFF'); c.alignment = wrap; c.border = thin
        ws.column_dimensions[c.column_letter].width = w
    from urllib.parse import quote
    for i, it in enumerate(items, 2):
        orig = f"{it['medicamento_original']} + {it['alimento_original']}"
        ws.cell(i, 1, it['id']); ws.cell(i, 2, it['medicamento']); ws.cell(i, 3, it['alimento']); ws.cell(i, 4, orig)
        if BULAS:
            ws.cell(i, 5, it['medicamento'])
            c = ws.cell(i, 6, 'DailyMed'); c.hyperlink = 'https://dailymed.nlm.nih.gov/dailymed/search.cfm?labeltype=all&query=' + quote(it['medicamento_original'])
            c.font = Font(color='1D4ED8', underline='single')
        else:
            for k in range(3):
                if k < len(it['artigos']):
                    c = ws.cell(i, 5 + k, f'PubMed {k + 1}'); c.hyperlink = it['artigos'][k]
                    c.font = Font(color='1D4ED8', underline='single')
                else:
                    ws.cell(i, 5 + k, '—').font = Font(color=muted)
        for col in range(1, last_col + 1):
            c = ws.cell(i, col); c.alignment = wrap; c.border = thin
            if col >= answer_col: c.fill = answer_fill; c.protection = Protection(locked=False)
        ws.row_dimensions[i].height = 30
    last = len(items) + 1
    letters = [ws.cell(1, answer_col + k).column_letter for k in range(3)]
    for idx, (values, col) in enumerate(zip(((BULA_CLASSES if BULAS else CLASSES), CONFIDENCE, (BULA_SOURCES if BULAS else SOURCES)), letters), 1):
        lists = wb['Listas'] if 'Listas' in wb.sheetnames else wb.create_sheet('Listas')
        for k, v in enumerate(values, 1): lists.cell(k, idx, v)
        letter = lists.cell(1, idx).column_letter
        dv = DataValidation(type='list', formula1=f'=Listas!${letter}$1:${letter}${len(values)}', allow_blank=True,
                            showErrorMessage=True, errorTitle='Valor inválido', error='Escolha um item da lista.')
        ws.add_data_validation(dv); dv.add(f'{col}2:{col}{last}')
    wb['Listas'].sheet_state = 'hidden'
    # Highlight rows still missing a classification.
    first_answer = letters[0]
    ws.conditional_formatting.add(f'A2:{ws.cell(1, answer_col - 1).column_letter}{last}', FormulaRule(formula=[f'${first_answer}2=""'], font=Font(bold=True, color=ink)))
    ws.freeze_panes = 'D2'
    ws.auto_filter.ref = f'A1:{ws.cell(1, last_col).column_letter}{last}'
    ws.protection.sheet = True
    ws.protection.autoFilter = False; ws.protection.sort = False
    wb.active = 1
    out = KIT / f'avaliador_{ev}.xlsx'
    wb.save(out)
    return out, len(items)

for k, ev in enumerate(EVALUATORS):
    out, n = build(ev, 1000 + k)
    print('gravado', out, n, 'pares')
