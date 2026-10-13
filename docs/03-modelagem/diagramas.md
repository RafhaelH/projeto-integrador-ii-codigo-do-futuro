# Diagramas revisados da implementação

Referência: código a351c5a/develop 644e7a6. Fontes versionáveis `.mmd`, blocos Mermaid e SVGs locais. Classes e sequências usam notação UML suportada pelo Mermaid; DER e fluxogramas são identificados como tais. Não se apresenta fluxograma como diagrama formal UML de casos de uso. O catálogo UC e seu mapa de atores estão em [casos-de-uso.md](casos-de-uso.md).

A revisão compara com código atual e os diagramas registrados no Integrador II; o protótipo e os diagramas originais do Integrador I não foram encontrados. Classes mostram atributos/métodos selecionados, sem inventar métodos de serviço dentro dos models. Relações autorais, Participant/Instructor/Institution externos à jornada e todos os campos constam no [modelo lógico](modelo-logico.md)/[dicionário](dicionario-de-dados.md); os dois DERs devem ser lidos juntos.

## Conceitual — pessoas e atribuições

[Fonte](diagramas/conceitual-pessoas.mmd) · [SVG legível](diagramas/conceitual-pessoas.svg)

```mermaid
erDiagram
    USER o|--o| PARTICIPANT : identifica
    USER ||--o| INSTRUCTOR : identifica
    PARTICIPANT ||--o{ PARTICIPANT_GUARDIAN : vincula
    GUARDIAN ||--o{ PARTICIPANT_GUARDIAN : responde
    INSTRUCTOR ||--o{ CLASS_INSTRUCTOR : ministra
    CLASS_GROUP ||--o{ CLASS_INSTRUCTOR : atribui
    INSTITUTION o|--o{ CLASS_GROUP : acolhe
```

## Conceitual — jornada

[Fonte](diagramas/conceitual-jornada.mmd) · [SVG legível](diagramas/conceitual-jornada.svg)

```mermaid
erDiagram
    WORKSHOP ||--o{ CLASS_GROUP : origina
    CLASS_GROUP ||--o{ MEETING : contem
    PARTICIPANT ||--o{ ENROLLMENT : solicita
    CLASS_GROUP ||--o{ ENROLLMENT : recebe
    ENROLLMENT ||--o{ ENROLLMENT_STATUS_HISTORY : registra
    ENROLLMENT ||--o{ ATTENDANCE : apura
    MEETING ||--o{ ATTENDANCE : recebe
    ENROLLMENT ||--o| STUDENT_PROJECT : entrega
    ENROLLMENT ||--o| EVALUATION : recebe
    ENROLLMENT ||--o| CERTIFICATE : identifica
```

## UML — classes de pessoas

[Fonte](diagramas/classes-pessoas.mmd) · [SVG legível](diagramas/classes-pessoas.svg)

```mermaid
classDiagram
    direction TB
    class User {
        UUID id
        string email
        string full_name
        string role
        bool is_active
        save()
        get_short_name()
    }
    class Participant {
        UUID id
        string full_name
        date birth_date
        string cpf
        bool is_active
        clean()
        save()
    }
    class Guardian {
        UUID id
        string full_name
        string phone
        bool is_active
        save()
    }
    class ParticipantGuardian {
        UUID id
        string relationship
        bool is_primary
    }
    class Instructor {
        UUID id
        string biography
        string specialties
        bool is_active
        clean()
    }
    class Institution {
        UUID id
        string name
        string document
        bool is_active
        save()
    }
    User "0..1" -- "0..1" Participant : user
    User "1" -- "0..1" Instructor : user
    Participant "1" -- "0..*" ParticipantGuardian
    Guardian "1" -- "0..*" ParticipantGuardian
```

## UML — classes acadêmicas

[Fonte](diagramas/classes-jornada.mmd) · [SVG legível](diagramas/classes-jornada.svg)

