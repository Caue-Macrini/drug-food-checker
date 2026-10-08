# Apresentação — sábado, 10 de outubro de 2026

## Abrir no seu computador

Dê dois cliques no atalho **Drug-Food Checker - Apresentar**, na área de trabalho, ou em `INICIAR-APRESENTACAO.cmd` na pasta do projeto.

- Sistema: http://127.0.0.1:8000
- Caixa de e-mails da demonstração: http://127.0.0.1:8025
- Contas de administrador e visitante: `.local-run/ACESSOS-APRESENTACAO.txt` (arquivo privado local).

Os serviços rodam em segundo plano; fechar a janela não os encerra. Reabrir o atalho reutiliza os serviços. O banco é persistente em `backend/drugfood.db`. Foi criado um backup em `backups/` antes da preparação das contas. Não mova a pasta do projeto antes da apresentação: o ambiente Python instalado depende de sua localização.

## Abrir na internet durante a apresentação

Dê dois cliques em **Drug-Food Checker - Link publico**, na área de trabalho, ou em `ABRIR-LINK-PUBLICO.cmd`. O endereço HTTPS aparecerá na janela e será salvo em `.local-run/LINK-PUBLICO.txt`.

O link usa Cloudflare Quick Tunnel: não exige conta ou domínio, muda quando o túnel é recriado e depende deste computador ligado e conectado. Não é hospedagem 24 horas. Compartilhe apenas o link, não o arquivo de senhas. O hPanel e o plano Hostinger não foram alterados. Use dados fictícios na apresentação. A caixa de e-mail local não é publicada.

Se a rede da faculdade bloquear o túnel ou a internet cair, apresente em http://127.0.0.1:8000. As fontes externas exigem internet, mas a consulta, o perfil, o histórico, os gráficos locais e a caixa de e-mails funcionam localmente.

Para encerrar: execute `Parar-Apresentacao.ps1` com PowerShell. Para encerrar apenas o link público: `./Parar-Apresentacao.ps1 -PublicOnly`.

## Roteiro sugerido (8–10 minutos)

1. Entre como visitante ou crie uma conta fictícia. Mostre o consentimento.
2. Abra Base de conhecimento: mostre os 25 medicamentos, a busca por alimento e as fontes. Busque leite e consulte Ciprofloxacino + Leite; mostre a ressalva sobre refeições. Volte a Consultar interação e selecione Levotiroxina para exibir os alimentos cadastrados.
3. Abra Evidências e Grafo. Mostre fonte, versão e os elementos do registro. O grafo não infere causalidade.
4. Preencha idade, peso e altura no perfil; salve e confira persistência e IMC. Dados clínicos são opcionais.
5. Reabra a consulta pelo histórico; demonstre os filtros.
6. Em Dados e privacidade, visualize e exporte o JSON.
7. Saia. Solicite recuperação da conta fictícia. Abra http://127.0.0.1:8025, selecione a mensagem e use o link. Redefina a senha e entre novamente. A mensagem é entregue apenas à caixa local de teste, não a Gmail/Outlook.
8. Entre como administrador. Mostre versões, auditoria e contas. Ações de importação e reativação preservam o histórico.
9. Para demonstrar cores e regras, importe `data/demo-sintetico.json`. Informe explicitamente que são dados fictícios. Consulte os medicamentos com prefixo DEMONSTRAÇÃO; não use esse arquivo como evidência clínica. O perfil hepático aciona uma regra nesse cenário de software.
10. Ao terminar, na Administração, use **Ativar versão** em **fontes-oficiais-2026-10-08**. O catálogo volta a apresentar seus registros.

Para testar exclusão, crie uma conta descartável; não exclua as contas preparadas de apresentação.

## Verificações realizadas

25 testes Python aprovados; compilação de produção aprovada. Fluxo completo Chrome validado: cadastro, consulta, evidências, grafo, perfil, histórico, exportação, mobile, recuperação por SMTP local e exclusão. O catálogo foi testado no link HTTPS: paginação dos 25 medicamentos, busca por alimento/sinônimo, associação sugerida, resultado com orientação/fonte/data e histórico. Cookies Secure/HttpOnly verificados. Dois avisos de depreciação nas bibliotecas de teste, sem falhas.

## O que o sistema faz e seus limites

A base ativa `fontes-oficiais-2026-10-08` contém 25 medicamentos, 19 alimentos/bebidas, 49 associações e 23 referências. A busca consulta registros cadastrados; não usa MLP nem prevê combinações ausentes. A classificação numérica só existe se uma versão importada declarar fundamento e revisão. As regras de perfil são acadêmicas, não validadas clinicamente. Ausência de registro não comprova segurança.

As fontes da FDA e MedlinePlus/ASHP são externas. O texto em português é uma síntese, não uma bula oficial brasileira nem revisão clínica independente. Os registros podem descrever precauções, restrições ou consistência alimentar; não são todos equivalentes em gravidade. A amostra FooDrugs de 100 registros é separada e não é a base integral.

O e-mail funciona na caixa local de demonstração; entrega a Gmail/Outlook exige configuração de SMTP real. O link público é temporário e depende do computador ligado e conectado. Não houve implantação permanente nem teste de carga.

## Manutenção

O build do Vite é servido pelo FastAPI. Node é usado na compilação; Vite não mantém o computador online. Para recompilar: `cd frontend` e `npm run build`. Testes: `cd backend` e `../.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider`. Com a aplicação e Mailpit iniciados: `cd frontend` e `node e2e.mjs`.

As ferramentas locais Mailpit 1.31.4 e cloudflared 2026.10.0 ficam em `.local-tools/`. Senhas, bancos, backups e logs não entram no pacote de código. Para trocar de computador, use `setup.ps1`; os atalhos e as ferramentas locais precisam ser preparados naquele computador.
