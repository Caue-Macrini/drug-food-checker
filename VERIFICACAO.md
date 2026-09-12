# Verificação — 12/09/2026

- 17 testes Python aprovados: conta, consentimento, perfil, regras, isolamento, recuperação de senha, revogação, exclusão, CSRF, limite de taxa, versionamento e conversão FooDrugs.
- Compilação Vite concluída, com dependências instaladas por package-lock.json.
- E2E Chrome aprovado: cadastro, consentimento, consulta, grafo, perfil, histórico, visualização/exportação JSON e exclusão.
- Layout verificado em 1440 px e 390 px, sem rolagem horizontal no celular e sem erros JavaScript.
- Fontes tipográficas incluídas localmente, sem requisições ao Google Fonts na execução.
- Nenhuma conta de teste permanece no banco local.
- Servidor iniciado pelo start.ps1 usando o ambiente .venv do próprio projeto.

Os testes emitiram dois avisos de depreciação das dependências Starlette/httpx e AnyIO, sem falhas.

Não executado: PostgreSQL via Docker (Engine desligado), SMTP real, HTTPS público, teste de carga da base integral e validação clínica. A amostra FDA ativa tem cinco associações não classificadas. O arquivo separado FooDrugs tem 100 registros reais para revisão/importação; o dump integral não foi baixado.
