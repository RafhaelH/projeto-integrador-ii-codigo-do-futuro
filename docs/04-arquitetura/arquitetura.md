# Arquitetura implementada

## Estilo e versão

Monólito modular Django 5.2, Python 3.12, templates renderizados no servidor e PostgreSQL 17. Código `a351c5a`, cujo src é igual a develop `644e7a6`. A [ADR 0001](adr/0001-monolito-modular-django.md) conserva a decisão registrada; esta descrição usa os arquivos atuais.

## Camadas e relação MTV/MVC

| Responsabilidade | Arquivos reais | Relação arquitetural |
|---|---|---|
| Roteamento/controle | config/urls.py, apps/*/urls.py, middleware | Framework encaminha à view, aplica sessão/CSRF |
| Seleção de dados/coordenação | apps/*/views.py, accounts/mixins.py | View no Django; também coordena entrada, forms e serviços |
| Apresentação | src/templates/**/*.html, src/static/css/app.css | Template no MTV; apresentação equivalente à view em MVC |
| Entrada | apps/*/forms.py | Formatos, obrigatórios, whitelist e mensagens; não substitui autorização |
| Aplicação/domínio | people, workshops, enrollments, learning/services.py | Elegibilidade, transições, vagas, chamada, entrega, avaliação, conclusão, certificado |
| Consultas | learning/selectors.py, reporting/selectors.py e querysets nas views simples | Leituras por papel/vínculo, agregações/filtros |
| Persistência/invariantes | apps/*/models.py e migrations | Model MTV/MVC: entidades, validação local, ORM, constraints/índices |

A equivalência é de responsabilidades. A [FAQ oficial Django 5.2](https://docs.djangoproject.com/en/5.2/faq/general/#django-appears-to-be-a-mvc-framework-but-you-call-the-controller-the-view-and-the-view-the-template-how-come-you-don-t-use-the-standard-names) explica view como seleção de dados, template como apresentação e framework/roteamento como controle. Nesta aplicação, views também coordenam forms e serviços. Não há correspondência exata entre nomes de classes, microserviços ou API/SPA separada. Os fluxos atuais usam forms HTML e CSS; não há JavaScript próprio implementado nem necessidade de adicioná-lo para atender ao enunciado.

## Módulos e dependências

| Módulo | Responsabilidade implementada |
|---|---|
| accounts | User por e-mail, papéis, mixins, perfil próprio/admin; auth views Django para login/logout/redefinição |
| core | Base abstrata UUID/timestamps, início/saúde/prontidão e comandos de carga/arquivo restritos à operação |
| people | Participant, Guardian, ParticipantGuardian, Instructor, Institution; elegibilidade e documentos |
| workshops | Workshop, ClassGroup, ClassInstructor, Meeting; publicação, agenda, atribuições/estados |
| enrollments | Enrollment/histórico; solicitação, confirmação, espera, promoção, rejeição/cancelamento |
| learning | Attendance, StudentProject, Evaluation, Certificate; chamada/entrega/revisão/conclusão/PDF/revogação |
| reporting | Indicadores e três CSVs somente leitura; sem models/migrations próprios |

people usa accounts/core; workshops usa people/accounts; enrollments usa people/workshops; learning usa enrollments/workshops; reporting consulta esses domínios. UUIDTimestampedModel não cria tabela. Views simples consultam diretamente: não existe proibição absoluta de querysets na apresentação. Settings base/local/test/production, uv.lock e testes por domínio organizam configurações e bibliotecas.

## Transações, autorização e conservação

create/confirm/cancel/promote_enrollment bloqueiam turma/registros em transaction.atomic e recalculam ocupação. A unicidade participante/turma impede duplicidade. complete_class_group valida encontros não cancelados e avaliações, grava resultados/histórico e então transiciona. O Django admin usa readonly, rejeita POST forjado e encaminha aos serviços canônicos.

Papel/vínculo são conferidos no servidor; instrutor precisa de atribuição e participante acessa objetos próprios. ADMIN é papel funcional global; is_staff/superuser são privilégios distintos de /admin/. A01/A02 não os possuem. Perfil próprio usa request.user e whitelist nome/e-mail, sem editar dados acadêmicos ou privilégios.

CSRF, escape, ORM, senha/sessões Django e HTTPS compõem os controles; não equivalem a auditoria externa de segurança. Histórico conserva transições da inscrição; frequência/avaliação mantêm última autoria/data, sem log integral de versões. Certificados são revogados pela interface.

## Execução publicada

Navegador → HTTPS/Nginx → loopback 127.0.0.1:8031 → Gunicorn/Django → PostgreSQL em rede interna sem porta publicada. WhiteNoise serve estáticos e volumes conservam banco/mídia. Backend de e-mail é **console**; não está demonstrada entrega SMTP externa. O [guia VPS](implantacao-vps.md) descreve operação/backup/restauração; nenhuma implantação ocorreu nesta auditoria.

[Diagramas](../03-modelagem/diagramas.md) mostram camadas/fluxos reais e [banco físico](../03-modelagem/banco-fisico.md) separa garantias SQL de regras dos serviços. CI usa PostgreSQL isolado para lint, migrations, testes e smoke do empacotamento.
