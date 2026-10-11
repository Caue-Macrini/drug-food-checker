# Classificação de risco por cores

## Por que é preciso derivar o nível de risco

O TCC define uma escala de três níveis — 0 sem risco identificado (verde), 1 atenção (amarelo), 2 risco elevado (vermelho) — e afirma, na p. 31, que "o nível base de cada interação é fornecido diretamente pela base FooDrugs". Na FooDrugs 4.0.0 isso não acontece: a tabela `TM_interactions` registra apenas que um medicamento e um alimento aparecem juntos num trecho de um documento. Não há campo de gravidade, tipo ou mecanismo.

Um mesmo par mistura trechos de natureza muito diferente. Em Cafeína + Teofilina (81 registros), por exemplo, um estudo mede redução de 29% no clearance da teofilina com a cafeína (interação real), enquanto outros só comparam os dois medicamentos.

O sistema, portanto, **deriva o nível base a partir dos próprios trechos**, com regras explícitas. É a mesma abordagem que a p. 31 do TCC defende para o ajuste por perfil: regras rastreáveis e auditáveis em vez de modelos probabilísticos, já que não existe conjunto rotulado público para o domínio. Não há rede neural nem modelo treinado.

## Etapa 1 — classificação de cada trecho

Cada um dos 1.108.429 registros textuais recebe uma das três categorias (`backend/risk_rules.py`, função `classify`):

| Categoria | Quando | Exemplo real |
|---|---|---|
| **Indica interação** | O trecho descreve alteração farmacocinética (concentração plasmática, biodisponibilidade, clearance, AUC, meia-vida, absorção, CYP450, P-gp), alteração de efeito (potencializa, antagoniza, reduz o efeito), efeito adverso da combinação, recomendação de uso (evitar, separar, monitorar) ou menciona explicitamente a interação | "the reduction in apparent total body clearance … of theophylline by 29% … concomitant administration of … caffeine" |
| **Sem efeito observado** | O trecho fala de interação ou farmacocinética e relata ausência de efeito ("did not alter the pharmacokinetics", "no significant interaction") | "Grapefruit juice did not alter the pharmacokinetics of fexofenadine…" |
| **Apenas menciona** | Os dois termos aparecem juntos sem descrição de interação | "…compare intravenous aminophylline with IV and oral caffeine…" |

Salvaguardas contra falsos positivos da base, que contém muitos trechos de ciência básica e termos mal extraídos:

- Alterações de efeito só contam em **contexto de uso humano**: pacientes, voluntários, dose, ingestão, suco, refeição, dieta, suplemento, alimentos comuns. Afirmações típicas de bula ("X may increase the plasma concentrations of Y") também contam.
- Termos farmacocinéticos específicos (biodisponibilidade, clearance, AUC, Cmax, meia-vida) dispensam essa palavra de contexto.
- Trechos de **estudos apenas em animais, células ou plantas**, sem menção a seres humanos, não contam, exceto quando trazem recomendação explícita.
- Vocabulário de química e materiais (ligação de hidrogênio, nanopartículas, baterias) e **interação estatística** ("their interaction", ANOVA) bloqueiam a classificação.
- Expressões ambíguas ficam de fora. "Taken together" costuma significar "em resumo"; "patients were monitored" descreve o método do estudo; "passive avoidance" é um teste de comportamento. Verbos são reconhecidos com terminação completa, para "double-blind" e "beta-blockers" não contarem como "dobrar" e "bloquear".
- **Frases mistas:** a parte negada é removida antes de procurar evidência positiva. Em "decreased the clearance of theophylline by 50% … no significant changes in volume of distribution", vale a redução de 50%. "Sem efeito observado" só é atribuído quando nada positivo sobra.
- **Aviso forte** exige recomendação explícita (evitar, contraindicado, não deve), sem negação ("need not be avoided"), ou efeito adverso grave. A palavra "severe" sozinha costuma qualificar a doença, não a interação.
- Alguns "alimentos" da FooDrugs são moléculas do próprio organismo ou ruído de extração (colesterol, glicose, proteína, insulina, óxido nítrico, creatinina, "SAME", "ACT"). Para eles, "a sinvastatina reduz o colesterol plasmático" é efeito do remédio, não interação; só contam com menção explícita à interação ou recomendação de uso (`NON_FOOD_TERMS`).

Trechos de monografias do **Drugs.com** incluídas na FooDrugs trazem a gravidade escrita no próprio texto ("Major Food Interaction||GENERALLY AVOID"). O sistema lê esse cabeçalho e usa a gravidade declarada (Major → 2; Moderate ou Minor → 1), **somente** quando o medicamento do par é o da monografia (endereço da página) e o alimento é o assunto daquela seção (frase de abertura). Assim, outros termos extraídos do mesmo texto, como exames de sangue ou nutrientes citados de passagem, não herdam a gravidade.

## Etapa 2 — nível base do par

Função `pair_level`, aplicada em ordem:

1. Se alguma monografia do Drugs.com classifica o par, vale a gravidade declarada (fonte de referência tem prioridade).
2. Se nenhum documento indica interação, ou se os documentos "sem efeito observado" são mais numerosos que os que indicam interação → **0, verde**.
3. Se 2 ou mais documentos trazem aviso forte → **2, vermelho**.
4. Se ao menos 1 documento indica interação → **1, amarelo**.

Par sem nenhum registro: **verde com ressalva**, conforme o fluxo alternativo do caso de uso "Consultar interação" (TCC, p. 39).

A força da evidência é informada à parte: ampla (5 ou mais documentos), moderada (2 a 4), limitada (1) ou fonte de referência com gravidade.

## Etapa 3 — ajuste pelo perfil clínico (Tabela 2 do TCC)

