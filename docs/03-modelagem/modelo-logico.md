# Modelo lógico relacional

Derivado dos modelos e migrations atuais. Cardinalidades e dependências funcionais estão em [modelo-de-dados.md](modelo-de-dados.md). Tipos e nulabilidade: [dicionário](dicionario-de-dados.md).

Cada relação abaixo lista todas as colunas; PK/FK/UK são chaves físicas, não nomes conceituais fictícios.

## accounts_user

`accounts_user(password, last_login, is_superuser, is_staff, is_active, date_joined, id [PK], email [UK], full_name, role, created_at, updated_at)`

- Restrição: `<UniqueConstraint: expressions=(Lower(F(email)),) name='accounts_user_email_ci_unique'>`.

## enrollments_enrollment

`enrollments_enrollment(id [PK], created_at, updated_at, status, status_reason, waitlisted_at, confirmed_at, cancelled_at, class_group_id [FK], created_by_id [FK], participant_id [FK])`

- `class_group_id` → `workshops_classgroup.id`; obrigatória.
- `created_by_id` → `accounts_user.id`; obrigatória.
- `participant_id` → `people_participant.id`; obrigatória.
- Restrição: `<UniqueConstraint: fields=('participant', 'class_group') name='enrollments_participant_class_unique'>`.

## enrollments_enrollmentstatushistory

`enrollments_enrollmentstatushistory(id [PK], from_status, to_status, reason, created_at, changed_by_id [FK], enrollment_id [FK])`

- `changed_by_id` → `accounts_user.id`; obrigatória.
- `enrollment_id` → `enrollments_enrollment.id`; obrigatória.

## learning_attendance

`learning_attendance(id [PK], created_at, updated_at, status, note, enrollment_id [FK], meeting_id [FK], recorded_by_id [FK])`

- `enrollment_id` → `enrollments_enrollment.id`; obrigatória.
- `meeting_id` → `workshops_meeting.id`; obrigatória.
- `recorded_by_id` → `accounts_user.id`; obrigatória.
- Restrição: `<UniqueConstraint: fields=('enrollment', 'meeting') name='learning_attendance_enrollment_meeting_unique'>`.

## learning_certificate

`learning_certificate(id [PK], created_at, updated_at, verification_code [UK], issued_at, workload_hours, is_active, revoked_at, revocation_reason, enrollment_id [UK] [FK])`

- `enrollment_id` → `enrollments_enrollment.id`; obrigatória.
- Restrição: `<CheckConstraint: condition=(OR: (AND: ('is_active', True), ('revocation_reason', ''), ('revoked_at__isnull', True)), (AND: ('is_active', False), ('revoked_at__isnull', False), (NOT (AND: ('revocation_reason', ''))))) name='learning_certificate_revocation_state'>`.

## learning_evaluation

`learning_evaluation(id [PK], created_at, updated_at, final_score, feedback, published_at, enrollment_id [UK] [FK], evaluated_by_id [FK])`

- `enrollment_id` → `enrollments_enrollment.id`; obrigatória.
- `evaluated_by_id` → `accounts_user.id`; obrigatória.
- Restrição: `<CheckConstraint: condition=(AND: ('final_score__gte', 0), ('final_score__lte', 10)) name='learning_evaluation_score_range'>`.

## learning_studentproject

`learning_studentproject(id [PK], created_at, updated_at, title, description, repository_url, demonstration_url, is_delivered, delivered_at, review_notes, enrollment_id [UK] [FK])`

- `enrollment_id` → `enrollments_enrollment.id`; obrigatória.

## people_guardian

`people_guardian(id [PK], created_at, updated_at, full_name, phone, email, is_active)`


## people_institution

`people_institution(id [PK], created_at, updated_at, name, document [UK], contact_name, contact_email, contact_phone, address, is_active)`


## people_instructor

`people_instructor(id [PK], created_at, updated_at, biography, specialties, is_active, user_id [UK] [FK])`

- `user_id` → `accounts_user.id`; obrigatória.

## people_participant

`people_participant(id [PK], created_at, updated_at, full_name, birth_date, cpf [UK], contact_email, phone, is_active, privacy_consent_at, image_authorization, user_id [UK] [FK])`

- `user_id` → `accounts_user.id`; opcional.

## people_participantguardian

`people_participantguardian(id [PK], created_at, updated_at, relationship, is_primary, guardian_id [FK], participant_id [FK])`

- `guardian_id` → `people_guardian.id`; obrigatória.
- `participant_id` → `people_participant.id`; obrigatória.
- Restrição: `<UniqueConstraint: fields=('participant', 'guardian') name='people_participant_guardian_unique'>`.
- Restrição: `<UniqueConstraint: fields=('participant',) name='people_participant_primary_guardian_unique' condition=(AND: ('is_primary', True))>`.

## workshops_classgroup

`workshops_classgroup(id [PK], created_at, updated_at, code [UK], title, location, capacity, waitlist_enabled, registration_opens_at, registration_closes_at, start_date, end_date, status, created_by_id [FK], institution_id [FK], workshop_id [FK])`

- `created_by_id` → `accounts_user.id`; obrigatória.
- `institution_id` → `people_institution.id`; opcional.
- `workshop_id` → `workshops_workshop.id`; obrigatória.
- Restrição: `<CheckConstraint: condition=(AND: ('capacity__gt', 0)) name='workshops_capacity_gt_zero'>`.

## workshops_classinstructor

`workshops_classinstructor(id [PK], created_at, updated_at, is_lead, assigned_at, class_group_id [FK], instructor_id [FK])`

- `class_group_id` → `workshops_classgroup.id`; obrigatória.
- `instructor_id` → `people_instructor.id`; obrigatória.
- Restrição: `<UniqueConstraint: fields=('class_group', 'instructor') name='workshops_class_instructor_unique'>`.
- Restrição: `<UniqueConstraint: fields=('class_group',) name='workshops_class_lead_unique' condition=(AND: ('is_lead', True))>`.

## workshops_meeting

`workshops_meeting(id [PK], created_at, updated_at, title, description, starts_at, ends_at, status, class_group_id [FK])`

- `class_group_id` → `workshops_classgroup.id`; obrigatória.
- Restrição: `<UniqueConstraint: fields=('class_group', 'starts_at') name='workshops_meeting_start_unique'>`.
- Restrição: `<CheckConstraint: condition=(AND: ('ends_at__gt', F(starts_at))) name='workshops_meeting_end_after_start'>`.

## workshops_workshop

`workshops_workshop(id [PK], created_at, updated_at, title, slug [UK], summary, objective, syllabus, estimated_hours, status, created_by_id [FK])`

- `created_by_id` → `accounts_user.id`; obrigatória.
