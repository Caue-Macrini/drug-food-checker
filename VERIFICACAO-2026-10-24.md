# Verificação da entrega — 24/10/2026

A versão ativa, no servidor local e no endereço público, é `foodrugs-4.0.0-completa`. A integração integral já estava implementada; nesta revisão foi recompilada, reativada a publicação e verificado o funcionamento sobre o banco instalado.

## Banco completo

- `PRAGMA quick_check`: `ok`.
- Contagem efetiva das dez tabelas originais: todas coincidem com `data/foodrugs-full-manifest.json`, totalizando 30.797.702 registros.
- 1.108.429 registros em `TM_interactions`, 439.338 em `texts` e 26.365.254 em `cmap_foodrugs`.
- Última página de cada uma das dez tabelas acessível pelo adaptador utilizado pela API, incluindo as tabelas com milhões de registros.
- Índices `_tm` e `_tm_signal`: 1.108.429 registros cada. `_pair_risk`: 632.092 pares.
- O checksum registrado na importação continua no manifesto. Nesta revisão foi verificada a integridade do SQLite e recontadas as tabelas; não foi necessário baixar novamente o dump.

## Testes executados

- `backend`: `../.venv/Scripts/python.exe -m pytest -q`: **66 aprovados**. Avisos de depreciação de dependências e de permissão do cache pytest, sem falhas nos testes.
- `frontend`: `npm run build`: compilação de produção concluída.
- `frontend`: `node foodrugs.e2e.mjs`: aprovado no endereço HTTPS público e novamente em localhost, Chrome desktop e viewport móvel de 390 px.
- Fluxos verificados no navegador: cadastro com consentimento, busca pelos sinônimos sinvastatina/toranja, consulta e explicação da classificação, evidências e paginação, catálogo e mais alimentos, manifesto, pesquisa molecular por resveratrol, tabela original por identificador, histórico e reabertura de consulta. Nenhum erro JavaScript capturado e nenhuma rolagem horizontal indevida no teste móvel.
- Conta descartável da execução pública excluída; ausência confirmada no banco de contas.
- Capturas `preview-foodrugs-resultado.png`, `preview-foodrugs-evidencia.png`, `preview-foodrugs-completa.png` e `preview-foodrugs-mobile.png` atualizadas. O teste agora posiciona a página no topo antes da captura para alinhar o menu fixo.

## Operação e limites

O endereço atual está em `.local-run/LINK-PUBLICO.txt`. Para abrir ou recriar o túnel, execute `ABRIR-LINK-PUBLICO.cmd`. O computador deve permanecer ligado e conectado; o endereço pode mudar quando o túnel for recriado. A alternativa local é http://127.0.0.1:8000.

O banco integral permanece em `.local-data/foodrugs-v4.sqlite`, fora do GitHub por seu tamanho. Os programas de instalação e o manifesto estão no repositório. Outro computador precisa executar a instalação integral.

Os testes verificam funcionamento técnico, não validação clínica. A FooDrugs contém associações de mineração de texto e dados moleculares; as cores são derivadas pelas regras documentadas do aplicativo, não por MLP ou por um campo de risco nativo da FooDrugs. E-mails continuam na caixa local de demonstração. Não foi realizado teste de carga nem implantação permanente.