```mermaid
classDiagram
    direction TB
    class Workshop {
        UUID id
        string title
        string slug
        decimal estimated_hours
        string status
    }
    class ClassGroup {
        UUID id
        string code
        int capacity
        datetime registration_opens_at
        datetime registration_closes_at
        date start_date
        date end_date
        string status
        clean()
    }
    class ClassInstructor {
        UUID id
        bool is_lead
        datetime assigned_at
    }
    class Meeting {
        UUID id
        datetime starts_at
        datetime ends_at
        string status
        clean()
    }
    class Enrollment {
        UUID id
        string status
        string status_reason
        datetime waitlisted_at
        clean()
        delete()
    }
    class EnrollmentStatusHistory {
        bigint id
        string from_status
        string to_status
        string reason
        datetime created_at
    }
    class Attendance {
        UUID id
        string status
        string note
        clean()
    }
    class StudentProject {
        UUID id
        string title
        bool is_delivered
        datetime delivered_at
        clean()
    }
    class Evaluation {
        UUID id
        decimal final_score
        string feedback
        datetime published_at
    }
    class Certificate {
        UUID id
        string verification_code
        decimal workload_hours
        bool is_active
        datetime revoked_at
        clean()
        delete()
    }
    Workshop "1" -- "0..*" ClassGroup
    ClassGroup "1" -- "0..*" ClassInstructor
    ClassGroup "1" -- "0..*" Meeting
    ClassGroup "1" -- "0..*" Enrollment
    Enrollment "1" -- "0..*" EnrollmentStatusHistory
    Enrollment "1" -- "0..*" Attendance
    Meeting "1" -- "0..*" Attendance
    Enrollment "1" -- "0..1" StudentProject
    Enrollment "1" -- "0..1" Evaluation
    Enrollment "1" -- "0..1" Certificate
```

## UML — sequência de confirmação

[Fonte](diagramas/confirmacao.mmd) · [SVG legível](diagramas/confirmacao.svg)

```mermaid
sequenceDiagram
    actor A as Administrador
    participant V as EnrollmentConfirmView
    participant S as confirm_enrollment
    participant DB as PostgreSQL
    A->>V: POST com CSRF e inscrição
    V->>V: Autenticação e papel ADMIN
    V->>S: inscrição, actor, reason
    S->>DB: BEGIN, bloquear turma e inscrição
    DB-->>S: registros e ocupação CONFIRMED
    S->>S: Revalidar elegibilidade, vaga e ordem
    alt Válido
        S->>DB: UPDATE CONFIRMED, INSERT histórico
        S->>DB: COMMIT
        S-->>V: inscrição confirmada
        V-->>A: Redirect + mensagem de sucesso
    else Sem vaga, inelegível ou fora de ordem sem motivo
        S->>DB: ROLLBACK
        S-->>V: ValidationError
        V-->>A: Mensagem, dados preservados
    end
```

## UML — sequência de conclusão e emissão

[Fonte](diagramas/conclusao-certificado.mmd) · [SVG legível](diagramas/conclusao-certificado.svg)

```mermaid
sequenceDiagram
    actor A as Administrador
    participant V as CompleteClassGroupView
    participant S as Serviços learning
    participant E as IssueCertificateView
    participant DB as PostgreSQL
    A->>V: POST com CSRF
    V->>S: complete_class_group(turma, actor)
    S->>DB: BEGIN, bloquear turma, encontros e inscrições
    S->>S: IN_PROGRESS, encontros processados/past, avaliações completas
    alt Pré-condição falha
        S->>DB: ROLLBACK
        S-->>V: ValidationError
    else Pré-condições válidas
        loop Cada inscrição CONFIRMED
            S->>S: frequência >=75, nota >=6, projeto entregue
            S->>DB: APPROVED ou NOT_COMPLETED com motivos/histórico
        end
        S->>DB: Turma COMPLETED, COMMIT
        S-->>V: resumo
    end
    A->>E: POST de emissão com CSRF
    E->>S: issue_certificate(inscrição, actor)
    S->>DB: BEGIN, bloquear inscrição, buscar certificado
    alt Certificado ativo existente
        DB-->>S: reutilizar (idempotência)
        S->>DB: COMMIT
        S-->>E: certificado existente
    else Não existe
        S->>S: somar horas de encontros COMPLETED
        S->>DB: inserir código único, carga e emissão
        S->>DB: COMMIT
        S-->>E: novo certificado
    else Certificado revogado ou inscrição não aprovada
        S->>DB: ROLLBACK
        S-->>E: ValidationError, nenhuma emissão
    end
    E-->>A: Mensagem conforme resultado
```

