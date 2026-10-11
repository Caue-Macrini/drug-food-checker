# Avaliação cega das regras de risco

Scripts usados na avaliação de 11/10/2026 (resultado em `data/avaliacao-cega-2026-10-11.json` e em `CLASSIFICACAO-RISCO.md`).

1. `gerar_amostras.py PASTA` — sorteia, com semente fixa, 120 trechos da base inteira (estratificados pela saída das regras) e 60 pares realistas (medicamento comum + alimento comum), excluindo os trechos usados no ajuste das regras. Grava versões "cegas" (sem a saída das regras) e as chaves.
2. Julgamento — cada item é julgado por dois juízes independentes que leem apenas o arquivo cego; divergências vão a um terceiro juiz. Em 11/10/2026 os juízes foram instâncias de modelo de linguagem (definição de "interação" registrada no JSON de resultado). Para uma validação humana, use a planilha `data/amostra-revisao-trechos.csv` ou os arquivos cegos.
3. `pontuar.py PASTA` — reclassifica os trechos com as regras atuais, lê o nível dos pares nas tabelas derivadas e calcula precisão, sensibilidade, especificidade e acurácia.
4. `exportar.py PASTA` — grava itens, rótulos e métricas em `data/avaliacao-cega-2026-10-11.json`.

Execute a partir de `backend/`, por exemplo: `../.venv/Scripts/python.exe avaliacao/pontuar.py C:/caminho/da/pasta`. Os scripts importam `risk_rules` e `foodrugs_store`; rode-os com `backend/` no caminho de importação.
