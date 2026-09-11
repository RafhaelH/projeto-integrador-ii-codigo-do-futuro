# Dicionário de dados

## Convenções

- Identificadores principais: UUID.
- Datas e horários: armazenados com fuso; apresentação em `America/Sao_Paulo`.
- Textos curtos: `varchar`; textos longos: `text`.
- Entidades principais possuem `created_at` e `updated_at`.
- `RESTRICT` impede remoção de uma referência com histórico; `CASCADE` remove apenas registros estritamente dependentes antes de existir histórico acadêmico.

## user

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| email | varchar(254) | Sim | único; identificador de acesso normalizado |
| password | varchar(128) | Sim | hash gerenciado pelo Django |
| full_name | varchar(150) | Sim | nome de exibição |
| role | varchar(20) | Sim | `ADMIN`, `INSTRUCTOR` ou `PARTICIPANT` |
| is_active | boolean | Sim | padrão verdadeiro |
| is_staff | boolean | Sim | controle administrativo técnico |
| last_login | datetime | Não | último acesso bem-sucedido |
| created_at | datetime | Sim | criação |
| updated_at | datetime | Sim | última alteração |

## participant

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| user_id | uuid | Não | FK única para `user`; permite cadastro sem acesso inicial |
| full_name | varchar(150) | Sim | nome civil/social usado na operação |
| birth_date | date | Sim | base da elegibilidade |
| cpf | varchar(11) | Não | único quando informado; armazenado sem máscara |
| contact_email | varchar(254) | Não | contato quando ainda não há usuário |
| phone | varchar(20) | Não | telefone do participante |
| is_active | boolean | Sim | padrão verdadeiro |
| privacy_consent_at | datetime | Não | registro do aceite aplicável |
| image_authorization | boolean | Sim | padrão falso |
| created_at | datetime | Sim | criação |
| updated_at | datetime | Sim | última alteração |

## guardian

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| full_name | varchar(150) | Sim | nome do responsável |
| phone | varchar(20) | Sim | contato principal |
| email | varchar(254) | Não | contato alternativo |
| is_active | boolean | Sim | padrão verdadeiro |
| created_at | datetime | Sim | criação |
| updated_at | datetime | Sim | última alteração |

## participant_guardian

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| participant_id | uuid | Sim | FK para `participant` |
| guardian_id | uuid | Sim | FK para `guardian` |
| relationship | varchar(30) | Sim | mãe, pai, tutor ou outro |
| is_primary | boolean | Sim | responsável principal |
| created_at | datetime | Sim | criação |

Restrição única: `(participant_id, guardian_id)`.

## instructor

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| user_id | uuid | Sim | FK única para `user` com papel instrutor |
| biography | text | Não | apresentação curta |
| specialties | varchar(255) | Não | especialidades para o MVP |
| is_active | boolean | Sim | padrão verdadeiro |
| created_at | datetime | Sim | criação |
| updated_at | datetime | Sim | última alteração |

## institution

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| name | varchar(150) | Sim | nome da instituição |
| document | varchar(14) | Não | CNPJ sem máscara e único quando informado |
| contact_name | varchar(150) | Não | pessoa de contato |
| contact_email | varchar(254) | Não | e-mail institucional |
| contact_phone | varchar(20) | Não | telefone institucional |
| address | varchar(255) | Não | endereço de referência |
| is_active | boolean | Sim | padrão verdadeiro |
| created_at | datetime | Sim | criação |
| updated_at | datetime | Sim | última alteração |

## workshop

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| title | varchar(150) | Sim | nome da oficina |
| slug | varchar(170) | Sim | único; usado em URL amigável |
| summary | varchar(300) | Sim | resumo público |
| objective | text | Sim | objetivo pedagógico |
| syllabus | text | Sim | conteúdo previsto |
| estimated_hours | decimal(5,2) | Sim | maior que zero |
| status | varchar(20) | Sim | `DRAFT`, `PUBLISHED`, `ARCHIVED` |
| created_by_id | uuid | Sim | FK para `user` administrador |
| created_at | datetime | Sim | criação |
| updated_at | datetime | Sim | última alteração |

