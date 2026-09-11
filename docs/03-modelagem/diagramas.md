# Diagramas do sistema

Os diagramas são mantidos em Mermaid para permanecerem versionáveis e fáceis de atualizar conforme a implementação.

## Contexto

```mermaid
flowchart TB
    Participante[Participante]
    Instrutor[Instrutor]
    Admin[Administrador]
    Plataforma["Plataforma Código do Futuro"]
    Email[Serviço de e-mail]

    Participante -->|"inscrição e acompanhamento"| Plataforma
    Instrutor -->|"turmas e registros acadêmicos"| Plataforma
    Admin -->|"configuração e gestão"| Plataforma
    Plataforma -->|"recuperação de acesso"| Email
```

## Componentes lógicos

```mermaid
flowchart TB
    Browser[Navegador]
    Web["Django: views, forms e templates"]
    Domain["Serviços e regras de domínio"]
    Data["Models e selectors"]
    DB[(PostgreSQL)]

    Browser -->|HTTPS| Web
    Web --> Domain
    Domain --> Data
    Data --> DB
```

## Sequência: confirmação de inscrição

```mermaid
sequenceDiagram
    actor A as Administrador
    participant V as View
    participant S as EnrollmentService
    participant D as Banco

    A->>V: Confirmar inscrição
    V->>S: confirm(enrollment, actor)
    S->>D: Iniciar transação e bloquear turma
    D-->>S: Turma e ocupação atual
    S->>S: Validar permissão, elegibilidade e vaga
    S->>D: Atualizar situação e confirmed_at
    D-->>S: Confirmar transação
    S-->>V: Inscrição confirmada
    V-->>A: Exibir sucesso e ocupação
```

## Sequência: conclusão da turma

```mermaid
sequenceDiagram
    actor A as Administrador
    participant V as View
    participant S as CompletionService
    participant D as Banco

    A->>V: Concluir turma
    V->>S: complete(class_group, actor)
    S->>D: Carregar encontros e inscrições
    D-->>S: Frequências, projetos e avaliações
    S->>S: Aplicar RN-032 e RN-036
    S->>D: Gravar resultado de cada inscrição
    S->>D: Marcar turma como concluída
    D-->>S: Confirmar transação
    S-->>V: Resumo de aprovados e não concluintes
```

## Atividade: jornada da inscrição

```mermaid
flowchart TB
    Start([Início]) --> Open{Turma aberta?}
    Open -- Não --> Reject[Recusar solicitação]
    Open -- Sim --> Eligible{Participante elegível?}
    Eligible -- Não --> Reject
    Eligible -- Sim --> Duplicate{Já inscrito?}
    Duplicate -- Sim --> Existing[Mostrar inscrição existente]
    Duplicate -- Não --> Vacancy{Há vaga?}
    Vacancy -- Sim --> Pending[Criar inscrição pendente]
    Vacancy -- Não --> Waitlist{Lista habilitada?}
    Waitlist -- Sim --> Waiting[Inserir em lista de espera]
    Waitlist -- Não --> Pending
    Pending --> Review{Decisão administrativa}
    Review -- Confirmar --> Confirmed[Ocupar vaga]
    Review -- Rejeitar --> Rejected[Registrar motivo]
```

## Manutenção dos diagramas

Qualquer mudança em estados, atores ou limites dos módulos deve atualizar este arquivo e o documento relacionado antes da implementação.
