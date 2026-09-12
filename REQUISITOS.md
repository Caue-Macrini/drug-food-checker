# Rastreabilidade do TCC

| Requisito | Implementação / limite |
|---|---|
| RF001 autenticar | Login com BCrypt, cookie HttpOnly e JWT revogável |
| RF002 criar conta | Formulário e validação de cadastro |
| RF003 recuperar senha | SMTP configurável, token hash de uso único / 30 min; outbox local sem SMTP |
| RF004 consentimento | Aceite obrigatório, versão 1.0, data registrada |
| RF005 perfil | Campos opcionais persistidos com validação |
| RF006 IMC | Cálculo visual e no servidor, sem interpretação diagnóstica |
| RF007 consulta | RapidFuzz, aliases, IDs confirmados e busca por par indexado |
| RF008 cores | Verde/amarelo/vermelho quando risco revisado existe; cinza para desconhecido |
| RF009 personalização | Quatro regras da p. 31; saturação em 2; sem ajustes se base é nula |
| RF010 explicação | Texto de cada registro; associações NLP têm limitação explícita |
| RF011 referência | URL HTTPS e proveniência versionada; amostra NLP aponta ao depósito |
| RF012 grafo | Cytoscape.js, zoom, arrastar, selecionar e alternativa por botões |
| RF013 histórico | Histórico isolado por conta, filtros e snapshot original |
| RF014 visualizar dados | Conta, perfil, consentimento, consultas e auditoria própria |
| RF015 exportar | Download JSON no navegador |
| RF016 excluir | Confirmação + senha; remove dados associados do banco ativo |
| RF017 base | Importação JSON transacional, versão ativa e conversor do dump FooDrugs; recortes até 10 mil registros |
| RF018 logs | Auditoria pseudônima na administração e logs de execução no servidor |
| RF019 contas | Ativar, desativar e excluir; administradores gerenciados por CLI |

RNF: BCrypt custo 12, consentimento, design responsivo, validações, índice por par, testes, cookies protegidos, controle de acesso, rate limit e auditoria implementados. HTTPS está configurado via Caddy para implantação. O limitador é de processo único; distribuição entre réplicas requer armazenamento compartilhado. Não foram comprovadas metas de latência/carga para a base completa, disponibilidade operacional ou conformidade regulatória integral.

Diferenças deliberadas: resultado ausente não recebe sinal verde; a FooDrugs não é tratada como catálogo de gravidade clínica; as regras do TCC são apresentadas como heurísticas. A base integral, revisão clínica, SMTP real e operação pública dependem de dados/infraestrutura adicionais. Os esquemas do DER foram simplificados com campos JSON onde adequado.
