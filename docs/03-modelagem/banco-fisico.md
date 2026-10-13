# Banco físico, restrições e migrations

## Implementação verificável

SGBD publicado: PostgreSQL 17. Fontes: 16 models persistentes próprios, 7 migrations do projeto e migrations Django. Core/reporting não possuem tabelas próprias. O [inventário](inventario-schema.json) registra nomes físicos, campos, índices, constraints, dependências e SHA-256 das migrations. O [dicionário](dicionario-de-dados.md) inclui auth/admin/contenttypes/sessions e associações de autorização.

[schema-postgresql.sql](schema-postgresql.sql) contém 107 instruções de referência geradas **offline** pelo schema editor PostgreSQL a partir do estado final das migrations. São 24 tabelas de modelos/associações; `django_migrations`, criada pelo executor, é adicional. Não é dump nem inspeção de catálogo da VPS; não substitui migrate. O gerador bloqueia conexão e nenhum SQL foi executado nesta auditoria. A aplicação física por migrations isoladas é comprovada nas [evidências](../06-testes/consolidacao-verificacao.md).

## Migrations próprias

| Arquivo em src/apps | Conteúdo |
|---|---|
| accounts/migrations/0001_initial.py | User customizado, auth groups/permissions, e-mail único e Lower(email) único |
| people/migrations/0001_initial.py | Cinco entidades, CPF/CNPJ opcionais únicos e vínculos/responsável principal |
| workshops/migrations/0001_initial.py | Oficina, turma, instrutor e encontro; checks capacidade/duração e índices oferta/agenda |
| enrollments/migrations/0001_initial.py | Inscrição/histórico; unicidade participante/turma e índices de fila |
| learning/migrations/0001_initial.py | Frequência; unicidade inscrição/encontro e índices de situação |
| learning/migrations/0002_studentproject_evaluation.py | Projeto/avaliação 1:1 com inscrição; CHECK nota 0–10 |
| learning/migrations/0003_certificate.py | Certificado 1:1; código único; CHECK revogação |

Dependencies garantem criação de entidades antes das referências. Nenhuma nova migration foi criada. Para reproduzir instalação, usar banco local/CI expressamente isolado antes de migrate; não copiar comandos CI sobre production.env.

## Integridade no SQL

PKs próprias são UUID (default uuid.uuid4 em Python), exceto histórico com bigint identity. FKs/OneToOne criam referências e índices/uniques. FKs PostgreSQL são deferrable initially deferred; on_delete=PROTECT/CASCADE é política do coletor Django, **não** ON DELETE RESTRICT/CASCADE no SQL gerado. Participant.user é opcional; Instructor.user obrigatório.

| Proteção | Identificador/implementação |
|---|---|
| E-mail sem diferença de caixa | accounts_user_email_ci_unique, além de UNIQUE email |
| Responsável por participante único e um principal | people_participant_guardian_unique; índice parcial people_participant_primary_guardian_unique |
| Instrutor por turma único e um principal | workshops_class_instructor_unique; índice parcial workshops_class_lead_unique |
| Capacidade >0 | workshops_capacity_gt_zero; PositiveIntegerField também impõe domínio não negativo |
| Início único/fim posterior no encontro | workshops_meeting_start_unique; workshops_meeting_end_after_start |
| Participante/turma único | enrollments_participant_class_unique |
| Inscrição/encontro único | learning_attendance_enrollment_meeting_unique |
| Nota 0–10 | learning_evaluation_score_range |
| Projeto/avaliação/certificado por inscrição | UNIQUE enrollment_id; certificado inclusive revogado |
| Códigos únicos | Certificate.verification_code, Workshop.slug, ClassGroup.code |
| Revogação coerente | learning_certificate_revocation_state: ativo sem data/motivo; inativo com data e motivo não vazio |

## Índices implementados

Além de PK/UNIQUE/FK e parciais: workshops_workshop_status_idx(status); workshops_class_search_idx(workshop_id,status,start_date); workshops_meeting_schedule_idx(class_group_id,status,starts_at); enrollments_class_status_idx(class_group_id,status,created_at); enrollments_waitlist_idx(class_group_id,status,waitlisted_at); learning_att_enrollment_idx(enrollment_id,status); learning_att_meeting_idx(meeting_id,status). Nomes automáticos constam no SQL; não são apenas planejados.

## Regras fora do SQL

Choices não geram CHECK de enumeração. Form/model validators verificam CPF/CNPJ/telefone, datas, carga estimada positiva, mesma turma na frequência e data da entrega; save não chama full_clean automaticamente. Serviços validam autorização, idade/responsável, prazo, vagas/fila, estados, aprovação e emissão. Limite entre inscrições exige bloqueio/transação, não CHECK por linha. Não atribuir ao banco garantias que dependem desses fluxos.

## Reprodução documental

Na raiz, `.venv/bin/python docs/03-modelagem/gerar-inventario.py` gera inventário, dicionário, modelo lógico e SQL sem conexão. `DATABASE_URL=sqlite:///:memory: DJANGO_SETTINGS_MODULE=config.settings.test .venv/bin/python src/manage.py makemigrations --check --dry-run` confere models/migrations fora da publicação. As migrations históricas ficam intactas, com somas no inventário.
