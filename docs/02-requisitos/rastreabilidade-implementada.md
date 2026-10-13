# Rastreabilidade da implementação e evidências

## Critério de leitura

Referência a351c5a, mesmo src de develop 644e7a6. A tabela liga os 40 RF à implementação e aos testes abertos na auditoria. **Cobertura funcional técnica** não equivale a aceite de usabilidade nem certificação de todos os RNF. Resultados e arquivos HTTP estão na [consolidação](../06-testes/consolidacao-verificacao.md); fontes das figuras em [capturas](../08-manual/plano-de-capturas.md). Requisitos, RN/CA e prioridades permanecem nos documentos existentes.

## Requisitos funcionais

| RF | Implementação (caminho/função) | Testes (sob tests) | Evidência/limite |
|---|---|---|---|
| RF-001 | [config/urls.py: auth LoginView](../../src/config/urls.py) | [accounts/test_authentication.py](../../tests/accounts/test_authentication.py) | Login ativo/inativo; HTTP técnico |
| RF-002 | [config/urls.py: LogoutView e base.html POST](../../src/config/urls.py) | [accounts/test_authentication.py](../../tests/accounts/test_authentication.py) | Logout; matriz HTTP |
| RF-003 | [config/urls.py: PasswordReset/Confirm views](../../src/config/urls.py) | [accounts/test_authentication.py](../../tests/accounts/test_authentication.py) | Token/senha/console; SMTP externo não comprovado |
| RF-004 | accounts/admin.py, forms.py: UserAdmin/UserChangeForm | [accounts/test_admin.py](../../tests/accounts/test_admin.py) | CRUD/admin HTTP histórico; proteção do último administrador |
| RF-005 | [accounts/mixins.py: RoleRequiredMixin; escopo nas views](../../src/apps/accounts/mixins.py) | [people/test_views.py](../../tests/people/test_views.py) | Bloqueios por papel e vínculo nas três execuções HTTP |
| RF-006 | [accounts/views.py: OwnProfileView e OwnProfileForm](../../src/apps/accounts/views.py) | [accounts/test_profile.py](../../tests/accounts/test_profile.py) | R-18 a R-21; figura 03 |
| RF-007 | [people/views.py: ParticipantCreate/Update/List/Detail](../../src/apps/people/views.py) | [people/test_views.py](../../tests/people/test_views.py) | Pessoa fictícia; figuras 04/05 |
| RF-008 | [people/models.py: ParticipantGuardian; services.py elegibilidade](../../src/apps/people/models.py) | [people/test_services.py](../../tests/people/test_services.py) | Menor com/sem responsável; figura 05 |
| RF-009 | [people/views.py: InstructorCreate/Update/List](../../src/apps/people/views.py) | [people/test_views.py](../../tests/people/test_views.py) | Perfil/usuário vinculados; figura 07 |
| RF-010 | [people/views.py: InstitutionCreate/Update; is_active](../../src/apps/people/views.py) | [people/test_views.py](../../tests/people/test_views.py) | Instituição/arquivamento; figura 08 |
| RF-011 | [workshops/services.py: transition_workshop](../../src/apps/workshops/services.py) | [workshops/test_services.py](../../tests/workshops/test_services.py) | Ciclo DRAFT/PUBLISHED/ARCHIVED; figuras 09/10 |
| RF-012 | [workshops/views.py: ClassGroupCreate/Update/Transition](../../src/apps/workshops/views.py) | [workshops/test_views.py](../../tests/workshops/test_views.py) | Datas/capacidade/cancelamento; figuras 11–14 |
| RF-013 | [workshops/models.py: ClassInstructor; views de vínculo](../../src/apps/workshops/models.py) | [workshops/test_models.py](../../tests/workshops/test_models.py) | Unicidade/um principal; figura 12 |
| RF-014 | [workshops/views.py: MeetingSaveMixin; cancel_meeting](../../src/apps/workshops/views.py) | [workshops/test_defect_regressions.py](../../tests/workshops/test_defect_regressions.py) | R-08, duplicidade/race; agenda figura 13 |
| RF-015 | [workshops/views.py: ClassGroupDetailView/escopo](../../src/apps/workshops/views.py) | [workshops/test_views.py](../../tests/workshops/test_views.py) | Agenda somente autorizada; figura 13 |
| RF-016 | [workshops/services.py: transition_class_group](../../src/apps/workshops/services.py) | [workshops/test_defect_regressions.py](../../tests/workshops/test_defect_regressions.py) | Estado/admin forjado R-22 a R-24 |
| RF-017 | [enrollments/services.py: create_enrollment](../../src/apps/enrollments/services.py) | [enrollments/test_services.py](../../tests/enrollments/test_services.py) | Elegibilidade/janela/titular; tarefa A05-3 |
| RF-018 | [enrollments/views.py: AdminEnrollmentCreateView](../../src/apps/enrollments/views.py) | [enrollments/test_views.py](../../tests/enrollments/test_views.py) | Cadastro administrativo HTTP |
| RF-019 | [enrollments/services.py: confirm/reject_enrollment](../../src/apps/enrollments/services.py) | [enrollments/test_services.py](../../tests/enrollments/test_services.py) | Decisão, motivo e histórico |
| RF-020 | [enrollments/services.py: occupied_places/_confirm_locked](../../src/apps/enrollments/services.py) | [enrollments/test_services.py](../../tests/enrollments/test_services.py) | Última vaga concorrente PostgreSQL; figura 15 |
| RF-021 | [enrollments/services.py: create_enrollment WAITLISTED](../../src/apps/enrollments/services.py) | [enrollments/test_services.py](../../tests/enrollments/test_services.py) | Fila com turma cheia; figura 15 |
| RF-022 | [enrollments/services.py: promote_next_waitlisted](../../src/apps/enrollments/services.py) | [enrollments/test_services.py](../../tests/enrollments/test_services.py) | Ordem, justificativa/exceção, promoção automática ao cancelar |
| RF-023 | [enrollments/services.py: cancel_enrollment](../../src/apps/enrollments/services.py) | [enrollments/test_services.py](../../tests/enrollments/test_services.py) | Titular antes do início, ADMIN com motivo; histórico preservado |
| RF-024 | [enrollments/views.py: EnrollmentList/Queue/Detail](../../src/apps/enrollments/views.py) | [enrollments/test_views.py](../../tests/enrollments/test_views.py) | Escopos e filtros; figura 15 |
| RF-025 | [learning/services.py: record_meeting_attendance](../../src/apps/learning/services.py) | [learning/test_services.py](../../tests/learning/test_services.py) | Autoria/correção/único; figuras 16/22/34 |
| RF-026 | [learning/services.py: calculate_attendance_summary](../../src/apps/learning/services.py) | [learning/test_services.py](../../tests/learning/test_services.py) | 6/8=75%; exclui futuro/cancelado; figura 16 |
| RF-027 | [learning/services.py: save_student_project](../../src/apps/learning/services.py) | [learning/test_services.py](../../tests/learning/test_services.py) | Entrega/rascunho próprio; figura 26; tarefa A05-5 |
| RF-028 | [learning/services.py: review_student_project](../../src/apps/learning/services.py) | [learning/test_services.py](../../tests/learning/test_services.py) | Instrutor vinculado; figura 17 |
| RF-029 | [learning/services.py: save_evaluation](../../src/apps/learning/services.py) | [learning/test_services.py](../../tests/learning/test_services.py) | Nota 0–10/autoria/publicação; figura 18 |
| RF-030 | [learning/services.py: complete_class_group](../../src/apps/learning/services.py) | [learning/test_services.py](../../tests/learning/test_services.py) | 75%,6,entrega e pré-condições; figura 19 |
| RF-031 | [learning/services.py: issue_certificate](../../src/apps/learning/services.py) | [learning/test_services.py](../../tests/learning/test_services.py) | Aprovação/idempotência/carga; PDF real figura 29 |
| RF-032 | [learning/views.py: CertificateDetail/DownloadView](../../src/apps/learning/views.py) | [learning/test_views.py](../../tests/learning/test_views.py) | Titular/admin/instrutor vinculado, revogação; figuras 20/37 |
| RF-033 | [reporting/selectors.py: dashboard_snapshot](../../src/apps/reporting/selectors.py) | [reporting/test_selectors.py](../../tests/reporting/test_selectors.py) | Reconciliação por universo; figura 27 |
| RF-034 | [reporting/selectors.py: class_groups_for_user](../../src/apps/reporting/selectors.py) | [reporting/test_selectors.py](../../tests/reporting/test_selectors.py) | Turmas atribuídas ao instrutor |
| RF-035 | [reporting/forms.py + selectors.py: filter_class_groups](../../src/apps/reporting/forms.py) | [reporting/test_forms.py](../../tests/reporting/test_forms.py) | Oficina, status e período por início da turma |
| RF-036 | reporting/csv_exports.py e views.py | [reporting/test_views.py](../../tests/reporting/test_views.py) | Três CSV UTF-8 BOM ;, somente ADMIN; sem contato/documentos |
| RF-037 | core/models.py UUIDTimestampedModel; histórico/User | [learning/test_models.py](../../tests/learning/test_models.py) | created_at/updated_at e datas preservadas |
| RF-038 | [learning/models.py: recorded_by/evaluated_by](../../src/apps/learning/models.py) | [learning/test_services.py](../../tests/learning/test_services.py) | Correção/autoria e publicação |
| RF-039 | forms/views de todos os módulos; templates messages | [workshops/test_defect_regressions.py](../../tests/workshops/test_defect_regressions.py) | Entradas inválidas/mensagens; HTTP casos originais/reteste |
| RF-040 | people/models.py is_active; workshop ARCHIVED; admin guards | [people/test_views.py](../../tests/people/test_views.py) | Desativação/arquivamento e conservação; DELETE acadêmico bloqueado |

