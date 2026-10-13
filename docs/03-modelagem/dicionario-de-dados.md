# Dicionário de dados implementado

Gerado por [gerar-inventario.py](gerar-inventario.py), com o Django fixado em `uv.lock`. A fonte é o código, sem consulta ou escrita no banco publicado. Veja [inventário completo](inventario-schema.json) e [banco físico](banco-fisico.md).

## Convenções

`NULL` é nulabilidade SQL; `blank` permite ausência na validação de formulário. Texto com blank=sim e NULL=não usa string vazia. PK e UNIQUE são restrições SQL; choices e validadores são regras Python, salvo CHECK explícito. Defaults, UUIDs e datas automáticas são preenchidos pelo Python, não defaults SQL permanentes. PROTECT/CASCADE indicam a política do coletor Django, não cláusulas ON DELETE equivalentes no PostgreSQL.

Há 16 modelos próprios persistentes; core possui base abstrata e reporting não possui tabelas. As tabelas do framework e as associações de autorização também estão listadas. `django_migrations` é mantida pelo executor de migrations (id bigint, app varchar(255), name varchar(255), applied timestamptz, todos NOT NULL; id PK), não por um modelo instalado.

## accounts_user

Modelo: `accounts.User`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `password` (password) | varchar(128) | não | não | — | MaxLengthValidator(128) |
| `last_login` (last_login) | timestamp with time zone | sim | sim | — | — |
| `is_superuser` (is_superuser) | boolean | não | não | — | default Python: False |
| `is_staff` (is_staff) | boolean | não | não | — | default Python: False |
| `is_active` (is_active) | boolean | não | não | — | default Python: True |
| `date_joined` (date_joined) | timestamp with time zone | não | não | — | default Python: django.utils.timezone.now |
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `email` (email) | varchar(254) | não | não | UNIQUE | EmailValidator(); MaxLengthValidator(254) |
| `full_name` (full_name) | varchar(150) | não | não | — | MaxLengthValidator(150) |
| `role` (role) | varchar(20) | não | não | — | MaxLengthValidator(20); choices: ADMIN, INSTRUCTOR, PARTICIPANT; default Python: PARTICIPANT |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |

Restrições explícitas do modelo:

- `<UniqueConstraint: expressions=(Lower(F(email)),) name='accounts_user_email_ci_unique'>`

Associação `groups`: tabela `accounts_user_groups`; id: bigint, NOT NULL, PK identity; user_id: uuid, NOT NULL, FK → accounts_user.id, INDEX, ORM CASCADE; group_id: integer, NOT NULL, FK → auth_group.id, INDEX, ORM CASCADE. PK id; FKs com índice; UNIQUE (('user', 'group'),).

Associação `user_permissions`: tabela `accounts_user_user_permissions`; id: bigint, NOT NULL, PK identity; user_id: uuid, NOT NULL, FK → accounts_user.id, INDEX, ORM CASCADE; permission_id: integer, NOT NULL, FK → auth_permission.id, INDEX, ORM CASCADE. PK id; FKs com índice; UNIQUE (('user', 'permission'),).

## auth_group

Modelo: `auth.Group`. Infraestrutura Django.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | integer | não | sim | PK | MinValueValidator(-2147483648); MaxValueValidator(2147483647); identity SQL |
| `name` (name) | varchar(150) | não | não | UNIQUE | MaxLengthValidator(150) |

Associação `permissions`: tabela `auth_group_permissions`; id: bigint, NOT NULL, PK identity; group_id: integer, NOT NULL, FK → auth_group.id, INDEX, ORM CASCADE; permission_id: integer, NOT NULL, FK → auth_permission.id, INDEX, ORM CASCADE. PK id; FKs com índice; UNIQUE (('group', 'permission'),).

## auth_permission

Modelo: `auth.Permission`. Infraestrutura Django.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | integer | não | sim | PK | MinValueValidator(-2147483648); MaxValueValidator(2147483647); identity SQL |
| `name` (name) | varchar(255) | não | não | — | MaxLengthValidator(255) |
| `content_type_id` (content_type) | integer | não | não | INDEX; FK → django_content_type.id; ORM CASCADE | — |
| `codename` (codename) | varchar(100) | não | não | — | MaxLengthValidator(100) |

Unicidade composta SQL: `[('content_type', 'codename')]`.

## django_admin_log

