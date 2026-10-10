# Drug-Food Checker

Sistema web em português baseado no TCC de Cauê Gaspar Macrini e João Pedro Alves Domingos (UDF). React + Vite, FastAPI + SQLAlchemy + RapidFuzz, grafo Cytoscape.js, PostgreSQL por Docker e SQLite para desenvolvimento local.

**Base de dados:** o sistema usa a **FooDrugs 4.0.0 completa** (IMDEA Food Institute, CC BY 4.0), importada integralmente do arquivo oficial: 10 tabelas e **30.797.702 registros**, incluindo **1.108.429 registros de mineração de texto**, **439.338 documentos** e **26.365.254 resultados moleculares**. Detalhes em [FOODRUGS-COMPLETA.md](FOODRUGS-COMPLETA.md).

**Apresentação:** consulte [APRESENTACAO.md](APRESENTACAO.md) para iniciar localmente, gerar o link temporário e seguir o roteiro. A última verificação está em [VERIFICACAO-2026-10-10.md](VERIFICACAO-2026-10-10.md).

## Executar no Windows

Requer Python 3.12+, Node.js 22+ e, para a base completa, pelo menos 10 GB livres. Na pasta deste projeto:

```powershell
./setup.ps1
./Instalar-FooDrugs.ps1
./start.ps1
```

`Instalar-FooDrugs.ps1` baixa o arquivo oficial (1,56 GB), confere o checksum MD5, importa as dez tabelas, constrói os índices e ativa a versão `foodrugs-4.0.0-completa`. É executado uma vez por computador e pode levar de vários minutos a mais de uma hora, conforme a conexão. Sem essa etapa, o sistema funciona com o catálogo complementar de 25 medicamentos descrito abaixo.

Se necessário, informe o executável: `./setup.ps1 -Python 'C:/caminho/python.exe'`.
Abra **http://127.0.0.1:8000**, clique em **Criar conta gratuita** e cadastre sua conta. Não há conta nem senha padrão. Contas e histórico são persistidos em `backend/drugfood.db`; a FooDrugs fica em `.local-data/foodrugs-v4.sqlite`. Mantenha o terminal de execução aberto; Ctrl+C encerra o servidor.

Administrador:

```powershell
cd backend
../.venv/Scripts/python.exe manage.py create-admin
```

A conta administrativa é criada de forma interativa, com senha própria e aceite. Ao entrar nela, aparece a opção Administração. Contas comuns não acessam as rotas administrativas.

## PostgreSQL e Docker

O projeto inclui a configuração; o Docker Engine precisa estar iniciado.

1. Copie `.env.example` para `.env`.
2. Preencha `POSTGRES_PASSWORD` e `JWT_SECRET` com valores aleatórios diferentes de pelo menos 32 caracteres. Para a senha do banco, use hexadecimal, evitando necessidade de escape na URL.
3. Execute `docker compose --profile dev up --build`.
4. Acesse http://127.0.0.1:8000. A caixa de e-mails de desenvolvimento fica em http://127.0.0.1:8025.
5. Crie um administrador com `docker compose exec app python manage.py create-admin`.

O banco não publica porta externa. Os dados permanecem no volume `postgres_data`. Não remova esse volume se desejar manter as contas.

A FooDrugs completa não é copiada para a imagem Docker (`.local-data` está no `.dockerignore`). Para usá-la no container, monte o arquivo `foodrugs-v4.sqlite` como volume somente leitura e aponte `FOODRUGS_DB` para ele.

Para ambiente público, configure `APP_ENV=production`, `DOMAIN` com domínio sob seu controle, `APP_ORIGIN=https://seu-dominio` e SMTP real. Use `docker compose --profile production up --build -d`. O Caddy fornece HTTPS, e os cookies tornam-se Secure. A configuração de produção exige segredo e origem HTTPS; não configure o perfil de e-mail de teste para envio real. A implantação pública, DNS, certificados reais e operação com dados de saúde não foram realizados nesta entrega.

## Funcionalidades

- Cadastro, consentimento versionado, login, logout e recuperação de senha.
- Perfil opcional com idade, peso, altura, IMC, condições, doença renal/hepática, medicamentos, suplementos e álcool.
- Autocompletar sobre os 161.495 termos de medicamentos e 50.796 termos alimentares da FooDrugs, com sinônimos em português (ex.: sinvastatina → Simvastatin, toranja → Grapefruit, leite → MILK). A consulta exige selecionar o termo, evitando substituição silenciosa de medicamentos.
- Consulta por par sobre todos os registros textuais da FooDrugs: evidências paginadas, trecho original da fonte, identificadores de registro e documento, link para a referência e versão da base.
- Base de conhecimento com busca por medicamento/alimento/sinônimo, alimentos associados paginados e abertura direta da consulta.
- Tela **Dados FooDrugs**: contagem e integridade por tabela, explorador das 10 tabelas originais e busca de relações moleculares (escore tau) com o estudo de origem.
- Grafo interativo com medicamento, alimento, composto, mecanismo e fonte; seleção também disponível por botões.
- Histórico individual, filtros por risco/período e reabertura do resultado original.
- Visualização/exportação JSON e exclusão com confirmação e senha.
- Administração: importar uma versão JSON, consultar e ativar versões, auditoria e ativar/desativar/excluir contas comuns.