Em RF-004, gestão de outras contas é pelo Django admin com staff/permissões, não pelo papel funcional isoladamente; A01/A02 não executam essa gestão. RF-003 está tecnicamente implementado/testado, mas o backend console da candidata exige mediação para obter token e não entrega e-mail externo. RF-017 exige oferta aberta no momento real; o teste humano A05-I expira no horário registrado.

## Requisitos não funcionais e lacunas de mensuração

| RNF | Situação de evidência | Fonte/limite e ação |
|---|---|---|
| 001 responsividade | PARCIAL | 1440×1000/390×844 no manifest; sem overflow global, mas tabela móvel tem scroll interno. Observar fluxos reais/aparelhos e registrar essa exceção |
| 002 rótulos/erros | ATENDIDO no escopo inspecionado | Templates de form, labels e form.errors, testes forms/views, figuras 03/18/26/34; não substitui varredura universal |
| 003 feedback | ATENDIDO no escopo testado | messages success/error, HTML aria-live; matrizes HTTP e correções |
| 004 teclado/foco | PARCIAL | CSS focus, skip-link e roteiros Tab/Enter; falta execução completa por pessoa/tecnologia assistiva |
| 005 contraste AA | NÃO VERIFICADO | Sem relatório de medição de todas as combinações; realizar auditoria correspondente, não aprovar por aparência |
| 006 inscrição sem ajuda | PENDENTE | A05 com pessoa real, primeira tentativa e ajuda anotadas |
| 007 hash de senha | ATENDIDO | User/Django e test_create_user_normalizes_email_and_hashes_password; settings produção usa hash padrão, test usa MD5 somente isolado |
| 008 autenticação/autorização | ATENDIDO nos fluxos testados | mixins/queries/services e testes de negativas por URL/papel/vínculo |
| 009 CSRF/XSS/SQL/sessão | PARCIAL | Middleware, escape, ORM, HTTPS/cookies; testes CSRF/isolamento; não há auditoria ofensiva completa |
| 010 segredos fora do Git | ATENDIDO na revisão | .gitignore/produção por env, varredura contra segredos reais e PDFs; ver verificações documentais |
| 011 escopo de dados | ATENDIDO nos fluxos testados | RN-043/044, seletores e HTTP; ADMIN tem alcance global, não multi-tenant |
| 012 minimização | PARCIAL | CSV sem CPF/contato, dados fictícios e mascaramento; não é avaliação jurídica ou validação de processo de consentimento real |
| 013 HTTPS | ATENDIDO | TLS nos HTTP existentes e publicação/versão comprovadas |
| 014 autoria/data | ATENDIDO | Campos e correção/conclusão nos testes learning/enrollments; não promete trilha de todas as versões |
| 015 P95 50 simultâneos | NÃO VERIFICADO | Sem ensaio de carga com 50 usuários/base/parâmetros; tempos sequenciais não suprem |
| 016 paginação/filtros | PARCIAL | ListViews usam paginate_by=25 e filtros disponíveis; ofertas globais não têm busca e nem toda tela é ListView. Conferir exceções/volumes reais |
| 017 CSV 10 mil em 5s | NÃO VERIFICADO | Sem base de 10 mil/medição reproduzível; CSV funcional é evidência diferente |
| 018 atomicidade/vaga | ATENDIDO | atomic/select_for_update; teste concorrente PostgreSQL e cenário HTTP última vaga |
| 019 unicidade/FK | ATENDIDO | Migrations/constraints/CHECK e testes models; regras entre tabelas dependem de serviço, não somente SQL |
| 020 erro sem detalhes internos | ATENDIDO no escopo testado | DEBUG=False, respostas genéricas/erros de form; testes e HTTP, sem prova de todos os erros possíveis |
| 021 backup/restore | ATENDIDO no escopo documentado | Backup verificado e restore só em PostgreSQL descartável; não presume cópia externa/agendamento |
| 022 modularidade | ATENDIDO | Arquitetura, services/selectors/models; views simples também consultam ORM |
| 023 testes críticos | ATENDIDO | Idade, responsável, vagas/concorrência, frequência, nota, entrega e conclusão em testes de serviços |
| 024 CI PR | ATENDIDO | .github/workflows/ci.yml e runs #11/#12/develop aprovadas; PR documental tem CI própria |
| 025 dependências fixadas | ATENDIDO | pyproject.toml e uv.lock; sem alteração de biblioteca nesta auditoria |
| 026 instruções reproduzíveis | ATENDIDO | README, guia implantação/operação, guardas e checks; execução de testes sempre isolada |
| 027 Chrome/Edge/Firefox | NÃO VERIFICADO | Capturas Chromium/Playwright não provam duas últimas versões estáveis dos três navegadores |
| 028 fuso | ATENDIDO | USE_TZ=True, America/Sao_Paulo; datas-aware nos forms/PDFs/HTTP; prazo A05 explícito |
| 029 português | ATENDIDO nas telas inspecionadas | LANGUAGE_CODE=pt-br, labels/mensagens/templates e manual/capturas |

Estas lacunas não autorizam inventar resultados nem expandir funcionalidades. Mensurações e aceites restantes devem ser planejados isoladamente, com parâmetros e limitações; se não executados, declarar ao tutor. “Todos Must atendidos” não pode ser usado como conclusão integral enquanto esses RNF carecem de prova.