Modelo: `admin.LogEntry`. Infraestrutura Django.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | integer | não | sim | PK | MinValueValidator(-2147483648); MaxValueValidator(2147483647); identity SQL |
| `action_time` (action_time) | timestamp with time zone | não | não | — | default Python: django.utils.timezone.now |
| `object_id` (object_id) | text | sim | sim | — | — |
| `object_repr` (object_repr) | varchar(200) | não | não | — | MaxLengthValidator(200) |
| `action_flag` (action_flag) | smallint | não | não | — | MinValueValidator(0); MaxValueValidator(32767); choices: 1, 2, 3 |
| `change_message` (change_message) | text | não | sim | — | — |
| `content_type_id` (content_type) | integer | sim | sim | INDEX; FK → django_content_type.id; ORM SET_NULL | — |
| `user_id` (user) | uuid | não | não | INDEX; FK → accounts_user.id; ORM CASCADE | — |

## django_content_type

Modelo: `contenttypes.ContentType`. Infraestrutura Django.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | integer | não | sim | PK | MinValueValidator(-2147483648); MaxValueValidator(2147483647); identity SQL |
| `app_label` (app_label) | varchar(100) | não | não | — | MaxLengthValidator(100) |
| `model` (model) | varchar(100) | não | não | — | MaxLengthValidator(100) |

Unicidade composta SQL: `[('app_label', 'model')]`.

## django_session

Modelo: `sessions.Session`. Infraestrutura Django.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `session_key` (session_key) | varchar(40) | não | não | PK | MaxLengthValidator(40) |
| `session_data` (session_data) | text | não | não | — | — |
| `expire_date` (expire_date) | timestamp with time zone | não | não | INDEX | — |

## enrollments_enrollment

Modelo: `enrollments.Enrollment`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |
| `status` (status) | varchar(30) | não | não | — | MaxLengthValidator(30); choices: PENDING, CONFIRMED, WAITLISTED, REJECTED, CANCELLED, APPROVED, NOT_COMPLETED; default Python: PENDING |
| `status_reason` (status_reason) | text | não | sim | — | — |
| `waitlisted_at` (waitlisted_at) | timestamp with time zone | sim | sim | — | — |
| `confirmed_at` (confirmed_at) | timestamp with time zone | sim | sim | — | — |
| `cancelled_at` (cancelled_at) | timestamp with time zone | sim | sim | — | — |
| `class_group_id` (class_group) | uuid | não | não | INDEX; FK → workshops_classgroup.id; ORM PROTECT | — |
| `created_by_id` (created_by) | uuid | não | não | INDEX; FK → accounts_user.id; ORM PROTECT | — |
| `participant_id` (participant) | uuid | não | não | INDEX; FK → people_participant.id; ORM PROTECT | — |

Restrições explícitas do modelo:

- `<UniqueConstraint: fields=('participant', 'class_group') name='enrollments_participant_class_unique'>`

Índices explícitos:

- `<Index: fields=['class_group', 'status', 'created_at'] name='enrollments_class_status_idx'>`
- `<Index: fields=['class_group', 'status', 'waitlisted_at'] name='enrollments_waitlist_idx'>`

## enrollments_enrollmentstatushistory

Modelo: `enrollments.EnrollmentStatusHistory`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | bigint | não | sim | PK | MinValueValidator(-9223372036854775808); MaxValueValidator(9223372036854775807); identity SQL |
| `from_status` (from_status) | varchar(30) | sim | sim | — | MaxLengthValidator(30); choices: PENDING, CONFIRMED, WAITLISTED, REJECTED, CANCELLED, APPROVED, NOT_COMPLETED |
| `to_status` (to_status) | varchar(30) | não | não | — | MaxLengthValidator(30); choices: PENDING, CONFIRMED, WAITLISTED, REJECTED, CANCELLED, APPROVED, NOT_COMPLETED |
| `reason` (reason) | text | não | sim | — | — |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `changed_by_id` (changed_by) | uuid | não | não | INDEX; FK → accounts_user.id; ORM PROTECT | — |
| `enrollment_id` (enrollment) | uuid | não | não | INDEX; FK → enrollments_enrollment.id; ORM CASCADE | — |

## learning_attendance

Modelo: `learning.Attendance`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |
| `status` (status) | varchar(20) | não | não | — | MaxLengthValidator(20); choices: PRESENT, ABSENT, JUSTIFIED |
| `note` (note) | varchar(255) | não | sim | — | MaxLengthValidator(255) |
| `enrollment_id` (enrollment) | uuid | não | não | INDEX; FK → enrollments_enrollment.id; ORM PROTECT | — |
| `meeting_id` (meeting) | uuid | não | não | INDEX; FK → workshops_meeting.id; ORM PROTECT | — |
| `recorded_by_id` (recorded_by) | uuid | não | não | INDEX; FK → accounts_user.id; ORM PROTECT | — |

