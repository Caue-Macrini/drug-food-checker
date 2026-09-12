# Drug-Food Checker

Sistema web em português baseado no TCC de Cauê Gaspar Macrini e João Pedro Alves Domingos (UDF). React + Vite, FastAPI + SQLAlchemy + RapidFuzz, grafo Cytoscape.js, PostgreSQL por Docker e SQLite para desenvolvimento local.

## Executar no Windows

Requer Python 3.12+ e Node.js 22+. Na pasta deste projeto:

```powershell
./setup.ps1
./start.ps1
```

Se necessário, informe o executável: `./setup.ps1 -Python 'C:/caminho/python.exe'`.
Abra **http://127.0.0.1:8000**, clique em **Criar conta gratuita** e cadastre sua conta. Não há conta nem senha padrão. As alterações são persistidas em `backend/drugfood.db`. Mantenha o terminal de execução aberto; Ctrl+C encerra o servidor.

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

Para ambiente público, configure `APP_ENV=production`, `DOMAIN` com domínio sob seu controle, `APP_ORIGIN=https://seu-dominio` e SMTP real. Use `docker compose --profile production up --build -d`. O Caddy fornece HTTPS, e os cookies tornam-se Secure. A configuração de produção exige segredo e origem HTTPS; não configure o perfil de e-mail de teste para envio real. A implantação pública, DNS, certificados reais e operação com dados de saúde não foram realizados nesta entrega.

## Funcionalidades

- Cadastro, consentimento versionado, login, logout e recuperação de senha.
- Perfil opcional com idade, peso, altura, IMC, condições, doença renal/hepática, medicamentos, suplementos e álcool.
- Autocompletar por nomes e aliases com tolerância a acentos e erros de digitação; a consulta exige selecionar o termo, evitando substituição silenciosa de medicamentos.
- Consulta por par, fontes, mecanismo, explicação, risco base e ajustado e razões dos modificadores.
- Grafo interativo com medicamento, alimento, composto, mecanismo e fonte; seleção também disponível por botões.
- Histórico individual, filtros por risco/período e reabertura do resultado original.
- Visualização/exportação JSON e exclusão com confirmação e senha.
- Administração: importar uma versão JSON, consultar versões, auditoria e ativar/desativar/excluir contas comuns.

## Bases e interpretação dos resultados

