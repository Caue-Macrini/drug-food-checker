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
2. Em Consultar interação, mostre a faixa de cobertura (161.495 termos de medicamentos, 50.796 termos alimentares, 1.108.429 registros textuais). Digite **sinvastatina**: as sugestões de alimentos aparecem com um ponto colorido pelo nível de risco. Escolha **toranja** e consulte.
3. **Vermelho — Risco elevado:** o resultado mostra o círculo vermelho e "Evite consumir Grapefruit durante o uso de Simvastatin sem orientação profissional". Em "Como a interação acontece", explique o aumento da concentração no sangue; em "Por que esta classificação", mostre que uma monografia do Drugs.com incluída na FooDrugs classifica a interação como *Major · GENERALLY AVOID*.
4. **Amarelo — Atenção:** consulte **cafeína + teofilina** (81 registros). Mostre "8 de 81 trechos (7 documentos) descrevem interação" e o mecanismo (enzimas do citocromo P450). Em Evidências, mostre que os trechos que indicam interação aparecem primeiro e que os demais estão marcados como "Apenas menciona os dois". Foi exatamente essa dúvida ("é bom tomar ou não?") que motivou a classificação por cores. Outros amarelos: **varfarina + vitamina K**, **ciprofloxacino + leite**, **levotiroxina + café**.
5. **Verde:** consulte **omeprazol + leite**. Os registros citam os dois, mas nenhum descreve interação, e a tela diz isso com a ressalva de segurança. Consulte também **levotiroxina + soja**, que não tem registro na base: verde "Sem interação conhecida", com a ressalva do fluxo alternativo do TCC.
6. **Perfil clínico (Tabela 2):** em Meu perfil clínico, informe idade 70 e três medicamentos em uso; salve (mostre o IMC). Volte, ative "Considerar meu perfil clínico" e consulte **varfarina + vitamina K**: o amarelo passa a vermelho, com o modificador "Idade ≥ 65 anos e uso de pelo menos 3 medicamentos (+1)". Explique que os modificadores intensificam uma interação identificada; não criam uma.
7. Abra **Dados FooDrugs**: mostre os 30.797.702 registros preservados, o checksum oficial e a contagem das 10 tabelas. Em Relações moleculares, pesquise **resveratrol** e mostre o estudo de origem. O escore tau não é risco para pacientes.
8. Reabra a consulta pelo histórico e demonstre o filtro por nível de risco. Em Dados e privacidade, visualize e exporte o JSON.
9. Saia. Solicite recuperação da conta fictícia. Abra http://127.0.0.1:8025, selecione a mensagem e use o link. Redefina a senha e entre novamente. A mensagem é entregue apenas à caixa local de teste, não a Gmail/Outlook.
10. Entre como administrador. Mostre versões (FooDrugs completa ativa; catálogo e amostra FDA inativos), auditoria e contas.
11. Opcional, para demonstrar os modificadores com dados fictícios controlados: importe `data/demo-sintetico.json`, informe que são dados fictícios e consulte os medicamentos com prefixo DEMONSTRAÇÃO. O perfil hepático aciona uma regra nesse cenário. **Ao terminar, na Administração, use Ativar versão em `foodrugs-4.0.0-completa`** para voltar à base completa.

Para testar exclusão, crie uma conta descartável; não exclua as contas preparadas de apresentação.

## Verificações realizadas

Em 11/10/2026: 66 testes Python aprovados (37 das regras de risco); build de produção; E2E da FooDrugs completa no Chrome (indicador de risco, resposta, motivos, evidências marcadas, paginação, base de conhecimento, tabelas científicas, histórico e mobile) sem erros JavaScript; link HTTPS respondendo. Desempenho das regras: 80% de concordância com o Drugs.com e, em avaliação cega de 60 pares realistas, 86,7% de precisão e 70,3% de sensibilidade. Detalhes em [VERIFICACAO-2026-10-11.md](VERIFICACAO-2026-10-11.md) e [CLASSIFICACAO-RISCO.md](CLASSIFICACAO-RISCO.md). Verificações anteriores: [10/10](VERIFICACAO-2026-10-10.md) (base completa e desempenho) e [08/10](VERIFICACAO-2026-10-08.md) (recuperação por SMTP local, exclusão, cookies Secure/HttpOnly).

## O que o sistema faz e seus limites

A base ativa `foodrugs-4.0.0-completa` é a FooDrugs 4.0.0 inteira: 1.108.429 registros textuais (632.092 pares), 439.338 documentos, 26.365.254 resultados moleculares e 10 tabelas, importados do arquivo oficial com checksum conferido. A busca consulta registros existentes; não prevê combinações ausentes. Ausência de registro não comprova segurança.

A FooDrugs não informa gravidade. A cor de cada resultado é derivada por **regras explícitas** que leem os trechos de origem (gravidade declarada nas monografias do Drugs.com, alterações farmacocinéticas ou de efeito, recomendações de uso, estudos sem efeito). Não há modelo treinado; cada cor mostra o motivo. As regras e o desempenho medido estão em [CLASSIFICACAO-RISCO.md](CLASSIFICACAO-RISCO.md). As associações vêm de mineração automática de texto e podem conter erros de extração. A classificação e as regras de perfil são heurísticas acadêmicas, sem validação clínica.

**Se perguntarem "por que não usaram aprendizado de máquina?":** o próprio TCC (p. 31) justifica regras explícitas por rastreabilidade e pela falta de conjunto rotulado público. O sistema mede as regras contra o Drugs.com, contra o catálogo FDA/MedlinePlus e contra avaliação cega de trechos e pares.

O catálogo `fontes-oficiais-2026-10-08` (25 medicamentos, sínteses da FDA e MedlinePlus/ASHP) continua disponível como versão inativa.

O e-mail funciona na caixa local de demonstração; entrega a Gmail/Outlook exige configuração de SMTP real. O link público é temporário e depende do computador ligado e conectado. Não houve implantação permanente nem teste de carga com usuários simultâneos.

## Manutenção

O build do Vite é servido pelo FastAPI. Node é usado na compilação; Vite não mantém o computador online. Para recompilar: `cd frontend` e `npm run build`. Testes: `cd backend` e `../.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider`. Com a aplicação iniciada: `cd frontend` e `node foodrugs.e2e.mjs`.

As ferramentas locais Mailpit 1.31.4 e cloudflared 2026.10.0 ficam em `.local-tools/`. Senhas, bancos, backups, logs e a FooDrugs não entram no pacote de código. Para trocar de computador, use `setup.ps1` e depois `Instalar-FooDrugs.ps1`; os atalhos e as ferramentas locais precisam ser preparados naquele computador.
