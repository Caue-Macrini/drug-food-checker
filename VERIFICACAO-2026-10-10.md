# Verificação de 10/10/2026 — FooDrugs completa

## Base

- Arquivo oficial `FinalFooDrugs_v4.sql` baixado do Zenodo: 1.561.331.208 bytes, MD5 `3c8f26240dd571ded1e4b100d1dfc9d2` conferido com o valor publicado. Lacunas de bytes nulos deixadas por uma gravação interrompida foram detectadas pela verificação e baixadas novamente antes da importação.
- 10 tabelas importadas, 30.797.702 registros, sem amostragem. `PRAGMA quick_check` aprovado.
- 1.108.429 registros textuais indexados; 0 sem documento correspondente; 0 sem par pesquisável.
- Versão `foodrugs-4.0.0-completa` ativada com backup prévio do banco de contas (`backups/antes-foodrugs-*.db`). Contas, histórico e versões anteriores preservados.

## Testes

- 29 testes Python aprovados, incluindo o leitor do dump (escapes SQL, nulos, recusa de chamadas de função e de arquivo parcial), índices, sinônimos, paginação, vínculo com documentos e ausência de inferência clínica.
- Build de produção Vite aprovado.
- `foodrugs.e2e.mjs` aprovado no Chrome: base completa ativa, cadastro, busca por sinônimo em português (sinvastatina + toranja), evidências com contexto original e paginação, base de conhecimento, tabelas científicas, relações moleculares, histórico e layout mobile, sem erros JavaScript.
- Link HTTPS temporário (Cloudflare Quick Tunnel) respondendo com a base completa ativa.

## Pares conferidos

| Consulta em português | Termos encontrados | Registros |
|---|---|---:|
| sinvastatina + toranja | Simvastatin + Grapefruit | 4 |
| varfarina + vitamina K | Warfarin + Vitamin K | 9 |
| ciprofloxacino + leite | Ciprofloxacin + MILK | 4 |
| levotiroxina + café | Levothyroxine + Coffee | 3 |
| metformina + álcool | Metformin + Alcohol | 3 |

Busca molecular "resveratrol": 723.105 resultados, com estudo de origem.

## Desempenho (camada de dados, 5 repetições)

| Operação | Mediana | Máximo |
|---|---:|---:|
| Busca de termo (medicamento ou alimento) | 1,5–2,9 ms | 6,2 ms |
| Evidências de um par | 3,6–7,0 ms | 16,0 ms |
| Base de conhecimento ("warfarin") | 82 ms | 799 ms (cache frio) |
| Relações moleculares ("resveratrol") | 124 ms | 208 ms |
| Tabela `cmap_foodrugs`, offset 20 milhões | 795 ms | 1.863 ms |

Todas abaixo da meta de 3 s do TCC. Os tempos não incluem rede nem renderização.

## Não verificado

Validação clínica das associações, teste de carga com usuários simultâneos, PostgreSQL/Docker com a base completa, implantação permanente e entrega SMTP a destinatários reais. Os testes `e2e.mjs` e `library.e2e.mjs` foram escritos para o catálogo complementar e não foram executados com a FooDrugs ativa. Há avisos de depreciação nas dependências de teste, sem falhas.
