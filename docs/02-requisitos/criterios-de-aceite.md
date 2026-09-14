# Critérios de aceite e rastreabilidade

Os critérios abaixo descrevem comportamentos observáveis. Os identificadores serão reutilizados nos testes manuais e automatizados.

## Acesso

### CA-001-01 — Autenticação válida

**Dado** um usuário ativo com credenciais válidas, **quando** ele autenticar, **então** o sistema deve iniciar a sessão e direcioná-lo ao painel compatível com seu perfil.

### CA-001-02 — Autenticação inválida

**Dado** um e-mail inexistente, senha incorreta ou usuário inativo, **quando** houver tentativa de acesso, **então** o sistema deve negar a autenticação sem informar qual dado está incorreto.

### CA-005-01 — Proteção por perfil

**Dado** um usuário sem permissão para uma operação, **quando** tentar acessá-la pela interface ou por URL direta, **então** o servidor deve negar a ação sem alterar dados.

## Participantes e responsáveis

### CA-007-01 — Cadastro válido

**Dado** um administrador e dados válidos, **quando** cadastrar um participante, **então** o sistema deve salvar o perfil e confirmar a operação.

### CA-008-01 — Menor com responsável

**Dado** um participante menor de 18 anos, **quando** seus dados forem preparados para inscrição, **então** deve existir ao menos um responsável ativo com os campos obrigatórios.

### CA-008-02 — Menor sem responsável

**Dado** um participante menor de 18 anos sem responsável, **quando** tentarem inscrevê-lo, **então** o sistema deve bloquear a inscrição e explicar como corrigir a pendência.

## Oficinas, turmas e encontros

### CA-011-01 — Publicação de oficina

**Dado** uma oficina em rascunho com nome, objetivo, descrição e conteúdo, **quando** o administrador publicar, **então** ela deve ficar disponível para criação de turmas.

### CA-012-01 — Turma válida

**Dado** uma oficina publicada, **quando** o administrador informar capacidade, local, período de inscrições e período de realização válidos, **então** a turma deve ser criada como planejada.

### CA-012-02 — Datas inconsistentes

**Dado** um período cronologicamente inválido, **quando** o administrador salvar a turma, **então** o sistema deve rejeitar a operação e destacar os campos inconsistentes.

### CA-016-01 — Abertura de inscrições

**Dado** uma turma planejada com capacidade válida e instrutor ativo, **quando** o administrador abrir inscrições, **então** a situação deve mudar e a turma deve aceitar inscrições dentro do prazo.

### CA-014-01 — Encontro dentro da turma

**Dado** uma turma válida, **quando** um encontro for cadastrado fora do seu período, **então** o sistema deve rejeitar a operação.

## Inscrições e vagas

### CA-017-01 — Inscrição elegível

**Dado** participante ativo e elegível e turma aberta com vaga, **quando** solicitar inscrição, **então** o sistema deve criar uma inscrição sem duplicidade e apresentar sua situação.

### CA-017-02 — Faixa etária inválida

**Dado** participante fora da faixa de 14 a 21 anos na data inicial da turma, **quando** tentar inscrição, **então** o sistema deve bloquear a solicitação com mensagem clara.

### CA-018-01 — Duplicidade

**Dado** participante já inscrito na turma, **quando** houver nova tentativa de inscrição, **então** o sistema deve rejeitar a duplicidade sem criar outro registro.

### CA-020-01 — Limite de vagas

**Dado** uma turma cuja quantidade de confirmados atingiu a capacidade, **quando** outra inscrição for processada, **então** ela não pode ser confirmada nem elevar a ocupação acima de 100%.

### CA-021-01 — Lista de espera

**Dado** uma turma lotada com lista de espera habilitada, **quando** um participante elegível se inscrever, **então** a inscrição deve entrar no fim da fila e informar sua posição.

### CA-022-01 — Promoção

**Dado** uma vaga liberada e inscrições em espera, **quando** ocorrer promoção, **então** a inscrição mais antiga elegível deve ser confirmada e a ocupação deve voltar a refletir a capacidade.

### CA-023-01 — Cancelamento antes do início

**Dado** uma inscrição confirmada e turma ainda não iniciada, **quando** o participante cancelar, **então** a inscrição deve ser marcada como cancelada e a vaga liberada.

## Frequência, avaliação e conclusão

### CA-025-01 — Chamada da turma

**Dado** encontro pertencente à turma do instrutor, **quando** ele registrar a chamada, **então** deve existir no máximo um resultado por inscrição confirmada e encontro.

