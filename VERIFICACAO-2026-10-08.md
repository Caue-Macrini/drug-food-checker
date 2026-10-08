# Verificação de 08/10/2026

- 25 testes Python aprovados, incluindo isolamento de contas, importação/reativação, histórico preservado, catálogo ativo, paginação, busca e orientação da fonte.
- Build de produção Vite aprovado.
- Fluxo Chrome local completo: cadastro, busca/limpeza, consulta, evidências, grafo, perfil persistente, histórico, exportação, mobile, SMTP local, redefinição de senha e exclusão.
- Fluxo HTTPS: catálogo de 25 medicamentos, três páginas, busca por alimento e sinônimo, seleção de alimentos associados, resultados com orientação/fonte/data, grafo, histórico e mobile. Cookie Secure/HttpOnly verificado.
- Importação do catálogo com backup prévio do SQLite; preservação de contas e histórico.

Os testes não são validação clínica. Não houve benchmark de carga, teste PostgreSQL/Docker, implantação permanente ou entrega SMTP a destinatários reais. Há dois avisos de depreciação nas dependências de teste, sem falhas.
