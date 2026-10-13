# Modelo conceitual e normalização implementados

## Entidades e cardinalidades

Os [DERs e UML](diagramas.md) descrevem os 16 models próprios; [modelo lógico](modelo-logico.md) lista todas as colunas e chaves e [dicionário](dicionario-de-dados.md) os domínios físicos. User autentica; Participant descreve o jovem; Guardian é responsável; ParticipantGuardian associa os dois; Instructor é perfil de User; Institution é parceira; Workshop é oferta reutilizável; ClassGroup é edição; ClassInstructor atribui instrutor; Meeting é encontro; Enrollment é vínculo/jornada; EnrollmentStatusHistory registra transições; Attendance é presença; StudentProject é entrega; Evaluation é avaliação acadêmica; Certificate identifica conclusão.

| Relação | Cardinalidade real e condição |
|---|---|
| User–Participant | User 0..1 perfil; Participant 0..1 User (FK única anulável) |
| User–Instructor | User 0..1 perfil; Instructor exatamente 1 User |
| Participant–Guardian | N:N via ParticipantGuardian; par único e no máximo um principal; podem existir zero vínculos, mas menor elegível exige responsável ativo |
| Workshop–ClassGroup | Oficina 0..N turmas; turma exatamente 1 oficina |
| Institution–ClassGroup | Instituição 0..N turmas; turma 0..1 instituição |
| Instructor–ClassGroup | N:N via ClassInstructor; par único e no máximo um principal; turma planejada pode ter zero, abrir/iniciar exige ativo |
| ClassGroup–Meeting/Enrollment | Turma 0..N de cada; cada encontro/inscrição pertence exatamente a uma turma |
| Participant–Enrollment | Participante 0..N inscrições; cada inscrição exatamente um participante; par participante/turma único |
| Enrollment–History | Inscrição 0..N linhas no schema; serviços criam linha inicial e cada transição; histórico tem um ator obrigatório |
| Enrollment–Meeting | N:N para frequência via Attendance; par único e mesma turma verificada em Python |
| Enrollment–Project/Evaluation/Certificate | 0..1 de cada por inscrição; cada dependente exatamente 1 inscrição |
| User–registros autorais | 0..N registros por usuário; autoria obrigatória em oficinas/turmas/inscrições/histórico/frequência/avaliação |

Certificate.enrollment é único mesmo inativo: não há vários certificados históricos por inscrição nem reemissão após revogação. Role do usuário é distinto dos perfis acadêmicos; responsáveis não possuem login próprio.

## Modelo lógico e dependências funcionais

O [modelo relacional](modelo-logico.md) usa nomes físicos reais, não nomes singularizados hipotéticos. Todas as chaves alternativas, FKs, nulabilidade e constraints constam no inventário gerado. Dependências relevantes:

| Relação | Determinantes e separação |
|---|---|
| accounts_user | id → identidade/papel/flags/datas; email normalizado também identifica uma conta |
| people_participant/instructor | id → atributos locais; user_id não nulo identifica no máximo um perfil |
| people_participantguardian | id e (participant_id,guardian_id) → relationship/is_primary/datas; nomes/contatos ficam nas pessoas |
| workshops_workshop/classgroup | id e slug/code → atributos próprios; título/objetivo de oficina não se repetem nos encontros |
| workshops_classinstructor | id e (class_group_id,instructor_id) → atribuição; vínculo N:N sem lista multivalorada |
| enrollments_enrollment | id e (participant_id,class_group_id) → status/timestamps/ator; dados de pessoa/oficina são referenciados |
| enrollments_enrollmentstatushistory | id → inscrição, de/para, motivo, ator e instante; múltiplas transições não são colunas repetidas |
| learning_attendance | id e (enrollment_id,meeting_id) → status/note/ator/datas |
| learning_studentproject/evaluation/certificate | id e enrollment_id → atributos próprios; verification_code também identifica certificado |

## Justificativa de normalização

**1FN:** valores escalares por coluna; não há grupos de responsáveis, instrutores ou frequências em um campo. Biography/syllabus/specialties são textos livres, não tabelas ocultas com chaves relacionais. Associações possuem linhas independentes.

**2FN:** em ParticipantGuardian/ClassInstructor/Enrollment/Attendance, atributos dependem do par completo que forma a chave alternativa, e não de apenas uma pessoa/turma/encontro. Nomes e descrições dessas entidades são mantidos na tabela correspondente. PK substituta UUID não dispensa analisar os pares únicos.

**3FN:** não se copia institution.name na turma, workshop.title no encontro ou participant.birth_date na inscrição. FKs remetem à entidade que determina esses atributos. Projetos/avaliações são separados porque têm responsabilidades e ciclo próprios, não por exigir divisão arbitrária de toda tabela. Conforme as dependências documentadas, as relações visam 3FN; isso não é uma prova de ausência de qualquer redundância de negócio.

**Redundâncias intencionais/semântica temporal:** Participant.full_name e User.full_name atendem cadastro acadêmico e identidade de acesso, editados separadamente. Instructor referencia User para nome. confirmed_at/waitlisted_at/cancelled_at e histórico mantêm estado atual e trilha de eventos; serviços devem preservar coerência, sem alegar que status → uma data constante. Certificate.workload_hours conserva carga calculada na emissão: snapshot justificado, não contador livre. O PDF não armazena snapshot completo de nomes/títulos e os consulta dos cadastros. created/updated são metadados, não dados duplicados do domínio.

**Valores não persistidos:** vagas disponíveis/ocupadas, posição da fila, idade, percentual de presença e indicadores. Operação conta CONFIRMED para vaga; painel histórico conta também APPROVED/NOT_COMPLETED. Frequência individual exclui encontros futuros/cancelados; reporting agrega encontros marcados COMPLETED (sem filtro temporal adicional), diferença explícita do código, sem inventar um filtro universal.

## Estados e garantia de regras

Oficina: DRAFT → PUBLISHED → ARCHIVED. Turma: PLANNED → OPEN → IN_PROGRESS → COMPLETED, com cancelamento antes de concluída. Inscrição: criação PENDING ou WAITLISTED; PENDING → CONFIRMED/REJECTED/CANCELLED; WAITLISTED → CONFIRMED/CANCELLED; CONFIRMED → CANCELLED/APPROVED/NOT_COMPLETED. Serviços controlam transições; defaults/choices não são máquina de estados SQL.

Unicidade/CHECK/FKs/índices e limites dos validators estão no [banco físico](banco-fisico.md). A revisão não presume que o planejamento do Integrador I estivesse disponível.