Restrições explícitas do modelo:

- `<UniqueConstraint: fields=('enrollment', 'meeting') name='learning_attendance_enrollment_meeting_unique'>`

Índices explícitos:

- `<Index: fields=['enrollment', 'status'] name='learning_att_enrollment_idx'>`
- `<Index: fields=['meeting', 'status'] name='learning_att_meeting_idx'>`

## learning_certificate

Modelo: `learning.Certificate`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |
| `verification_code` (verification_code) | varchar(40) | não | não | UNIQUE | MaxLengthValidator(40); default Python: apps.learning.models.generate_certificate_code |
| `issued_at` (issued_at) | timestamp with time zone | não | não | — | default Python: django.utils.timezone.now |
| `workload_hours` (workload_hours) | numeric(5, 2) | não | não | — | MinValueValidator(0); DecimalValidator() |
| `is_active` (is_active) | boolean | não | não | — | default Python: True |
| `revoked_at` (revoked_at) | timestamp with time zone | sim | sim | — | — |
| `revocation_reason` (revocation_reason) | text | não | sim | — | — |
| `enrollment_id` (enrollment) | uuid | não | não | UNIQUE; FK → enrollments_enrollment.id; ORM PROTECT | — |

Restrições explícitas do modelo:

- `<CheckConstraint: condition=(OR: (AND: ('is_active', True), ('revocation_reason', ''), ('revoked_at__isnull', True)), (AND: ('is_active', False), ('revoked_at__isnull', False), (NOT (AND: ('revocation_reason', ''))))) name='learning_certificate_revocation_state'>`

## learning_evaluation

Modelo: `learning.Evaluation`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |
| `final_score` (final_score) | numeric(3, 1) | não | não | — | MinValueValidator(0); MaxValueValidator(10); DecimalValidator() |
| `feedback` (feedback) | text | não | não | — | — |
| `published_at` (published_at) | timestamp with time zone | sim | sim | — | — |
| `enrollment_id` (enrollment) | uuid | não | não | UNIQUE; FK → enrollments_enrollment.id; ORM PROTECT | — |
| `evaluated_by_id` (evaluated_by) | uuid | não | não | INDEX; FK → accounts_user.id; ORM PROTECT | — |

Restrições explícitas do modelo:

- `<CheckConstraint: condition=(AND: ('final_score__gte', 0), ('final_score__lte', 10)) name='learning_evaluation_score_range'>`

## learning_studentproject

Modelo: `learning.StudentProject`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |
| `title` (title) | varchar(150) | não | não | — | MaxLengthValidator(150) |
| `description` (description) | text | não | não | — | — |
| `repository_url` (repository_url) | varchar(200) | não | sim | — | URLValidator(); MaxLengthValidator(200) |
| `demonstration_url` (demonstration_url) | varchar(200) | não | sim | — | URLValidator(); MaxLengthValidator(200) |
| `is_delivered` (is_delivered) | boolean | não | não | — | default Python: False |
| `delivered_at` (delivered_at) | timestamp with time zone | sim | sim | — | — |
| `review_notes` (review_notes) | text | não | sim | — | — |
| `enrollment_id` (enrollment) | uuid | não | não | UNIQUE; FK → enrollments_enrollment.id; ORM PROTECT | — |

## people_guardian

Modelo: `people.Guardian`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |
| `full_name` (full_name) | varchar(150) | não | não | — | MaxLengthValidator(150) |
| `phone` (phone) | varchar(11) | não | não | — | validate_phone; MaxLengthValidator(11) |
| `email` (email) | varchar(254) | não | sim | — | EmailValidator(); MaxLengthValidator(254) |
| `is_active` (is_active) | boolean | não | não | — | default Python: True |

## people_institution

Modelo: `people.Institution`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |
| `name` (name) | varchar(150) | não | não | — | MaxLengthValidator(150) |
| `document` (document) | varchar(14) | sim | sim | UNIQUE | validate_cnpj; MaxLengthValidator(14) |
| `contact_name` (contact_name) | varchar(150) | não | sim | — | MaxLengthValidator(150) |
| `contact_email` (contact_email) | varchar(254) | não | sim | — | EmailValidator(); MaxLengthValidator(254) |
| `contact_phone` (contact_phone) | varchar(11) | não | sim | — | validate_phone; MaxLengthValidator(11) |
| `address` (address) | varchar(255) | não | sim | — | MaxLengthValidator(255) |
| `is_active` (is_active) | boolean | não | não | — | default Python: True |