### CA-025-02 — Instrutor não vinculado

**Dado** um instrutor não atribuído à turma, **quando** tentar registrar frequência, **então** o sistema deve negar a operação.

### CA-026-01 — Cálculo de frequência

**Dado** 8 encontros realizados, 6 presenças, 1 ausência e 1 falta justificada, **quando** o sistema calcular a frequência, **então** o resultado deve ser 75%.

### CA-029-01 — Nota válida

**Dado** uma inscrição confirmada, **quando** o instrutor registrar uma nota entre 0,0 e 10,0 e uma devolutiva, **então** a avaliação deve ser salva com autoria e horário.

### CA-029-02 — Nota inválida

**Dado** uma nota fora do intervalo, **quando** houver tentativa de salvar, **então** o sistema deve rejeitá-la sem alterar a avaliação anterior.

### CA-030-01 — Aprovação

**Dado** participante com 75% ou mais de frequência, nota 6,0 ou maior e projeto entregue, **quando** a turma for concluída, **então** sua inscrição deve ficar concluída com aprovação.

### CA-030-02 — Não conclusão

**Dado** participante que descumpre ao menos um critério obrigatório, **quando** a turma for concluída, **então** sua inscrição deve ficar como não concluída e indicar os critérios não atendidos.

## Certificado e indicadores

### CA-031-01 — Emissão autorizada

**Dado** inscrição concluída com aprovação, **quando** o certificado for gerado, **então** deve conter dados da RN-042 e código único.

### CA-031-02 — Emissão bloqueada

**Dado** inscrição ainda ativa ou não concluída, **quando** tentarem gerar certificado, **então** o sistema deve negar a emissão.

### CA-032-01 — Consulta autorizada

**Dado** um certificado ativo, **quando** o participante titular, o administrador ou um instrutor vinculado consultar ou baixar o documento, **então** o sistema deve permitir o acesso.

### CA-032-02 — Consulta bloqueada

**Dado** um certificado de outro participante ou de turma não vinculada, **quando** houver tentativa de acesso, **então** o sistema deve negar a consulta sem expor os dados do documento.

### CA-033-01 — Painel filtrado

**Dado** um período e filtros selecionados, **quando** o administrador consultar o painel, **então** todos os indicadores devem representar o mesmo universo filtrado.

### CA-034-01 — Painel do instrutor

**Dado** um instrutor autenticado, **quando** abrir o painel, **então** nenhuma informação de turma não vinculada pode aparecer.

### CA-035-01 — Relatórios filtrados

**Dado** filtros válidos de período, oficina e situação, **quando** o administrador consultar ou exportar um relatório, **então** os registros devem pertencer ao mesmo universo informado no painel.

### CA-036-01 — Exportação protegida

**Dado** um administrador autenticado, **quando** exportar inscrições, frequência ou conclusão, **então** o sistema deve entregar CSV em UTF-8 sem CPF, telefone ou e-mail.

**Dado** um instrutor ou participante, **quando** tentar acessar diretamente uma exportação, **então** o sistema deve negar a operação.

## Matriz de rastreabilidade inicial

| Fluxo | Requisitos | Regras | Casos de uso | Testes mínimos |
|---|---|---|---|---|
| Autenticação e autorização | RF-001–006 | RN-001–003, RN-043–044 | UC-001, UC-002 | unitário, integração e segurança |
| Pessoas | RF-007–010 | RN-004–007 | UC-003 | modelo, serviço e formulário |
| Oferta educacional | RF-011–016 | RN-008–017 | UC-004, UC-005 | serviço, transição e interface |
| Inscrição e vagas | RF-017–024 | RN-018–028 | UC-006, UC-007 | concorrência, integração e E2E |
| Frequência | RF-025–026 | RN-029–033 | UC-008 | cálculo, permissão e interface |
| Projeto e avaliação | RF-027–030 | RN-034–038 | UC-009, UC-010 | validação e conclusão |
| Certificados | RF-031–032 | RN-039–042 | UC-011 | geração e autorização |
| Indicadores e relatórios | RF-033–036 | RN-043–045, RN-048 | UC-012 | agregação, filtro e permissão |
| Rastreabilidade operacional | RF-037–040 | RN-007, RN-028, RN-033 | transversal | modelo e integração |

## Condição de aceite do MVP

O MVP poderá ser apresentado aos avaliadores quando todos os requisitos **Must** tiverem ao menos um teste aprovado, nenhum defeito crítico estiver aberto e os fluxos UC-001, UC-006, UC-008 e UC-010 puderem ser executados de ponta a ponta.