## UML — sequência do perfil próprio

[Fonte](diagramas/perfil-proprio.mmd) · [SVG legível](diagramas/perfil-proprio.svg)

```mermaid
sequenceDiagram
    actor U as Usuário de qualquer papel
    participant V as OwnProfileView
    participant F as OwnProfileForm
    participant DB as PostgreSQL
    U->>V: GET /conta/perfil/
    V->>V: LoginRequired, alvo request.user
    V-->>U: Nome/e-mail, papel informativo
    U->>V: POST nome/e-mail + CSRF
    V->>F: validar obrigatórios/formato/unicidade
    alt Entrada inválida
        F-->>V: erros associados aos campos
        V-->>U: HTTP 200, sem alterações
    else Entrada válida
        V->>DB: BEGIN, UPDATE apenas full_name/email/updated_at
        alt Violação de UNIQUE concorrente
            DB-->>V: IntegrityError específica, ROLLBACK
            V-->>U: HTTP 200, e-mail já em uso
        else Salvo
            V->>DB: COMMIT
            V-->>U: Redirect + Seu perfil foi atualizado
        end
    end
```

## Atividade de inscrição (fluxograma)

[Fonte](diagramas/atividade-inscricao.mmd) · [SVG legível](diagramas/atividade-inscricao.svg)

```mermaid
flowchart TB
    Inicio([Solicitar]) --> Permissao{ADMIN ou titular?}
    Permissao -- Não --> Negado[Acesso negado]
    Permissao -- Sim --> Lock[Bloquear turma em transação]
    Lock --> Aberta{OPEN e dentro do prazo?}
    Aberta -- Não --> Erro[ValidationError e rollback]
    Aberta -- Sim --> Elegivel{Ativo, 14-21 no início e responsável quando menor?}
    Elegivel -- Não --> Erro
    Elegivel -- Sim --> Duplicada{Já tem inscrição?}
    Duplicada -- Sim --> Erro
    Duplicada -- Não --> Lotada{CONFIRMED >= capacidade?}
    Lotada -- Não --> Pendente[PENDING]
    Lotada -- Sim --> Fila{Espera habilitada?}
    Fila -- Não --> Pendente
    Fila -- Sim --> Espera[WAITLISTED e timestamp]
    Pendente --> Historico[Gravar inscrição e histórico]
    Espera --> Historico
    Historico --> Commit[Commit e mensagem de situação]
```

## Componentes e camadas

[Fonte](diagramas/camadas.mmd) · [SVG legível](diagramas/camadas.svg)

```mermaid
flowchart TB
    Browser[Navegador HTML e CSS] --> Router[URLs e middleware Django]
    Router --> View[Views e mixins de autorização]
    View --> Form[Forms]
    Form --> View
    View --> Service[Services: comandos e transações]
    View --> Selector[Selectors e consultas simples]
    Service --> Model[Models e ORM]
    Selector --> Model
    Model --> DB[(PostgreSQL)]
    View --> Template[Templates Django]
    Template --> Browser
    Router --> Console[Recuperação: backend console]
```

## Conferência dos fluxos

- Confirmação: enrollments/services.py confirm_enrollment/_confirm_locked e views; bloqueia turma antes da inscrição, preserva histórico, falha sem exceder vaga.
- Conclusão: learning/services.py complete_class_group/issue_certificate; professor pode avaliar, somente ADMIN conclui/emite. Falha de pré-condições não grava resultado parcial. Um certificado revogado não pode ser reemitido.
- Perfil: accounts/views.py OwnProfileView, forms e tests/accounts/test_profile.py; alvo definido pela sessão, whitelist, UNIQUE e CSRF.
- Solicitação: create_enrollment; duplicidade gera erro, não devolve silenciosamente um registro existente. A espera não confirma automaticamente uma nova solicitação.

Qualquer mudança de estado/regra deve atualizar fontes e renderizações. Os SVGs foram renderizados localmente com mermaid-cli 12.0.0; não requerem serviços de terceiros para leitura.