`NívelAjustado = mín(2, máx(0, NívelBase + Σ modificadores))`, com +1 para cada condição:

| Perfil | Combinado com | Origem da propriedade do medicamento |
|---|---|---|
| Insuficiência hepática | Medicamento metabolizado por CYP450 | Lista explícita de substratos conhecidos ou mecanismo CYP detectado nos trechos do par |
| Doença renal estágio ≥ 3 | Medicamento de excreção renal | Lista explícita (ex.: metformina, lítio, digoxina) |
| Idade ≥ 65 anos | Três ou mais medicamentos em uso | Perfil do usuário |
| Álcool ≥ 4 vezes por semana | Medicamento hepatotóxico | Lista explícita (ex.: paracetamol, isoniazida, metotrexato) |

As listas ficam em `backend/risk_rules.py`. Um medicamento fora delas simplesmente não ativa o modificador. Os modificadores **intensificam uma interação identificada** (nível base 1 ou 2), como descreve o TCC na p. 21 ("uma interação considerada moderada pode receber maior destaque"). Eles não criam interação: pares sem registro ou sem interação descrita permanecem verdes.

## O que o usuário vê

- Indicador circular colorido com resposta direta: "Evite consumir…", "Pode haver interação…" ou "Sem interação identificada", e a recomendação de procurar médico ou farmacêutico.
- **Como a interação acontece:** explicação simplificada em português, com a direção da alteração (aumenta ou reduz a quantidade do medicamento no sangue), o tipo (farmacocinética ou farmacodinâmica) e o mecanismo detectado (CYP450, quelação por minerais, vitamina K, tiramina etc.).
- **Por que esta classificação:** a gravidade da fonte, quantos trechos e documentos indicam interação, avisos fortes, estudos sem efeito e a regra aplicada.
- Ajustes do perfil clínico aplicados.
- Trechos originais, primeiro os que indicam interação, cada um com sua marcação.

## Desempenho medido (regras-evidencia-1.5, 11/10/2026)

**Resultado na base inteira:** dos 1.108.429 trechos, 50.369 indicam interação, 125 relatam ausência de efeito e 1.057.935 apenas mencionam os dois termos. Dos 632.092 pares, 123 ficam vermelhos, 39.192 amarelos e 592.777 verdes. Entre os pares vermelhos, 139 têm gravidade declarada pelo Drugs.com.

**1. Concordância com o Drugs.com** (fonte de referência com gravidade). Em 45 pares que têm monografia e também artigos na base, a monografia foi escondida e o par foi classificado só pelos artigos:

| Drugs.com | Regras: verde | Regras: amarelo | Regras: vermelho |
|---|---:|---:|---:|
| Moderate/Minor (36) | 7 | 28 | 1 |
| Major (9) | 2 | 7 | 0 |

As regras reconheceram a interação em **80%** dos pares (36 de 45). Distinguir Major de Moderate apenas pelos artigos é a parte fraca: por isso a gravidade declarada da monografia tem prioridade quando existe.

**2. Controle positivo — catálogo FDA/MedlinePlus.** Das 49 interações documentadas no catálogo complementar, 26 têm registros na FooDrugs. **88,5%** delas (23) saem amarelas ou vermelhas. As 3 verdes não têm, na base, nenhum trecho que descreva a interação (por exemplo, os trechos de buspirona + álcool tratam de fissura por álcool).

**3. Avaliação cega com amostras não usadas no ajuste** (`data/avaliacao-cega-2026-10-11.json`). Dois juízes independentes julgaram cada item sem ver a saída das regras; um terceiro desempatou as divergências. Os juízes foram instâncias de modelo de linguagem, e não especialistas humanos; a revisão humana pode ser feita com `data/amostra-revisao-trechos.csv`.

| Amostra | Resultado |
|---|---|
| **60 pares realistas** (medicamento comum + alimento comum; 30 amarelos/vermelhos e 30 verdes pelas regras) | Precisão **86,7%** · sensibilidade **70,3%** · especificidade **82,6%** · acurácia **75,0%** · acordo entre juízes 57/60 |
| 120 trechos sorteados da base inteira | Precisão 26,7% nos trechos marcados como "indica interação" · 8,3% dos trechos marcados como menção descrevem interação · acordo entre juízes 111/120 |

O resultado por **par realista** é o que importa para o usuário: quando o sistema mostra amarelo ou vermelho para um medicamento e um alimento comuns, em cerca de 87% dos casos há trecho descrevendo a interação. A precisão por trecho na base inteira é baixa porque a FooDrugs é dominada por ciência básica e por pares sem sentido clínico ("TPN + carotenoids", "NMDA + morphine"), que as regras de frase não conseguem separar completamente. Essa é uma limitação conhecida, e o motivo de cada resultado mostrar os trechos e a regra aplicada.

**Processo de ajuste:** as regras foram ajustadas em etapas (versões 1.0 a 1.5) com base em erros reais observados, na concordância com o Drugs.com, no controle do catálogo e em uma primeira amostra julgada de 180 trechos. A avaliação final usou amostras novas, sorteadas depois do ajuste, para não superestimar o desempenho. Os 37 casos de teste de `backend/test_risk_rules.py` fixam os erros corrigidos.

## Reprodução

```powershell
cd backend
../.venv/Scripts/python.exe classify_foodrugs.py   # cerca de 10 minutos; monta _tm_signal e _pair_risk à parte e troca as tabelas numa única transação
../.venv/Scripts/python.exe validate_risk.py       # gera data/validacao-classificacao.json e data/amostra-revisao-trechos.csv
# avaliação cega: ver backend/avaliacao/LEIAME.md
../.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider test_risk_rules.py
```

As tabelas originais da FooDrugs não são alteradas. `Instalar-FooDrugs.ps1` executa a classificação automaticamente.
