# Avaliação por bulas oficiais (padrão de referência documental)

Alternativa à avaliação por farmacêuticos. Usa a mesma amostra de 133 pares, com a mesma semente, os mesmos
scripts e o mesmo gabarito do sistema. Muda só a fonte do padrão de referência: em vez da opinião de
profissionais, vale o que as bulas oficiais dizem.

## Por que bulas

- A RDC 47/2009 da ANVISA exige que a bula descreva as interações medicamento-alimento: item 4 da bula do
  paciente ("O que devo saber antes de usar este medicamento?") e item 6 da bula do profissional ("Interações
  medicamentosas").
- A fonte é oficial, pública e reproduzível: qualquer membro da banca pode conferir um par abrindo a bula.
- Não envolve participantes humanos nem opinião clínica. Mesmo assim, confirme com a orientadora se é
  necessário submeter ao comitê de ética.

## Desenho

- **Extratores**: os dois autores (A = Cauê, B = João Pedro). Cada um trabalha de forma independente na sua
  planilha, sem abrir o Drug-Food Checker, o gabarito ou a planilha do outro. A planilha não mostra a
  classificação do sistema.
- **Fonte**: Bulário Eletrônico da ANVISA, priorizando a bula do profissional do medicamento de referência.
  Se o medicamento não for registrado no Brasil, vale a bula do FDA (DailyMed), seções *Drug Interactions* e
  *Dosage and Administration*.
- **Critérios** (também estão na aba Instruções da planilha):
  - 2: a bula manda evitar, contraindica, manda espaçar a tomada ou ajustar dose por causa do alimento.
  - 1: a bula cita efeito possível ou pequeno, ou orienta a tomada, sem mandar evitar ou espaçar.
  - 0: a bula não menciona o alimento, o grupo que o contém nem o componente.
  - NS: bula não encontrada.
  - INV: par inválido.

  Conta como menção o próprio alimento, o grupo que o contém ("laticínios", "bebidas alcoólicas") ou o
  componente nomeado ("alimentos ricos em vitamina K"). Orientações genéricas como "tomar com ou sem alimentos"
  não contam para alimentos específicos.
- **Justificativa obrigatória**: para as classes 1 e 2, copie a frase da bula na última coluna.
- **Adjudicação**: as divergências vão para `adjudicacao.csv`, e a orientadora decide preenchendo a coluna
  `decisao`.
- **Resposta do sistema**: o nível que o aplicativo mostra (`level` no gabarito). Positivo = nível ≥ 1.
  "Sem registro" conta como negativo.

## Passo a passo

1. Abra `kit-bulas/avaliador_A.xlsx` (Cauê) e `kit-bulas/avaliador_B.xlsx` (João Pedro). Os pares são os
   mesmos, em ordem diferente. Muitos pares repetem o medicamento: abra a bula uma vez e use-a para todos os
   alimentos dele (filtre a coluna Medicamento).
2. Quando os dois terminarem, salve as planilhas em `backend/avaliacao/kit-bulas/` e rode (em `backend/`):
   `..\.venv\Scripts\python.exe avaliacao\kit_concordancia.py avaliacao\kit-bulas`
3. Envie `kit-bulas/adjudicacao.csv` à orientadora. Ela preenche a coluna `decisao` com 0, 1, 2, NS ou INV, e você
   roda o passo 2 de novo.
4. O resultado sai em `kit-bulas/relatorio_avaliacao.md` e `.json`:
   - concordância entre os extratores;
   - sensibilidade, especificidade, VPP e VPN do sistema, na amostra aleatória (com IC95%), no universo
     ponderado e nos controles da literatura;
   - matriz 3×3 sistema × referência;
   - lista de falsos negativos.

Para regenerar as planilhas: `python avaliacao\kit_planilhas.py avaliacao\kit-bulas A B --bulas` (requer
openpyxl; os arquivos `amostra_cega.json` e `gabarito_sistema.json` de `kit-bulas` são cópias dos de `kit`).

## Limitações a declarar no TCC

- Bula que não cita a interação não prova que ela não existe. Bulas omitem interações descritas na literatura,
  então classe 0 significa "não consta na bula". Isso tende a aparecer como falso positivo do sistema, quando o
  sistema acerta e a bula é que não cita.
- Os extratores são os autores do sistema. Isso é mitigado por três cuidados: a planilha não mostra a resposta
  do sistema, as extrações são independentes e a justificativa (frase da bula) fica registrada e pode ser
  auditada.
- Com dois extratores e 133 pares, os intervalos de confiança por estrato ficam largos.
- A bula do medicamento de referência pode diferir da de genéricos e similares. A versão consultada é a vigente
  na data da extração; registre a data.
