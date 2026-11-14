# Avaliação por farmacêuticos (padrão-ouro humano)

Protocolo para medir o desempenho do Drug-Food Checker contra o julgamento de profissionais. Ele substitui
os juízes de modelo de linguagem usados em 11/10/2026 por avaliadores humanos independentes.

## Desenho

- **Amostra estratificada** de 133 pares medicamento × alimento (semente 20261114), sorteada de um universo de
  961 pares avaliáveis:
  - E2: nível 2 (vermelho), 30 de 69;
  - E1c: nível 1 com rótulo curado (Drugs.com), 25 de 92;
  - E1t: nível 1 vindo só da mineração de texto, 25 de 267;
  - E0: nível 0 (há registros, nenhuma interação identificada), 30 de 533;
  - CTRL: 25 interações clássicas da literatura (varfarina + vitamina K, IMAO + tiramina, tetraciclina + leite,
    levodopa + proteína etc.), incluídas qualquer que seja a resposta do sistema. Dois controles já caíram no
    sorteio aleatório; os outros 23 entram como estrato à parte.
- **Universo**: E1t e E0 restritos a 83 medicamentos comuns × 52 alimentos comuns. E2 e E1c incluem todos os
  pares de nível 2 ou com rótulo curado cujos termos passam pelo filtro de termos não alimentares.
- **Cegamento**: o avaliador vê só o par (nome em português e termo original) e até 3 artigos do PubMed como
  apoio opcional. Links do Drugs.com e do DrugBank foram excluídos porque revelam a gravidade curada. Cada
  avaliador recebe os pares em ordem diferente.
- **Classes**: 0 sem interação relevante; 1 orientar/monitorar; 2 evitar, espaçar ou ajustar dose;
  NS evidência insuficiente; INV par inválido. Também registra confiança e fonte principal.
- **Padrão-ouro**: classe igual nos dois avaliadores; nas divergências, decisão de um terceiro farmacêutico
  (adjudicação).
- **Resposta do sistema**: positivo = nível ≥ 1. "Sem registro na base" conta como negativo, porque é o que o
  usuário recebe.

## Arquivos

| Arquivo | Para quem | Conteúdo |
|---|---|---|
| `kit/avaliador_A.xlsx`, `kit/avaliador_B.xlsx` | Farmacêuticos A e B | Instruções, definições e a planilha cega |
| `kit/amostra_cega.json` | — | Os mesmos pares, sem a saída do sistema |
| `kit/gabarito_sistema.json` | **Somente o pesquisador** | Nível do sistema, estrato e tamanhos para ponderação |
| `kit/adjudicacao.csv` | Terceiro farmacêutico | Gerado automaticamente com as divergências |
| `kit/relatorio_avaliacao.md` / `.json` | TCC | Resultado final |

## Passo a passo

1. **Recrutar** 2 farmacêuticos com CRF ativo (de preferência com experiência clínica ou hospitalar) e um
   terceiro para adjudicar. Registrar o consentimento de uso do nome nos agradecimentos.
2. **Enviar** a cada um apenas a sua planilha (`avaliador_A.xlsx` ou `avaliador_B.xlsx`). Nunca enviar o
   `gabarito_sistema.json`. O tempo estimado é de 2 a 4 horas.
3. **Receber** as planilhas preenchidas, salvá-las em `backend/avaliacao/kit/` com o mesmo nome e rodar:
   `..\.venv\Scripts\python.exe avaliacao\kit_concordancia.py avaliacao\kit`
4. **Adjudicar**: enviar `adjudicacao.csv` ao terceiro avaliador. Ele preenche a coluna `decisao` com 0, 1, 2,
   NS ou INV. Depois rode o passo 3 de novo. As decisões já escritas são preservadas.
5. **Relatar** no TCC: o kappa entre avaliadores (com IC95%) e a sensibilidade, especificidade, VPP e VPN.
   - Amostra aleatória: com IC de Wilson.
   - Universo ponderado: cada par vale N_h/n_h do seu estrato.
   - Controles: a sensibilidade do sistema para interações clássicas.

   Também entram a matriz 3×3 e a lista de falsos negativos.

Para regenerar o kit (mesma semente, mesmo resultado):

```
..\.venv\Scripts\python.exe avaliacao\kit_amostra.py avaliacao\kit
python avaliacao\kit_planilhas.py avaliacao\kit A B   # requer openpyxl
```

## Interpretação

- Kappa entre avaliadores: < 0,40 fraco; 0,41–0,60 moderado; 0,61–0,80 substancial; > 0,80 quase perfeito
  (Landis e Koch, 1977). Abaixo de 0,60, revise as definições antes de usar o padrão-ouro.
- VPP do estrato E2 é a pergunta "quando o sistema diz vermelho, o farmacêutico concorda?".
- Sensibilidade nos controles mostra lacunas de cobertura da base. Antes da avaliação, já se sabe que 6 dos 25
  controles não têm registro para o termo sugerido em primeiro lugar e 3 aparecem como nível 0.

## Limitações a declarar

- Dois avaliadores e uma amostra de 133 pares dão intervalos de confiança largos por estrato.
- O universo de E0/E1t depende das listas de termos comuns definidas em `kit_amostra.py`.
- Os controles foram escolhidos pelo pesquisador; servem para medir sensibilidade a interações conhecidas,
  não prevalência.
