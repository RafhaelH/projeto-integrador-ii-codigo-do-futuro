# Plano de testes

## Objetivo

Verificar se a aplicação atende às especificações e validar se os fluxos resolvem a necessidade dos usuários com segurança e clareza.

## Escopo

- modelos e restrições;
- serviços e regras de negócio;
- formulários e validações;
- autorização por papel e vínculo;
- views e respostas HTTP;
- fluxos completos pelo navegador;
- responsividade e acessibilidade essencial;
- concorrência no controle de vagas;
- indicadores e relatórios.

## Estratégia

| Nível | Foco | Exemplos |
|---|---|---|
| Unitário | função ou regra isolada | idade, frequência, nota, transições |
| Integração | módulos e banco | confirmação com vaga, restrições, permissões |
| Interface | formulários e views | mensagens, status HTTP, filtros |
| Ponta a ponta | jornada real | inscrição até certificado |
| Exploratória | comportamento não previsto | navegação, textos e estados incomuns |
| Aceitação | adequação ao usuário | cinco avaliadores executando tarefas |

## Ambientes

- **Local:** desenvolvimento e testes rápidos.
- **CI:** banco isolado, lint, migrações e suíte automatizada.
- **Homologação:** configuração próxima da publicação, dados fictícios e testes manuais.
- **Produção acadêmica:** demonstração e avaliação, sem dados sensíveis reais.

## Dados de teste

Uma carga reproduzível deverá conter:

- um administrador;
- dois instrutores, cada um com turmas distintas;
- participantes adulto e menor com responsável;
- participante menor sem responsável para cenário inválido;
- oficina em cada situação;
- turma com vagas, turma lotada e turma concluída;
- encontros futuros, realizados e cancelados;
- inscrições em todas as situações;
- frequências que resultem em aprovação e não conclusão.

Credenciais de demonstração não serão usadas em produção real e serão documentadas apenas no local apropriado.

## Casos críticos iniciais

| ID | Cenário | Resultado esperado | Referências |
|---|---|---|---|
| CT-001-01 | Login de usuário ativo | sessão iniciada | RF-001; CA-001-01 |
| CT-001-02 | Login de usuário inativo | acesso negado sem vazamento | RN-002; CA-001-02 |
| CT-005-01 | Participante acessa gestão por URL | HTTP 403 ou resposta equivalente | RF-005; CA-005-01 |
| CT-008-01 | Inscrição de menor sem responsável | operação bloqueada | RN-005; CA-008-02 |
| CT-012-01 | Turma com datas inválidas | formulário rejeitado | RN-011–012; CA-012-02 |
| CT-016-01 | Abrir turma sem instrutor | transição bloqueada | RN-014; CA-016-01 |
| CT-018-01 | Duas inscrições na mesma turma | segunda rejeitada | RN-018; CA-018-01 |
| CT-020-01 | Duas confirmações para última vaga | apenas uma confirmada | RN-022; CA-020-01 |
| CT-021-01 | Inscrição em turma lotada | entrada correta na fila | RN-023–024; CA-021-01 |
| CT-022-01 | Vaga liberada com fila | mais antigo promovido | RN-025; CA-022-01 |
| CT-025-01 | Chamada repetida | atualização sem duplicidade | RN-030; CA-025-01 |
| CT-025-02 | Instrutor de outra turma registra chamada | acesso negado | RN-029; CA-025-02 |
| CT-026-01 | 6 presenças em 8 encontros | frequência de 75% | RN-031–032; CA-026-01 |
| CT-029-01 | Nota 10,1 | avaliação rejeitada | RN-035; CA-029-02 |
| CT-030-01 | 75%, nota 6 e projeto entregue | aprovação | RN-036; CA-030-01 |
| CT-030-02 | 74,9%, nota 10 e projeto entregue | não conclusão | RN-036–037; CA-030-02 |
| CT-031-01 | Certificado de não concluinte | emissão negada | RN-039; CA-031-02 |
| CT-034-01 | Painel do instrutor | somente turmas vinculadas | RN-044; CA-034-01 |

## Testes não funcionais

| Área | Método | Evidência |
|---|---|---|
| Responsividade | conferir fluxos críticos em viewport móvel e desktop | screenshots e checklist |
| Acessibilidade | teclado, foco, rótulos, contraste e análise automatizada | relatório e inspeção |
| Desempenho | carga controlada com base de referência | script, parâmetros e resultados |
| Segurança | checks do Django, testes de autorização e revisão de segredos | saída da CI |
| Backup | restaurar uma cópia em ambiente descartável | procedimento e registro |

## Severidade de defeitos

| Nível | Definição | Condição para entrega |
|---|---|---|
| Crítico | perda/exposição de dados ou fluxo principal indisponível | zero aberto |
| Alto | função Must incorreta sem alternativa aceitável | zero aberto |
| Médio | impacto parcial com alternativa | decisão documentada |
| Baixo | detalhe visual ou melhoria sem bloqueio | pode compor backlog futuro |

## Critério de encerramento

- todos os testes críticos aprovados;
- todos os itens Must cobertos por ao menos um teste;
- nenhuma falha crítica ou alta aberta;
- cinco avaliações registradas;
- regressão executada após as correções;
- evidências organizadas para o relatório final.
