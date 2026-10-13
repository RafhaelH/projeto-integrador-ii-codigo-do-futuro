# Matriz de permissões implementadas

Referência a351c5a/develop 644e7a6. Colunas descrevem acessos funcionais do MVP, sem privilégios adicionais do Django admin. Ocultar botão não substitui autorização: mixins, querysets e serviços conferem papel/vínculo/titularidade. Fontes: accounts/mixins.py, views/seletores dos domínios e testes negativos de acesso.

| Recurso/ação | ADMIN funcional | INSTRUCTOR | PARTICIPANT |
|---|---|---|---|
| Meu perfil (/conta/perfil/) | Próprio nome/e-mail | Próprio nome/e-mail | Próprio nome/e-mail |
| Contas/papéis de terceiros | Exige staff/permissões no Django admin | Sem gestão funcional | Sem gestão funcional |
| Cadastros de participantes/responsáveis | Criar/consultar/editar/vincular/desativar | Sem acesso às telas de Pessoas; nomes/resultados das turmas vinculadas no acompanhamento | Sem acesso às telas de Pessoas; dados da conta no perfil e jornada própria |
| Cadastro de instrutores | Criar/consultar/editar | Sem acesso ao cadastro; próprio nome de conta | Sem acesso ao cadastro |
| Cadastro de instituições | Criar/consultar/editar/desativar | Sem cadastro; nome/local da instituição na turma atribuída | Sem cadastro; local apresentado na oferta disponível |
| Cadastro/publicação/arquivamento de oficina | Gerenciar | Sem tela de cadastro/detalhe de oficina; título associado à turma | Sem detalhe administrativo; descrição da oferta disponível |
| Turmas/detalhe/cronograma | Criar/editar planejada, transicionar/cancelar conforme serviço | Consultar apenas atribuídas | Consultar ofertas/datas e jornada; sem detalhe administrativo/agenda de encontros |
| Atribuição de instrutores/agenda | Gerenciar nas condições permitidas | Consultar; não criar/editar/cancelar agenda | Sem gestão |
| Inscrições | Registrar/confirmar/rejeitar/promover/cancelar com motivo; consultar global | Consultar apenas das turmas atribuídas | Solicitar próprias em prazo, consultar e cancelar antes do início |
| Fila da turma | Consultar/processar | Consultar somente turma atribuída | Sem fila global; situação/posição próprias em Minhas inscrições |
| Frequência/chamada | Registrar/corrigir/consultar | Registrar/corrigir/consultar com vínculo ativo | Consultar própria; sem chamada |
| Projeto | Consultar/revisar devolutiva; não registrar entrega como participante | Consultar/revisar da turma atribuída | Registrar/alterar somente próprio em inscrição confirmada/turma IN_PROGRESS |
| Avaliação final | Registrar/publicar/consultar conforme serviço | Registrar/publicar em turma atribuída e vínculo ativo | Consultar própria somente após publicação |
| Concluir turma/emitir/revogar certificado | Exclusivo ADMIN, guardas acadêmicas e motivo de revogação | Não permitido | Não permitido |
| Consultar/baixar certificado | Consulta global; download só ativo | Ativo da turma atribuída, instrutor ativo | Ativo próprio |
| Painel (/painel/) | Global com filtros | Turmas atribuídas com filtros | Negado; resumo próprio em Início/Minha jornada |
| Exportações CSV (/painel/relatorios/) | Exclusivo ADMIN | Negado | Negado |

## Restrições e particularidades

1. O Django admin usa is_staff/permissões (ou superusuário), distintos de role. A01/A02 são ADMIN funcionais sem staff, superusuário, grupos ou permissões extras. Contas com concessões especiais devem ser avaliadas também segundo os controles do Django admin; o papel sozinho não concede esse acesso.
2. Instrutor conhecer UUID não concede vínculo; consultas fora do escopo retornam 404 ou papel negado 403 conforme a view. Participante não vê dados acadêmicos/contatos de terceiros.
3. A matriz antiga projetava acesso mínimo de responsáveis/instituições/oficinas e agenda do participante; a implementação atual restringe as telas administrativas. **Não há tela de responsáveis para instrutor nem agenda completa dos encontros para participante.** Esta revisão documenta o limite; não cria novas permissões.
4. Chamada pode marcar encontro como COMPLETED pelo serviço; isso não concede edição administrativa da agenda ao instrutor. Projeto só é entregue pelo titular; ADMIN/instrutor revisam devolutiva.
5. Status acadêmicos no admin são readonly e POSTs forjados são rejeitados antes da gravação; conclusão usa complete_class_group, emissão/revogação os serviços próprios.
6. O último administrador ativo não pode perder acesso/ativação/papel; testes dessa proteção ocorreram somente em banco descartável.
7. CSV é exclusivo ADMIN e não contém CPF/telefone/e-mail. Usuários comuns não alteram role, senha ou privilégios pelo formulário de perfil próprio.

Evidências: [rastreabilidade](rastreabilidade-implementada.md), testes de views dos módulos, [HTTP e correções consolidados](../06-testes/consolidacao-verificacao.md). Não interpretar um resultado de teste por URL como avaliação humana de clareza das permissões.