A instalação começa com **cinco associações** em `data/starter.json`, baseadas na página pública da FDA: [Grapefruit Juice and Some Drugs Don't Mix](https://www.fda.gov/consumers/consumer-updates/grapefruit-juice-and-some-drugs-dont-mix). É uma amostra identificada, não a base FooDrugs completa. A fonte descreve associações e não fornece a escala 0/1/2 do TCC; por isso o risco inicial fica **não classificado**.

`data/foodrugs-example.json` contém **100 registros reais** da tabela `TM_interactions`, extraídos de um fragmento do dump oficial FooDrugs 4.0.0. Mantém os identificadores de interação e texto e os termos originais, em inglês. São associações potenciais de mineração de texto, que podem conter erros; a fonte vinculada é o depósito da base, não uma alegação de validação de cada associação. O recorte não inclui os documentos da tabela `texts` nem inferências transcriptômicas. A ativação desse arquivo pela administração substitui a amostra FDA como versão ativa.

Fonte e atribuição: Piette Gómez, Lacruz Pleguezuelos e colaboradores, IMDEA Food Institute, [FooDrugs 4.0.0 no Zenodo](https://doi.org/10.5281/zenodo.8192515), licença CC BY 4.0. As modificações consistem em recorte e normalização para JSON, sem inferência de gravidade. [Artigo original](https://doi.org/10.1093/database/baad075).

### Converter o dump FooDrugs

Baixe `FinalFooDrugs_v4.sql` do depósito oficial (aproximadamente 1,56 GB). O conversor lê o arquivo como dados; não executa comandos SQL:

```powershell
cd backend
../.venv/Scripts/python.exe foodrugs_import.py C:/dados/FinalFooDrugs_v4.sql --output ../data/minha-base.json --limit 5000 --version foodrugs-4-recorte-5000
```

Importe o JSON na Administração. O conversor foi testado no formato real do cabeçalho do dump V4 e em testes de escape; a conversão do arquivo inteiro não foi executada. A interface aceita até 10 mil registros / 8 MB por versão, com transação atômica. A importação integral em grande escala e a resolução dos textos originais são extensões necessárias para uso da base completa.

### Classificação revisada

O contrato JSON está em `data/starter.json` e na documentação da API `/docs`. Para habilitar um risco, o registro precisa de `base_risk` (0, 1 ou 2), `reviewed: true` e `risk_basis` não vazio. Esse campo é uma declaração do administrador; o software não verifica a qualificação clínica do revisor. Não marque registros como revisados sem uma revisão efetiva. Sem esses campos o risco fica nulo. Nunca se converte automaticamente um escore molecular em risco clínico.

Os quatro modificadores da página 31 do TCC estão em `backend/services.py`, limitados a 0–2. Eles são uma heurística acadêmica, não um modelo validado. Ausência de registro é mostrada em estado neutro e não em verde, para não sugerir segurança indevida. Peso, IMC, doenças livres e suplementos são armazenados, mas não geram modificadores além daqueles definidos no TCC.

## Segurança e privacidade implementadas

BCrypt custo 12, JWT de 8 horas em cookie HttpOnly/SameSite Strict, revogação de sessões no logout, mudança de senha e desativação. Tokens de recuperação expiram em 30 minutos, são armazenados com hash e consumidos uma vez. O cliente usa JSON e a API valida origem para reduzir CSRF. Limitação de taxa local por IP: 20 solicitações/minuto para autenticação e 120/minuto para as demais rotas.

Histórico vinculado por UUID mensal, com mapa de propriedade separado. Logs usam HMAC do identificador, sem conteúdo clínico. Exclusão remove a conta e seus dados associados no banco ativo. SQLite de desenvolvimento e arquivos de e-mail não são criptografados; backup, retenção, governança, criptografia em repouso e revisão jurídica/clínica devem ser definidos para operação real. Não se declara conformidade integral com a LGPD apenas por implementar essas funções.

Sem SMTP, em desenvolvimento, a recuperação grava o link em `backend/outbox/`, sem expô-lo na API. Em produção, configure SMTP; falhas de entrega geram evento técnico genérico no servidor. Nunca distribua `.env`, `.local-secret`, bancos locais ou `outbox`.

## Desenvolvimento e testes

Frontend com atualização automática: `cd frontend; npm run dev`. Nesse caso inicie a API com `APP_ORIGIN=http://127.0.0.1:5173` e porta 8000. A proxy do Vite encaminha `/api`.

```powershell
cd backend
../.venv/Scripts/python.exe -m pytest -q
cd ../frontend
npm run build -- --configLoader runner
node e2e.mjs
```

O E2E precisa da aplicação na porta 8000 e Google Chrome. Cria e exclui apenas sua própria conta de teste. Capturas: `preview-desktop.png` e `preview-mobile.png`. O backend usa banco temporário isolado nos testes. O parâmetro `--configLoader runner` contorna restrições de leitura dos diretórios ancestrais em ambientes Windows isolados.

Validação realizada: testes automatizados da API, regras e conversor; compilação de produção; fluxo real no Chrome em desktop e largura de 390 px, sem erros JavaScript. PostgreSQL/Docker e HTTPS público não foram executados, pois o serviço Docker estava desligado. Metas de carga, milhões de registros e latência <3 s do TCC ainda exigem benchmark específico.

## Organização

`backend/main.py`: API e segurança; `models.py`: persistência; `schemas.py`: contratos e validação; `services.py`: busca, consulta e regras; `foodrugs_import.py`: conversor; `frontend/src/`: interface; `data/`: dados e exemplos. A modelagem mantém as entidades principais, usando JSON para listas clínicas e metadados de evidência; não reproduz literalmente todos os esquemas e tabelas do DER do TCC.

Veja `REQUISITOS.md` para a correspondência entre os requisitos do documento e a implementação.
