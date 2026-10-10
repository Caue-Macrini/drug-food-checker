# Apresentação — sábado, 10 de outubro de 2026

## Abrir no seu computador

Dê dois cliques no atalho **Drug-Food Checker - Apresentar**, na área de trabalho, ou em `INICIAR-APRESENTACAO.cmd` na pasta do projeto.

- Sistema: http://127.0.0.1:8000
- Caixa de e-mails da demonstração: http://127.0.0.1:8025
- Contas de administrador e visitante: `.local-run/ACESSOS-APRESENTACAO.txt` (arquivo privado local).

Os serviços rodam em segundo plano; fechar a janela não os encerra. Reabrir o atalho reutiliza os serviços. Contas e histórico ficam em `backend/drugfood.db`; a FooDrugs completa fica em `.local-data/foodrugs-v4.sqlite` (2,7 GB). Há backups do banco de contas em `backups/`, incluindo um feito antes da ativação da FooDrugs. Não mova a pasta do projeto antes da apresentação: o ambiente Python instalado depende de sua localização.

A base ativa é `foodrugs-4.0.0-completa`. Para conferir antes de apresentar, abra http://127.0.0.1:8000/api/health: deve mostrar `"associations":1108429` e `"molecular_records":26365254`.

## Abrir na internet durante a apresentação

Dê dois cliques em **Drug-Food Checker - Link publico**, na área de trabalho, ou em `ABRIR-LINK-PUBLICO.cmd`. O endereço HTTPS aparecerá na janela e será salvo em `.local-run/LINK-PUBLICO.txt`.

O link usa Cloudflare Quick Tunnel: não exige conta ou domínio, **muda quando o túnel é recriado** e depende deste computador ligado e conectado. Não é hospedagem 24 horas. Confira o endereço atual em `.local-run/LINK-PUBLICO.txt` antes de compartilhar. Compartilhe apenas o link, não o arquivo de senhas. O hPanel e o plano Hostinger não foram alterados. Use dados fictícios na apresentação. A caixa de e-mail local não é publicada.

Se a rede da faculdade bloquear o túnel ou a internet cair, apresente em http://127.0.0.1:8000. A FooDrugs completa está no computador, então a consulta, as evidências, a tela Dados FooDrugs, o perfil, o histórico e a caixa de e-mails funcionam sem internet. Só abrir os documentos e estudos nos sites de origem exige internet.

Para encerrar: execute `Parar-Apresentacao.ps1` com PowerShell. Para encerrar apenas o link público: `./Parar-Apresentacao.ps1 -PublicOnly`.

## Roteiro sugerido (8–10 minutos)

1. Entre como visitante ou crie uma conta fictícia. Mostre o consentimento.
2. Em Consultar interação, mostre a faixa de cobertura (161.495 termos de medicamentos, 50.796 termos alimentares, 1.108.429 registros textuais). Digite **sinvastatina** e **toranja** em português e consulte: o sistema encontra Simvastatin + Grapefruit (4 registros). Antes de consultar, mostre as sugestões de alimentos associados ao medicamento.
3. Abra Evidências: mostre o trecho original da fonte ("Major Food Interaction… grapefruit juice may significantly increase the plasma concentrations of lovastatin and simvastatin"), o número do registro e do documento e o link da referência. Explique por que aparece **Não classificado**: a FooDrugs extrai associações de textos, mas não fornece gravidade clínica, e o sistema não inventa uma. Abra o Grafo; ele não infere causalidade.
4. Outros pares que funcionam bem: **varfarina + vitamina K** (9 registros), **ciprofloxacino + leite** (4), **levotiroxina + café** (3), **metformina + álcool** (3).
5. Abra **Dados FooDrugs**: mostre os 30.797.702 registros preservados, o checksum oficial e a contagem das 10 tabelas. Em Relações moleculares, pesquise **resveratrol** e mostre o estudo de origem (GEO). O escore tau não é risco para pacientes.
6. Abra Base de conhecimento e busque um medicamento por sinônimo em português.
7. Preencha idade, peso e altura no perfil; salve e confira persistência e IMC. Dados clínicos são opcionais. Com a FooDrugs, os modificadores do perfil não alteram o resultado, porque não há risco base a ajustar.
8. Reabra a consulta pelo histórico; demonstre os filtros. Em Dados e privacidade, visualize e exporte o JSON.
9. Saia. Solicite recuperação da conta fictícia. Abra http://127.0.0.1:8025, selecione a mensagem e use o link. Redefina a senha e entre novamente. A mensagem é entregue apenas à caixa local de teste, não a Gmail/Outlook.
10. Entre como administrador. Mostre versões (FooDrugs completa ativa; catálogo e amostra FDA inativos), auditoria e contas.
11. Opcional, para demonstrar cores e regras do TCC: importe `data/demo-sintetico.json`, informe que são dados fictícios e consulte os medicamentos com prefixo DEMONSTRAÇÃO. O perfil hepático aciona uma regra nesse cenário. **Ao terminar, na Administração, use Ativar versão em `foodrugs-4.0.0-completa`** para voltar à base completa.

Para testar exclusão, crie uma conta descartável; não exclua as contas preparadas de apresentação.

## Verificações realizadas

Em 10/10/2026: 29 testes Python aprovados; compilação de produção aprovada; E2E da FooDrugs completa no Chrome aprovado (busca com sinônimo em português, evidências com contexto original e paginação, base de conhecimento, tabelas científicas, relações moleculares, histórico e mobile), sem erros JavaScript. O link HTTPS respondeu com a base completa ativa. Consultas de par levam milissegundos. Detalhes em [VERIFICACAO-2026-10-10.md](VERIFICACAO-2026-10-10.md). A verificação de 08/10 (recuperação por SMTP local, exclusão, cookies Secure/HttpOnly) está em [VERIFICACAO-2026-10-08.md](VERIFICACAO-2026-10-08.md).

## O que o sistema faz e seus limites

A base ativa `foodrugs-4.0.0-completa` é a FooDrugs 4.0.0 inteira: 1.108.429 registros textuais (632.092 pares), 439.338 documentos, 26.365.254 resultados moleculares e 10 tabelas, importados do arquivo oficial com checksum conferido. A busca consulta registros existentes; não usa MLP nem prevê combinações ausentes. Ausência de registro não comprova segurança.

As associações da FooDrugs vêm de mineração automática de texto e podem conter erros de extração. Não são classificações clínicas validadas, por isso os resultados não recebem cor de risco. A classificação numérica só existe se uma versão importada declarar fundamento e revisão. As regras de perfil são acadêmicas, não validadas clinicamente.

O catálogo `fontes-oficiais-2026-10-08` (25 medicamentos, sínteses da FDA e MedlinePlus/ASHP) continua disponível como versão inativa.

O e-mail funciona na caixa local de demonstração; entrega a Gmail/Outlook exige configuração de SMTP real. O link público é temporário e depende do computador ligado e conectado. Não houve implantação permanente nem teste de carga com usuários simultâneos.

## Manutenção

O build do Vite é servido pelo FastAPI. Node é usado na compilação; Vite não mantém o computador online. Para recompilar: `cd frontend` e `npm run build`. Testes: `cd backend` e `../.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider`. Com a aplicação iniciada: `cd frontend` e `node foodrugs.e2e.mjs`.

As ferramentas locais Mailpit 1.31.4 e cloudflared 2026.10.0 ficam em `.local-tools/`. Senhas, bancos, backups, logs e a FooDrugs não entram no pacote de código. Para trocar de computador, use `setup.ps1` e depois `Instalar-FooDrugs.ps1`; os atalhos e as ferramentas locais precisam ser preparados naquele computador.