## people_instructor

Modelo: `people.Instructor`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |
| `biography` (biography) | text | não | sim | — | — |
| `specialties` (specialties) | varchar(255) | não | sim | — | MaxLengthValidator(255) |
| `is_active` (is_active) | boolean | não | não | — | default Python: True |
| `user_id` (user) | uuid | não | não | UNIQUE; FK → accounts_user.id; ORM PROTECT | — |

## people_participant

Modelo: `people.Participant`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |
| `full_name` (full_name) | varchar(150) | não | não | — | MaxLengthValidator(150) |
| `birth_date` (birth_date) | date | não | não | — | — |
| `cpf` (cpf) | varchar(11) | sim | sim | UNIQUE | validate_cpf; MaxLengthValidator(11) |
| `contact_email` (contact_email) | varchar(254) | não | sim | — | EmailValidator(); MaxLengthValidator(254) |
| `phone` (phone) | varchar(11) | não | sim | — | validate_phone; MaxLengthValidator(11) |
| `is_active` (is_active) | boolean | não | não | — | default Python: True |
| `privacy_consent_at` (privacy_consent_at) | timestamp with time zone | sim | sim | — | — |
| `image_authorization` (image_authorization) | boolean | não | não | — | default Python: False |
| `user_id` (user) | uuid | sim | sim | UNIQUE; FK → accounts_user.id; ORM PROTECT | — |

## people_participantguardian

Modelo: `people.ParticipantGuardian`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |
| `relationship` (relationship) | varchar(30) | não | não | — | MaxLengthValidator(30); choices: MOTHER, FATHER, LEGAL_GUARDIAN, OTHER |
| `is_primary` (is_primary) | boolean | não | não | — | default Python: False |
| `guardian_id` (guardian) | uuid | não | não | INDEX; FK → people_guardian.id; ORM PROTECT | — |
| `participant_id` (participant) | uuid | não | não | INDEX; FK → people_participant.id; ORM CASCADE | — |

Restrições explícitas do modelo:

- `<UniqueConstraint: fields=('participant', 'guardian') name='people_participant_guardian_unique'>`
- `<UniqueConstraint: fields=('participant',) name='people_participant_primary_guardian_unique' condition=(AND: ('is_primary', True))>`

## workshops_classgroup

Modelo: `workshops.ClassGroup`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |
| `code` (code) | varchar(30) | não | não | UNIQUE | MaxLengthValidator(30) |
| `title` (title) | varchar(150) | não | não | — | MaxLengthValidator(150) |
| `location` (location) | varchar(255) | não | não | — | MaxLengthValidator(255) |
| `capacity` (capacity) | integer | não | não | — | MinValueValidator(1); MaxValueValidator(2147483647) |
| `waitlist_enabled` (waitlist_enabled) | boolean | não | não | — | default Python: True |
| `registration_opens_at` (registration_opens_at) | timestamp with time zone | não | não | — | — |
| `registration_closes_at` (registration_closes_at) | timestamp with time zone | não | não | — | — |
| `start_date` (start_date) | date | não | não | — | — |
| `end_date` (end_date) | date | não | não | — | — |
| `status` (status) | varchar(30) | não | não | — | MaxLengthValidator(30); choices: PLANNED, OPEN, IN_PROGRESS, COMPLETED, CANCELLED; default Python: PLANNED |
| `created_by_id` (created_by) | uuid | não | não | INDEX; FK → accounts_user.id; ORM PROTECT | — |
| `institution_id` (institution) | uuid | sim | sim | INDEX; FK → people_institution.id; ORM PROTECT | — |
| `workshop_id` (workshop) | uuid | não | não | INDEX; FK → workshops_workshop.id; ORM PROTECT | — |

Restrições explícitas do modelo:

- `<CheckConstraint: condition=(AND: ('capacity__gt', 0)) name='workshops_capacity_gt_zero'>`

Índices explícitos:

- `<Index: fields=['workshop', 'status', 'start_date'] name='workshops_class_search_idx'>`

## workshops_classinstructor

