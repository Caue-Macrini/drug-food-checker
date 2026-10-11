# Rastreabilidade do TCC

| Requisito | Implementação / limite |
|---|---|
| RF001 autenticar | Login com BCrypt, cookie HttpOnly e JWT revogável |
| RF002 criar conta | Formulário e validação de cadastro |
| RF003 recuperar senha | SMTP configurável, token hash de uso único / 30 min; outbox local sem SMTP |
| RF004 consentimento | Aceite obrigatório, versão 1.0, data registrada |
| RF005 perfil | Campos opcionais persistidos com validação |
| RF006 IMC | Cálculo visual e no servidor, sem interpretação diagnóstica |
| RF007 consulta | Busca indexada sobre os 161.495 termos de medicamentos e 50.796 termos alimentares da FooDrugs, com sinônimos em português; IDs confirmados e busca por par indexado (RapidFuzz no catálogo complementar) |
| RF008 cores | Indicador circular verde/amarelo/vermelho (Figura 16) com resposta direta em português. Nível base 0–2 derivado por regras explícitas sobre os trechos da FooDrugs (ver CLASSIFICACAO-RISCO.md); par ausente fica verde com ressalva (fluxo alternativo, p. 39) |
| RF009 personalização | Quatro modificadores da Tabela 2 (p. 31) aplicados ao nível base, limitados a 0–2; propriedades CYP450, excreção renal e hepatotoxicidade vêm de listas explícitas e do mecanismo detectado nos trechos |
| RF010 explicação | Explicação simplificada em português (como a interação acontece, tipo farmacocinética/farmacodinâmica, mecanismo detectado), "por que esta classificação" e o trecho original de cada documento, marcado como "indica interação", "apenas menciona" ou "sem efeito observado" |
| RF011 referência | Identificador do registro e do documento, link para a referência original, versão da base e DOI do depósito FooDrugs |
| RF012 grafo | Cytoscape.js, zoom, arrastar, selecionar e alternativa por botões |
| RF013 histórico | Histórico isolado por conta, filtros e snapshot original |
| RF014 visualizar dados | Conta, perfil, consentimento, consultas e auditoria própria |
| RF015 exportar | Download JSON no navegador |
| RF016 excluir | Confirmação + senha; remove dados associados do banco ativo |
| RF017 base | FooDrugs 4.0.0 completa importada (10 tabelas, 30.797.702 registros, checksum oficial) por `Instalar-FooDrugs.ps1`; tela Dados FooDrugs; importação JSON transacional e versionamento para outras bases |
| RF018 logs | Auditoria pseudônima na administração e logs de execução no servidor |
| RF019 contas | Ativar, desativar e excluir; administradores gerenciados por CLI |

RNF: BCrypt custo 12, consentimento, design responsivo, validações, índice por par, testes, cookies protegidos, controle de acesso, rate limit e auditoria implementados. HTTPS está configurado via Caddy para implantação. O limitador é de processo único; distribuição entre réplicas requer armazenamento compartilhado. Com a base completa, consultas de par e buscas de termos levam milissegundos na camada de dados (medição de 10/10/2026), dentro da meta de 3 s; não foram feitos teste de carga com usuários simultâneos, comprovação de disponibilidade operacional ou conformidade regulatória integral.

Diferenças em relação ao texto do TCC: a FooDrugs não fornece nível de risco pronto (p. 31 afirma que sim); o sistema o deriva por regras explícitas e auditáveis, coerente com a justificativa da própria p. 31 para preferir regras a modelos probabilísticos. A classificação e as regras do perfil são heurísticas acadêmicas, sem validação clínica; o desempenho medido (80% de concordância com o Drugs.com; 86,7% de precisão e 70,3% de sensibilidade em avaliação cega de pares realistas) está em CLASSIFICACAO-RISCO.md. A base integral FooDrugs está implementada; revisão clínica, SMTP real e operação pública permanente dependem de dados/infraestrutura adicionais. Os esquemas do DER foram simplificados com campos JSON onde adequado.