## Bases e interpretação dos resultados

### FooDrugs 4.0.0 completa (base ativa)

Importação integral de `FinalFooDrugs_v4.sql` (1.561.331.208 bytes, MD5 `3c8f26240dd571ded1e4b100d1dfc9d2`), sem amostragem e sem executar o SQL baixado:

| Tabela | Registros | Conteúdo |
|---|---:|---|
| `TM_interactions` | 1.108.429 | Associações medicamento–alimento extraídas de textos |
| `texts` | 439.338 | Documentos e trechos de origem |
| `cmap_foodrugs` | 26.365.254 | Resultados moleculares (escore tau) |
| `topTable` | 2.799.422 | Expressão gênica diferencial |
| `cmap` | 70.895 | Compostos, genes e linhagens celulares |
| `misc_sample` | 6.846 | Atributos das amostras |
| `sample` | 4.559 | Amostras experimentais |
| `nodes` | 2.617 | Nós dos estudos |
| `misc_study` | 192 | Atributos dos estudos |
| `study` | 150 | Estudos de expressão gênica |

Os registros textuais formam 632.092 pares medicamento–alimento distintos. Todos os registros textuais têm documento correspondente e são pesquisáveis. A contagem de termos não equivale ao número de medicamentos comercializados: nomes podem representar classes, compostos ou erros de extração.

Associações textuais são candidatas produzidas pela mineração de texto original da FooDrugs. O sistema não executa MLP e não transforma escore tau, coocorrência ou contexto textual em risco clínico; por isso os resultados aparecem como **Não classificado**. Usar a base completa não significa ter uma base clinicamente validada nem cobertura de todas as interações existentes.

