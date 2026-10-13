# Defeitos encontrados

## DEF-001 — MÉDIO — Início duplicado de encontro retorna HTTP 500

Casos: HTTP-101, HTTP-297

Passos:

1. Administrador abre o cadastro de encontro numa turma exclusiva não encerrada.
2. Envia início e fim válidos, com início igual ao de um encontro existente.

Esperado: HTTP 200 com erro de duplicidade no formulário; nenhuma gravação.

Observado: HTTP 500 em duas execuções; nenhuma gravação indevida. IntegrityError/UniqueViolation na constraint workshops_meeting_start_unique.

Correção proposta: Validar (class_group, starts_at) no MeetingForm considerando a instância editada e tratar IntegrityError de disputa como erro de formulário. Manter a constraint.

## DEF-002 — ALTO — RF-006 sem fluxo para editar o próprio perfil

Casos: HTTP-260

Passos:

1. Participante autentica pela tela publicada.
2. Abre a página inicial e procura o ponto de entrada para consultar/editar seu perfil.

Esperado: Fluxo autenticado para consulta e atualização dos campos próprios permitidos, conforme RF-006 (Must).

Observado: Página HTTP 200 sem opção de edição própria; inventário de URLs não contém endpoint correspondente. Nenhum caminho inexistente foi inventado ou testado.

Correção proposta: Implementar fluxo próprio por sessão com campos permitidos, objeto vinculado a request.user e proteção contra alteração de papel/permissões; testar os três perfis.

## DEF-003 — ALTO — Django admin permite concluir turma fora do processamento acadêmico

Casos: HTTP-320

Passos:

1. Criar turma exclusiva PLANNED, sem instrutor, encontros, inscrições ou avaliações.
2. Abrir seu formulário real em /admin/workshops/classgroup/<id>/change/.
3. Enviar status=COMPLETED com os demais campos válidos e management forms das inlines.

Esperado: Rejeição da alteração e manutenção do estado PLANNED, conforme RN-015/RN-038 e o fluxo de transições.

Observado: HTTP 302; status PLANNED → COMPLETED gravado sem critérios acadêmicos. Apenas a turma exclusiva deste teste foi afetada.

Correção proposta: Tornar status somente leitura no ModelAdmin e encaminhar transições ao serviço de domínio; evitar gravações diretas que contornem os critérios. Aplicar guardas equivalentes aos demais modelos acadêmicos expostos no admin.
