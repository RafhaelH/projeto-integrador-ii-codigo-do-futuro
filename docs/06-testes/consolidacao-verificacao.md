# Consolidação de verificação, validação e melhorias

## Método e limites

Esta consolidação referencia resultados existentes conferidos em 13/10/2026, sem apagar ou reclassificar relatórios históricos. Nenhum pytest, migration, login ou requisição funcional foi executado contra o banco publicado nesta auditoria. Testes de Django com client são automatizados de views/integração, não navegadores reais. Scripts HTTP com contas fictícias são validação técnica, não opiniões de pessoas.

| Natureza / versão | Evidência aberta e conferida | Resultado e limite |
|---|---|---|
| Automatizados, candidata anterior | [evidências históricas](evidencias-automatizadas.md) | 189 aprovados e 1 reservado ao PostgreSQL na preparação local; manter contexto original |
| HTTP real, 00665be | [relatório original](validacao-publicada/VALIDATION-20261013-120621/relatorio.md), [matriz](validacao-publicada/VALIDATION-20261013-120621/matriz.csv) | 340 verificações registradas: 331 aprovadas, 4 reprovadas, 5 não executadas; 557 requisições. Inclui setup/repetição, **não 340 cenários distintos** |
| Automatizados, cccfa6e | [relatório de reteste](correcoes-publicadas/RETEST-20261013-130005/relatorio.md) | 225 aprovados, sem skip, PostgreSQL isolado; cobertura 89,11%; 127 direcionados precederam a suíte, não somar como testes novos |
| HTTP real, cccfa6e | [25 cenários consolidados](correcoes-publicadas/RETEST-20261013-130005/cenarios-consolidados.csv), [matriz](correcoes-publicadas/RETEST-20261013-130005/matriz.csv) | 25 cenários, 278 verificações aprovadas e 465 requisições; repetições/setup não multiplicam cenários |
| Automatizados, a351c5a | [log completo](preparacao-20261013/testes-automatizados.txt), [resumo](preparacao-20261013/verificacoes.json) | 235 aprovados, zero skip, cobertura 89,84%, PostgreSQL isolado; é total da suíte, não acréscimo aos 225 |
| HTTP real, a351c5a | [57 verificações](preparacao-20261013/http-checks.json), [81 requisições](preparacao-20261013/http-requests.json), [efeitos](preparacao-20261013/http-efeitos-persistidos.json) | Todas aprovadas com TLS/sessão/CSRF; 57 são verificações, não 57 cenários distintos; regressão dos três defeitos incluída |
| Inspeção visual, a351c5a | [manual e registro](../08-manual/plano-de-capturas.md), [manifest](../08-manual/capturas/manifest.json) | 38 imagens: 36 app (35 telas + scroll interno adicional), 1 CSV em visualizador local, 1 página do PDF real. Desktop 1440×1000/mobile 390×844; não demonstra compatibilidade com todos os navegadores nem acessibilidade AA |
| Simulações técnicas | [operação](preparacao-20261013/operacao.md), [relatório](preparacao-20261013/relatorio.md) | dry-run, restauração somente descartável, idempotência, preparação e tarefas com usuários fictícios; não contam como avaliações humanas |
| Avaliação humana | [cinco fichas](../07-avaliacoes/resultados/README.md) | **aguardando avaliação humana**; cinco colegas de curso/profissionais reais ainda precisam executar e opinar |

## Três defeitos e retestes

Fonte de descoberta: [defeitos originais](validacao-publicada/VALIDATION-20261013-120621/defeitos.md). Correções no commit cccfa6e, [PR #11](https://github.com/RafhaelH/projeto-integrador-ii-codigo-do-futuro/pull/11), preservadas em a351c5a.

| Defeito / antes | Causa e correção | Teste e depois |
|---|---|---|
| DEF-001 médio; HTTP-101/297: encontro duplicado → 500 | Unicidade composta não validada porque class_group omitido do form. MeetingForm verifica par; view atomic captura somente IntegrityError específico, mantendo constraint | tests/workshops/test_defect_regressions.py: duplicate_create, own_start/update, race/other_integrity; R-08: 200 com mensagem, sem mudanças; criação/edição válidas passam |
| DEF-002 alto; HTTP-260: RF-006 sem perfil próprio | Implementados OwnProfileView/Form, rota/template/menu; request.user, whitelist nome/e-mail, normalização/unique e tratamento de corrida | tests/accounts/test_profile.py: três papéis, anônimo, campos/terceiro forjados, CSRF, inválidos/race; R-18–R-21: edição/login atualizados e rejeições sem privilégio ou alteração alheia |
| DEF-003 alto; HTTP-320: Django admin PLANNED → COMPLETED sem registros acadêmicos | readonly e validação de POST/add/inlines antes de salvar; administração acadêmica só consulta; conclusão canônica obrigatória | tests/workshops/test_defect_regressions.py: admin_direct_transition/add/inline/processed_meeting; learning/test_services.py completion; R-22–R-24: fraude rejeitada com 200/403, edição legítima preservada; conclusão canônica 1 aprovado/3 não concluídos |

As quatro reprovações continuam no relatório original. São três defeitos porque DEF-001 teve duas reproduções. A preparação também corrigiu cronologia de inscrição fictícia de Robótica ([registro](preparacao-20261013/cronologia-robotica.json)); é ajuste técnico da carga, não sugestão humana.

## CI, banco e empacotamento

PR #11 integrado em 8924a6d, PR [#12](https://github.com/RafhaelH/projeto-integrador-ii-codigo-do-futuro/pull/12) em 644e7a6; ambos aprovados. [CI de develop 644e7a6](https://github.com/RafhaelH/projeto-integrador-ii-codigo-do-futuro/actions/runs/38442586075) concluída com sucesso, PostgreSQL 17, lint/formatação, checks/migrations, suíte, build e smoke. [CI do PR #12](https://github.com/RafhaelH/projeto-integrador-ii-codigo-do-futuro/actions/runs/38442202738) e [PR #11](https://github.com/RafhaelH/projeto-integrador-ii-codigo-do-futuro/actions/runs/38436232722) preservam os contextos. [Estado verificado](../09-entrega/estado-verificado.json) reconfirma código publicado a351c5a por 122 hashes, mesmo src de develop.

Backups/checksum/catálogo, restauração de cópia em banco descartável e remoção exata desse banco estão no [relatório de preparação](preparacao-20261013/relatorio.md). Não se declara restore na produção, cópia externa do backup ou rotina agendada que não esteja evidenciada.

## O que permanece sem aprovação

Cinco opiniões/PDF consolidado real, vídeo narrado e revisão após feedback. SMTP externo, ensaio de carga P95 com 50 usuários, relatório de 10 mil inscrições, compatibilidade nas versões exigidas de Chrome/Edge/Firefox, contraste AA e auditoria completa de teclado/acessibilidade não têm aprovação demonstrada. A [rastreabilidade](../02-requisitos/rastreabilidade-implementada.md) registra metas e lacunas sem transformá-las em resultados. Tempo de uma requisição sequencial não é medição de carga/usabilidade.