## class_group

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| workshop_id | uuid | Sim | FK `RESTRICT` para `workshop` |
| institution_id | uuid | Não | FK `RESTRICT` para `institution` |
| code | varchar(30) | Sim | código único da turma |
| title | varchar(150) | Sim | identificação da edição |
| location | varchar(255) | Sim | local presencial |
| capacity | positive_integer | Sim | maior que zero |
| waitlist_enabled | boolean | Sim | padrão verdadeiro |
| registration_opens_at | datetime | Sim | início das inscrições |
| registration_closes_at | datetime | Sim | fim das inscrições |
| start_date | date | Sim | início das atividades |
| end_date | date | Sim | fim das atividades |
| status | varchar(30) | Sim | `PLANNED`, `OPEN`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED` |
| created_by_id | uuid | Sim | FK para `user` administrador |
| created_at | datetime | Sim | criação |
| updated_at | datetime | Sim | última alteração |

## class_instructor

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| class_group_id | uuid | Sim | FK para `class_group` |
| instructor_id | uuid | Sim | FK para `instructor` |
| is_lead | boolean | Sim | indica instrutor principal |
| assigned_at | datetime | Sim | data da atribuição |

Restrição única: `(class_group_id, instructor_id)`.

## meeting

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| class_group_id | uuid | Sim | FK para `class_group` |
| title | varchar(150) | Sim | tema do encontro |
| description | text | Não | conteúdo e observações |
| starts_at | datetime | Sim | início |
| ends_at | datetime | Sim | fim posterior ao início |
| status | varchar(20) | Sim | `PLANNED`, `COMPLETED`, `CANCELLED` |
| created_at | datetime | Sim | criação |
| updated_at | datetime | Sim | última alteração |

Restrição única: `(class_group_id, starts_at)`.

## enrollment

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| participant_id | uuid | Sim | FK `RESTRICT` para `participant` |
| class_group_id | uuid | Sim | FK `RESTRICT` para `class_group` |
| status | varchar(30) | Sim | `PENDING`, `CONFIRMED`, `WAITLISTED`, `REJECTED`, `CANCELLED`, `APPROVED`, `NOT_COMPLETED` |
| status_reason | text | Não | obrigatório em rejeição, exceção ou cancelamento administrativo |
| waitlisted_at | datetime | Não | base para ordenar a fila |
| confirmed_at | datetime | Não | momento da confirmação |
| cancelled_at | datetime | Não | momento do cancelamento |
| created_by_id | uuid | Sim | FK para `user` que iniciou o registro |
| created_at | datetime | Sim | criação e desempate da solicitação |
| updated_at | datetime | Sim | última alteração |

Restrição única: `(participant_id, class_group_id)`.

## attendance

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| enrollment_id | uuid | Sim | FK para `enrollment` |
| meeting_id | uuid | Sim | FK para `meeting` da mesma turma |
| status | varchar(20) | Sim | `PRESENT`, `ABSENT`, `JUSTIFIED` |
| note | varchar(255) | Não | justificativa ou observação |
| recorded_by_id | uuid | Sim | FK para `user` autorizado |
| created_at | datetime | Sim | criação |
| updated_at | datetime | Sim | última alteração |

Restrição única: `(enrollment_id, meeting_id)`.

## student_project

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| enrollment_id | uuid | Sim | FK única para `enrollment` |
| title | varchar(150) | Sim | nome do projeto |
| description | text | Sim | problema e solução |
| repository_url | url | Não | repositório público ou autorizado |
| demonstration_url | url | Não | página ou demonstração |
| is_delivered | boolean | Sim | padrão falso |
| delivered_at | datetime | Não | preenchido quando entregue |
| review_notes | text | Não | devolutiva do instrutor |
| created_at | datetime | Sim | criação |
| updated_at | datetime | Sim | última alteração |

## evaluation

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| enrollment_id | uuid | Sim | FK única para `enrollment` |
| final_score | decimal(3,1) | Sim | entre 0,0 e 10,0 |
| feedback | text | Sim | devolutiva individual |
| evaluated_by_id | uuid | Sim | FK para `user` autorizado |
| published_at | datetime | Não | liberação para o participante |
| created_at | datetime | Sim | criação |
| updated_at | datetime | Sim | última alteração |

## certificate

| Campo | Tipo | Obrigatório | Restrições/descrição |
|---|---|---:|---|
| id | uuid | Sim | PK |
| enrollment_id | uuid | Sim | FK única para `enrollment` aprovada |
| verification_code | varchar(40) | Sim | único e não sequencial |
| issued_at | datetime | Sim | emissão |
| workload_hours | decimal(5,2) | Sim | carga calculada na emissão |
| is_active | boolean | Sim | permite revogação sem exclusão |
| revoked_at | datetime | Não | data da revogação |
| revocation_reason | text | Não | motivo da revogação |

## Campos derivados não persistidos

| Informação | Origem do cálculo |
|---|---|
| vagas ocupadas | inscrições confirmadas da turma |
| vagas disponíveis | capacidade menos vagas ocupadas |
| posição na espera | ordem por `waitlisted_at`, respeitando elegibilidade |
| frequência percentual | presenças divididas por encontros realizados |
| carga horária realizada | soma da duração dos encontros concluídos |
| elegibilidade para certificado | situação aprovada da inscrição |
