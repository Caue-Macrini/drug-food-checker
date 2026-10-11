# FooDrugs completa no Drug-Food Checker

## Escopo da importação

O aplicativo importa integralmente o arquivo `FinalFooDrugs_v4.sql` da FooDrugs 4.0.0, disponibilizado pelo IMDEA Food Institute no [Zenodo](https://doi.org/10.5281/zenodo.8192515). O arquivo oficial tem 1.561.331.208 bytes e MD5 `3c8f26240dd571ded1e4b100d1dfc9d2`. A atribuição da base é CC BY 4.0. As tabelas e valores originais são preservados em um banco SQLite separado, sem executar o SQL baixado.

As dez tabelas importadas são `TM_interactions`, `texts`, `cmap`, `cmap_foodrugs`, `nodes`, `sample`, `study`, `misc_sample`, `misc_study` e `topTable`. Não se somam contagens históricas de outras versões à versão 4.

## Resultado da importação (10/10/2026)

| Tabela | Registros |
|---|---:|
| `TM_interactions` (associações extraídas de textos) | 1.108.429 |
| `texts` (documentos e trechos) | 439.338 |
| `cmap_foodrugs` (resultados moleculares, escore tau) | 26.365.254 |
| `topTable` (expressão gênica diferencial) | 2.799.422 |
| `cmap` (compostos, genes, linhagens) | 70.895 |
| `misc_sample` | 6.846 |
| `sample` | 4.559 |
| `nodes` | 2.617 |
| `misc_study` | 192 |
| `study` | 150 |
| **Total** | **30.797.702** |

Índices de consulta: 161.495 termos de medicamentos, 50.796 termos alimentares/bioativos, 632.092 pares distintos e 437.677 documentos associados a pares. Registros textuais sem documento correspondente: 0. Registros sem par pesquisável: 0. O banco resultante `.local-data/foodrugs-v4.sqlite` tem cerca de 2,7 GB. As contagens também estão em `data/foodrugs-full-manifest.json` e na tela **Dados FooDrugs**.

Desempenho medido na camada de dados, no computador da apresentação: busca de termo 2–5 ms; evidências de um par 4–16 ms; busca na base de conhecimento cerca de 80 ms (até 0,8 s na primeira consulta, com cache frio); busca molecular por termo cerca de 0,1–0,2 s; páginas profundas das tabelas grandes (ex.: offset de 20 milhões em `cmap_foodrugs`) 0,8–1,9 s. Não houve teste de carga com usuários simultâneos.

## Uso na aplicação

- **Consultar interação:** consulta todos os registros textuais do par escolhido. Evidências são paginadas, com identificadores, contexto original e referência do documento. A primeira página é preservada no histórico com a contagem total e a versão; as demais evidências são consultadas na mesma versão imutável da FooDrugs.
- **Base de conhecimento:** busca termos originais e alguns sinônimos em português, com catálogo e alimentos relacionados paginados. Nomes podem representar classes, compostos ou erros de extração; a contagem de termos não equivale ao número de medicamentos comercializados.
- **Dados FooDrugs:** mostra integridade e contagens, relações moleculares vinculadas a estudos/amostras e todas as tabelas originais, navegáveis por páginas ou identificador. Células longas são abreviadas apenas na interface; o banco contém os valores integrais.
- A normalização de caixa e acentos agrupa termos somente nos índices de busca. As tabelas originais não são alteradas, e registros sem par pesquisável permanecem acessíveis no explorador.

Associações textuais são candidatas produzidas pela mineração de texto original da FooDrugs. O nível de risco exibido (verde, amarelo, vermelho) é derivado por regras explícitas sobre esses trechos e gravado nas tabelas derivadas `_tm_signal` e `_pair_risk`; ver [CLASSIFICACAO-RISCO.md](CLASSIFICACAO-RISCO.md). O escore tau dos dados moleculares não é convertido em risco. Os dados moleculares mantêm seu contexto experimental e são apresentados separadamente. Usar a base completa não significa ter uma base clinicamente validada ou cobertura de todas as interações existentes.

## Instalação reproduzível

Depois de `setup.ps1`, execute na pasta do projeto:

```powershell
./Instalar-FooDrugs.ps1
./Apresentar.ps1
```

É necessário espaço para o download, partes de retomada, banco e índices (reserve pelo menos 10 GB). A instalação demora conforme a conexão e o computador. Verifica o checksum, lê todas as tabelas, constrói índices, verifica integridade e só então ativa `foodrugs-4.0.0-completa`. Faz backup do banco de contas SQLite antes da ativação. Não apaga contas, consultas nem as versões anteriores.

O dump e o banco grande ficam em `.local-data/`, fora do GitHub e dos pacotes de código. O repositório inclui os programas de download/importação, testes e manifesto; não contém uma cópia parcial disfarçada de base completa. Para outro computador, execute a instalação integral. A aplicação precisa do banco `.local-data/foodrugs-v4.sqlite`; `FOODRUGS_DB` permite configurar outro caminho.

Uma importação JSON pela Administração troca a versão ativa. Para voltar à FooDrugs, use **Ativar versão** em `foodrugs-4.0.0-completa`. O sistema impede ativar essa versão se seu banco não estiver instalado. Não execute duas instalações simultâneas. Se a importação for interrompida e deixar um estágio incompleto, preserve-o para diagnóstico e refaça o estágio a partir do dump já verificado.

## Verificação

O manifesto registra contagens por tabela, tamanho e checksum do arquivo, quantidade indexada e referências textuais ausentes. Os testes usam banco temporário para verificar escapes SQL, valores nulos, recusa de arquivo parcial, busca por sinônimos, paginação e ausência de inferência clínica. A consulta do histórico continua isolada por conta.

O explorador científico consulta o arquivo local. Abrir os documentos e estudos nos sites de origem exige internet. A publicação por túnel continua temporária e depende do computador ligado; não é hospedagem permanente.
