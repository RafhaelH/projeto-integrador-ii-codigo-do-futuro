# Requisitos não funcionais

## Usabilidade e acessibilidade

| ID | Prioridade | Requisito verificável |
|---|---|---|
| RNF-001 | Must | A interface deve se adaptar a larguras de celular e computador sem rolagem horizontal nos fluxos principais. |
| RNF-002 | Must | Formulários devem possuir rótulos visíveis, indicação de obrigatoriedade e mensagens associadas ao campo inválido. |
| RNF-003 | Must | Todas as ações devem oferecer feedback perceptível de sucesso, falha ou processamento. |
| RNF-004 | Must | A navegação por teclado deve alcançar os controles dos fluxos críticos, com foco visível. |
| RNF-005 | Must | Texto e componentes essenciais devem manter contraste compatível com WCAG 2.1 nível AA. |
| RNF-006 | Should | Um novo usuário deve concluir uma inscrição orientada sem ajuda externa durante o teste de aceitação. |

## Segurança e privacidade

| ID | Prioridade | Requisito verificável |
|---|---|---|
| RNF-007 | Must | Senhas nunca devem ser armazenadas em texto puro e devem usar o mecanismo seguro do framework. |
| RNF-008 | Must | Todas as operações protegidas devem exigir autenticação e autorização no servidor. |
| RNF-009 | Must | A aplicação deve usar proteção contra CSRF, XSS, injeção SQL e sequestro de sessão oferecida ou recomendada pelo framework. |
| RNF-010 | Must | Configurações sensíveis devem vir de variáveis de ambiente e não podem ser versionadas. |
| RNF-011 | Must | Usuários devem visualizar somente os dados necessários ao seu papel e vínculo. |
| RNF-012 | Must | Dados pessoais coletados devem ser limitados ao necessário para executar e comprovar as atividades do projeto. |
| RNF-013 | Must | O ambiente publicado deve utilizar HTTPS. |
| RNF-014 | Should | O sistema deve registrar autoria e horário de operações acadêmicas sensíveis. |

## Desempenho e capacidade

| ID | Prioridade | Requisito verificável |
|---|---|---|
| RNF-015 | Must | Páginas comuns devem responder em até 2 segundos no percentil 95, em ambiente de teste com até 50 usuários simultâneos e base de referência. |
| RNF-016 | Must | Listagens devem usar paginação e filtros no servidor quando ultrapassarem 25 registros. |
| RNF-017 | Should | Relatórios do MVP devem ser produzidos em até 5 segundos com uma base de até 10 mil inscrições. |

## Confiabilidade e integridade

| ID | Prioridade | Requisito verificável |
|---|---|---|
| RNF-018 | Must | Operações que alteram inscrição e vaga devem ser atômicas. |
| RNF-019 | Must | Chaves e restrições do banco devem impedir duplicidades e referências inválidas definidas nas regras de negócio. |
| RNF-020 | Must | Erros inesperados não devem expor código, credenciais ou detalhes internos ao usuário. |
| RNF-021 | Should | O ambiente publicado deve possuir rotina de backup documentada e teste de restauração. |

## Manutenibilidade e qualidade

| ID | Prioridade | Requisito verificável |
|---|---|---|
| RNF-022 | Must | O código deve seguir a separação modular e as convenções definidas na arquitetura. |
| RNF-023 | Must | Regras críticas de vagas, idade, frequência e conclusão devem possuir testes automatizados. |
| RNF-024 | Must | O repositório deve executar análise estática e testes automaticamente em pull requests. |
| RNF-025 | Must | Dependências devem ser fixadas em arquivo versionado e atualizadas de forma controlada. |
| RNF-026 | Must | O projeto deve possuir instruções reproduzíveis de instalação, migração, testes e execução. |

## Compatibilidade

| ID | Prioridade | Requisito verificável |
|---|---|---|
| RNF-027 | Must | A interface deve funcionar nas duas versões estáveis mais recentes de Chrome, Edge e Firefox no momento da entrega. |
| RNF-028 | Must | Datas e horários devem ser apresentados no fuso `America/Sao_Paulo` e armazenados com informação de fuso. |
| RNF-029 | Must | A interface e as mensagens destinadas ao usuário devem estar em português brasileiro. |

## Observação sobre mensuração

Os limites de volume são metas do projeto acadêmico, não uma promessa de escala comercial. Os dados e o roteiro usados na medição deverão ser registrados junto às evidências de teste.
