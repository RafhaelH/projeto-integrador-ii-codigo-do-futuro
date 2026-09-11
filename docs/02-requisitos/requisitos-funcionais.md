# Requisitos funcionais

## Convenções

- **Must:** obrigatório para a entrega do MVP.
- **Should:** importante, implementado após os itens Must.
- **Could:** desejável, condicionado ao tempo disponível.

## Autenticação e usuários

| ID | Prioridade | Requisito |
|---|---|---|
| RF-001 | Must | O sistema deve autenticar usuários ativos por e-mail e senha. |
| RF-002 | Must | O sistema deve encerrar a sessão do usuário. |
| RF-003 | Must | O sistema deve permitir a redefinição segura de senha. |
| RF-004 | Must | O administrador deve cadastrar, consultar, editar, ativar e desativar usuários. |
| RF-005 | Must | O sistema deve restringir telas e ações conforme o perfil do usuário. |
| RF-006 | Must | O usuário deve consultar e atualizar os dados permitidos do próprio perfil. |

## Pessoas e instituições

| ID | Prioridade | Requisito |
|---|---|---|
| RF-007 | Must | O administrador deve cadastrar, consultar e editar participantes. |
| RF-008 | Must | O administrador deve cadastrar e vincular responsáveis legais a participantes menores de idade. |
| RF-009 | Must | O administrador deve cadastrar, consultar e editar instrutores. |
| RF-010 | Should | O administrador deve cadastrar, consultar, editar e arquivar instituições parceiras. |

## Oficinas, turmas e encontros

| ID | Prioridade | Requisito |
|---|---|---|
| RF-011 | Must | O administrador deve cadastrar, editar, consultar, publicar e arquivar oficinas. |
| RF-012 | Must | O administrador deve criar, editar, consultar e cancelar turmas vinculadas a uma oficina. |
| RF-013 | Must | O administrador deve atribuir um ou mais instrutores a uma turma. |
| RF-014 | Must | O administrador deve cadastrar, editar e cancelar encontros de uma turma. |
| RF-015 | Must | Usuários autorizados devem consultar o cronograma da turma. |
| RF-016 | Must | O administrador deve alterar a situação da turma conforme o fluxo permitido. |

## Inscrições e vagas

| ID | Prioridade | Requisito |
|---|---|---|
| RF-017 | Must | O participante deve solicitar inscrição em uma turma com inscrições abertas. |
| RF-018 | Must | O administrador deve registrar uma inscrição em nome de um participante. |
| RF-019 | Must | O administrador deve confirmar ou rejeitar uma inscrição pendente. |
| RF-020 | Must | O sistema deve controlar a ocupação da turma sem ultrapassar sua capacidade. |
| RF-021 | Should | O sistema deve incluir o participante em lista de espera quando não houver vaga. |
| RF-022 | Should | O administrador deve promover uma inscrição da lista de espera quando surgir uma vaga. |
| RF-023 | Must | O participante ou administrador deve cancelar uma inscrição dentro das condições permitidas. |
| RF-024 | Must | O usuário autorizado deve consultar inscrições por turma, participante e situação. |

## Frequência, projetos e avaliação

| ID | Prioridade | Requisito |
|---|---|---|
| RF-025 | Must | O instrutor da turma ou administrador deve registrar e corrigir a frequência por encontro. |
| RF-026 | Must | O sistema deve calcular o percentual de frequência do participante na turma. |
| RF-027 | Should | O participante deve registrar ou atualizar seu projeto enquanto a turma permitir entregas. |
| RF-028 | Should | O instrutor da turma ou administrador deve consultar e revisar os projetos. |
| RF-029 | Must | O instrutor da turma ou administrador deve registrar a avaliação final do participante. |
| RF-030 | Must | O sistema deve determinar a conclusão com base nos critérios da turma. |

## Certificados, painel e relatórios

| ID | Prioridade | Requisito |
|---|---|---|
| RF-031 | Should | O sistema deve gerar certificado para inscrição concluída com aprovação. |
| RF-032 | Should | O participante e o administrador devem consultar e baixar certificados autorizados. |
| RF-033 | Must | O administrador deve visualizar indicadores de participantes, inscrições, ocupação, frequência e conclusão. |
| RF-034 | Must | O instrutor deve visualizar indicadores apenas de suas turmas. |
| RF-035 | Should | O administrador deve emitir relatórios filtrados de inscrições, frequência e conclusão. |
| RF-036 | Should | O sistema deve exportar relatórios tabulares em CSV. |

## Rastreabilidade e operação

| ID | Prioridade | Requisito |
|---|---|---|
| RF-037 | Must | O sistema deve registrar data de criação e última alteração dos registros principais. |
| RF-038 | Must | O sistema deve identificar o usuário responsável pelos registros de frequência e avaliação. |
| RF-039 | Must | O sistema deve apresentar mensagens claras de sucesso, validação e erro. |
| RF-040 | Must | O sistema deve permitir arquivamento ou desativação nos cadastros que possuem histórico associado. |

## Dependências principais

| Requisito | Depende de |
|---|---|
| RF-008 | RF-007 |
| RF-012 | RF-011 |
| RF-014 | RF-012 |
| RF-017 | RF-001, RF-007, RF-012, RF-016 |
| RF-019 | RF-018 ou RF-017 |
| RF-025 | RF-014, RF-019 |
| RF-029 | RF-019 |
| RF-030 | RF-026, RF-029 |
| RF-031 | RF-030 |
| RF-033 | dados produzidos pelos módulos anteriores |