Modelo: `workshops.ClassInstructor`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |
| `is_lead` (is_lead) | boolean | não | não | — | default Python: False |
| `assigned_at` (assigned_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `class_group_id` (class_group) | uuid | não | não | INDEX; FK → workshops_classgroup.id; ORM CASCADE | — |
| `instructor_id` (instructor) | uuid | não | não | INDEX; FK → people_instructor.id; ORM PROTECT | — |

Restrições explícitas do modelo:

- `<UniqueConstraint: fields=('class_group', 'instructor') name='workshops_class_instructor_unique'>`
- `<UniqueConstraint: fields=('class_group',) name='workshops_class_lead_unique' condition=(AND: ('is_lead', True))>`

## workshops_meeting

Modelo: `workshops.Meeting`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |
| `title` (title) | varchar(150) | não | não | — | MaxLengthValidator(150) |
| `description` (description) | text | não | sim | — | — |
| `starts_at` (starts_at) | timestamp with time zone | não | não | — | — |
| `ends_at` (ends_at) | timestamp with time zone | não | não | — | — |
| `status` (status) | varchar(20) | não | não | — | MaxLengthValidator(20); choices: PLANNED, COMPLETED, CANCELLED; default Python: PLANNED |
| `class_group_id` (class_group) | uuid | não | não | INDEX; FK → workshops_classgroup.id; ORM CASCADE | — |

Restrições explícitas do modelo:

- `<UniqueConstraint: fields=('class_group', 'starts_at') name='workshops_meeting_start_unique'>`
- `<CheckConstraint: condition=(AND: ('ends_at__gt', F(starts_at))) name='workshops_meeting_end_after_start'>`

Índices explícitos:

- `<Index: fields=['class_group', 'status', 'starts_at'] name='workshops_meeting_schedule_idx'>`

## workshops_workshop

Modelo: `workshops.Workshop`. Domínio do projeto.

| Coluna (campo) | Tipo PostgreSQL | NULL | blank | Chaves/índice | Regras e preenchimento |
|---|---|---|---|---|---|
| `id` (id) | uuid | não | não | PK | default Python: uuid.uuid4 |
| `created_at` (created_at) | timestamp with time zone | não | sim | — | auto_now_add |
| `updated_at` (updated_at) | timestamp with time zone | não | sim | — | auto_now |
| `title` (title) | varchar(150) | não | não | — | MaxLengthValidator(150) |
| `slug` (slug) | varchar(170) | não | não | UNIQUE | RegexValidator(); MaxLengthValidator(170) |
| `summary` (summary) | varchar(300) | não | não | — | MaxLengthValidator(300) |
| `objective` (objective) | text | não | não | — | — |
| `syllabus` (syllabus) | text | não | não | — | — |
| `estimated_hours` (estimated_hours) | numeric(5, 2) | não | não | — | MinValueValidator(0.01); DecimalValidator() |
| `status` (status) | varchar(20) | não | não | — | MaxLengthValidator(20); choices: DRAFT, PUBLISHED, ARCHIVED; default Python: DRAFT |
| `created_by_id` (created_by) | uuid | não | não | INDEX; FK → accounts_user.id; ORM PROTECT | — |

Índices explícitos:

- `<Index: fields=['status'] name='workshops_workshop_status_idx'>`

## Regras entre entidades e valores derivados

- Idade 14–21 no início e responsável ativo para menor na inscrição: people/enrollments services; não são CHECK SQL.
- Uma turma pode ter zero instrutores enquanto planejada; abrir/iniciar exige instrutor ativo e iniciar exige encontro planejado.
- Frequência liga inscrição e encontro da mesma turma: Attendance.clean e seleção do serviço. A FK isolada não verifica essa igualdade.
- Vagas operacionais contam CONFIRMED; painel histórico conta CONFIRMED/APPROVED/NOT_COMPLETED. Fila usa waitlisted_at, created_at e PK como desempate.
- Frequência usa PRESENT / encontros COMPLETED já terminados; JUSTIFIED não conta presença. Percentual é calculado, não coluna.
- Aprovação exige frequência ≥75%, nota ≥6 e projeto entregue; conclusão exige todos os encontros não cancelados processados e avaliações registradas.
- Certificate.enrollment_id é UNIQUE para todo o histórico: há no máximo um certificado por inscrição, mesmo revogado; o MVP não reemite revogado. workload_hours é snapshot na emissão; PDF usa nomes/dados relacionados na consulta, sem snapshot integral do cadastro.
- Histórico da inscrição é imutável pelos fluxos/admin; frequência/avaliação conservam última autoria/data, sem log de todas as versões.
- CPF/CNPJ opcionais são normalizados para NULL quando vazios e validados em Python; hashes de senha e sessões nunca são evidência pública.
