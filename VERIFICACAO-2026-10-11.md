# Verificação de 11/10/2026 — classificação de risco por cores

## O que mudou

- Resultado com indicador verde/amarelo/vermelho (TCC, RF008 e Figura 16), resposta direta em português, explicação de como a interação acontece e a seção "Por que esta classificação".
- O nível base é derivado por regras explícitas (`regras-evidencia-1.5`) aplicadas aos 1.108.429 trechos da FooDrugs; detalhes em [CLASSIFICACAO-RISCO.md](CLASSIFICACAO-RISCO.md).
- Modificadores do perfil clínico (Tabela 2 do TCC) aplicados à FooDrugs, apenas quando há interação identificada.
- Evidências ordenadas, com os trechos que indicam interação primeiro, cada uma marcada como "Indica interação", "Apenas menciona os dois" ou "Sem efeito observado".
- Sugestões de alimentos coloridas pelo nível de risco; cerca de 90 sinônimos em português (ex.: cafeína, teofilina, chá verde, suco de toranja).
- Reclassificação atômica: as tabelas derivadas são montadas à parte e trocadas numa única transação; o sistema não lê tabelas vazias durante a atualização.
- `Publicar-Apresentacao.ps1` aguarda até cerca de 30 segundos pela resposta do túnel antes de desistir.

## Testes

- 66 testes Python aprovados, incluindo 37 casos das regras de risco: frases de interação, menções, estudos sem efeito, química, estudos em animais, interação estatística, listas ("evite café e cafeína"), alimentos que contêm o medicamento, gravidade das monografias, modificadores do perfil, par ausente e par sem classificação.
- Build de produção aprovado.
- `foodrugs.e2e.mjs` aprovado no Chrome: indicador colorido, resposta, "Por que esta classificação", trecho com marcação, paginação, base de conhecimento, tabelas científicas, histórico e mobile, sem erros JavaScript.
- `capturas.mjs` gerou as capturas em `capturas-tcc/` (vermelho, amarelo, verde, par sem registro, ajuste pelo perfil e celular) e removeu a conta de captura.

## Revisão de código

Uma revisão independente do código novo apontou 30 possíveis problemas; os confirmados foram corrigidos e cobertos por testes:

- Teste do modo catálogo quebrado.
- "Carregar mais evidências" mostrando nível diferente do resultado.
- Histórico antigo com evidências duplicadas.
- Falha com par sem classificação.
- Orientação do catálogo ausente.
- Ícone e textos inadequados para resultados não classificados.
- Modificadores criando interação.
- Reclassificação não atômica.
- Gravidade do Drugs.com atribuída a termos secundários.
- Termos ambíguos nas regras ("taken together", "double-blind", "patients were monitored", "passive avoidance").
- Frases mistas classificadas como "sem efeito".

## Desempenho das regras

| Medida | Resultado |
|---|---|
| Interações do Drugs.com reconhecidas só pelos artigos (45 pares) | 80% |
| Interações do catálogo FDA/MedlinePlus que não ficam verdes (26 pares na base) | 88,5% |
| Avaliação cega, 60 pares realistas: precisão / sensibilidade / especificidade / acurácia | 86,7% / 70,3% / 82,6% / 75,0% |
| Avaliação cega, 120 trechos da base inteira: precisão dos trechos "indica interação" | 26,7% |

Os juízes da avaliação cega foram instâncias de modelo de linguagem, com dois juízes independentes e desempate; não houve validação por especialistas humanos. Os dados estão em `data/avaliacao-cega-2026-10-11.json`, e a planilha `data/amostra-revisao-trechos.csv` permite a revisão humana.

## Não verificado

- Validação clínica.
- Revisão humana da amostra.
- Teste de carga.
- PostgreSQL/Docker com a base completa.
- `e2e.mjs` e `library.e2e.mjs`, que exigem ativar o catálogo complementar e não foram executados, para não trocar a base ativa da apresentação. As telas do modo catálogo foram ajustadas para manter os títulos que esses testes procuram.