Fonte e atribuição: Piette Gómez, Lacruz Pleguezuelos e colaboradores, IMDEA Food Institute, [FooDrugs 4.0.0 no Zenodo](https://doi.org/10.5281/zenodo.8192515), licença CC BY 4.0. [Artigo original](https://doi.org/10.1093/database/baad075). As tabelas originais são preservadas; as modificações consistem em índices de busca e sinônimos em português.

### Catálogo complementar

Sem executar a instalação FooDrugs, o banco novo usa um catálogo demonstrativo de **25 medicamentos, 19 alimentos/bebidas e 49 associações**, em `data/catalogo-oficial.json`. São sínteses em português de **23 referências da FDA e do MedlinePlus/ASHP**, consultadas em 08/10/2026. Cada registro informa fonte, orientação de consumo e data de consulta. As orientações não foram validadas por revisão clínica independente e não recebem automaticamente uma gravidade numérica. Consulte [CATALOGO.md](CATALOGO.md) para escopo e procedência. Com a FooDrugs instalada, o catálogo continua disponível como versão inativa na Administração.

O arquivo `data/starter.json` preserva a amostra FDA anterior (cinco associações). `data/foodrugs-example.json` contém 100 registros reais da `TM_interactions`, usados nos testes do conversor de recortes. Bancos já existentes não são sobrescritos na inicialização. O histórico mantém as evidências da data de cada consulta.

### Conversor de recortes (não é a instalação integral)

`backend/foodrugs_import.py` converte uma parte do dump em JSON importável pela Administração (até 10 mil registros / 8 MB por versão). Serve apenas para recortes e testes:

```powershell
cd backend
../.venv/Scripts/python.exe foodrugs_import.py C:/dados/FinalFooDrugs_v4.sql --output ../data/minha-base.json --limit 5000 --version foodrugs-4-recorte-5000
```

Ativar um JSON pela Administração troca a versão ativa. Para voltar à base completa, use **Ativar versão** em `foodrugs-4.0.0-completa`.

### Classificação revisada

O contrato JSON está em `data/starter.json` e na documentação da API `/docs`. Para habilitar um risco, o registro precisa de `base_risk` (0, 1 ou 2), `reviewed: true` e `risk_basis` não vazio. Esse campo é uma declaração do administrador; o software não verifica a qualificação clínica do revisor. Não marque registros como revisados sem uma revisão efetiva. Sem esses campos o risco fica nulo. Nunca se converte automaticamente um escore molecular em risco clínico.

Os quatro modificadores da página 31 do TCC estão em `backend/services.py`, limitados a 0–2. Eles são uma heurística acadêmica, não um modelo validado. Como a FooDrugs não fornece risco base, nenhum modificador é aplicado aos resultados dela. Ausência de registro é mostrada em estado neutro e não em verde, para não sugerir segurança indevida. Peso, IMC, doenças livres e suplementos são armazenados, mas não geram modificadores além daqueles definidos no TCC.

## Segurança e privacidade implementadas

BCrypt custo 12, JWT de 8 horas em cookie HttpOnly/SameSite Strict, revogação de sessões no logout, mudança de senha e desativação. Tokens de recuperação expiram em 30 minutos, são armazenados com hash e consumidos uma vez. O cliente usa JSON e a API valida origem para reduzir CSRF. Limitação de taxa local por IP: 20 solicitações/minuto para autenticação e 120/minuto para as demais rotas.

Histórico vinculado por UUID mensal, com mapa de propriedade separado. Logs usam HMAC do identificador, sem conteúdo clínico. Exclusão remove a conta e seus dados associados no banco ativo. A FooDrugs é aberta somente para leitura e não contém dados de usuários. SQLite de desenvolvimento e arquivos de e-mail não são criptografados; backup, retenção, governança, criptografia em repouso e revisão jurídica/clínica devem ser definidos para operação real. Não se declara conformidade integral com a LGPD apenas por implementar essas funções.

Sem SMTP, em desenvolvimento, a recuperação grava o link em `backend/outbox/`, sem expô-lo na API. Em produção, configure SMTP; falhas de entrega geram evento técnico genérico no servidor. Nunca distribua `.env`, `.local-secret`, bancos locais ou `outbox`.

## Desenvolvimento e testes

Frontend com atualização automática: `cd frontend; npm run dev`. Nesse caso inicie a API com `APP_ORIGIN=http://127.0.0.1:5173` e porta 8000. A proxy do Vite encaminha `/api`.

```powershell
cd backend
../.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider
cd ../frontend
npm run build
node foodrugs.e2e.mjs
node e2e.mjs
node library.e2e.mjs
```

Os E2E precisam da aplicação na porta 8000 e do Google Chrome. `foodrugs.e2e.mjs` exige a FooDrugs completa ativa; `e2e.mjs` e `library.e2e.mjs` foram escritos para o catálogo complementar. Os testes criam apenas contas de teste próprias. O backend usa banco temporário isolado nos testes. Capturas: `preview-foodrugs-evidencia.png`, `preview-foodrugs-completa.png` e `preview-foodrugs-mobile.png`. Se o build falhar por restrição de leitura de diretórios em ambientes Windows isolados, use `npm run build -- --configLoader runner`.

Validação em 10/10/2026 (detalhes em [VERIFICACAO-2026-10-10.md](VERIFICACAO-2026-10-10.md)): 29 testes Python aprovados; build de produção; E2E da FooDrugs completa no Chrome (desktop e mobile) sem erros JavaScript; link HTTPS temporário respondendo com a base completa. Tempo das consultas na camada de dados, com a base completa: busca de termos de 2 a 5 ms, evidências de um par de 4 a 16 ms, busca molecular por termo cerca de 0,2 s. Todas abaixo da meta de 3 s do TCC. Não foi feito teste de carga com usuários simultâneos nem teste em PostgreSQL/Docker.

## Organização

- `backend/main.py`: API e segurança; `models.py`: persistência; `schemas.py`: contratos e validação; `services.py`: busca, consulta e regras do catálogo.
- `backend/download_foodrugs.py`: download retomável com verificação MD5; `foodrugs_full.py`: leitor do dump sem executar SQL; `index_foodrugs.py`: índices e sinônimos; `install_foodrugs.py`: instalação e ativação; `foodrugs_store.py`: consultas somente leitura à base completa; `foodrugs_import.py`: conversor de recortes.
- `frontend/src/`: interface (`main.jsx`, `Library.jsx`, `Foodrugs.jsx` para a tela Dados FooDrugs, `Molecular.jsx` para relações moleculares).
- `data/`: catálogo, exemplos e `foodrugs-full-manifest.json` (contagens e checksum da importação). `.local-data/`: dump e banco FooDrugs (fora do Git).

A modelagem mantém as entidades principais, usando JSON para listas clínicas e metadados de evidência; não reproduz literalmente todos os esquemas e tabelas do DER do TCC.

Veja `REQUISITOS.md` para a correspondência entre os requisitos do documento e a implementação.
