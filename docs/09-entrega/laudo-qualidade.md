# Laudo técnico de qualidade — parecer condicionado

## Objeto e natureza

Código do Futuro, aplicação web Python/Django e PostgreSQL. Base documental 58db4fc, publicação a351c5a reconfirmada em 19/10/2026 por 122 hashes. Autoria desta verificação: agente Codex, a pedido do estudante; não é laudo assinado por cinco colegas nem certificação de segurança/acessibilidade. Identificação pessoal do estudante fica na cópia de entrega fora do Git.

## Três defeitos históricos e retestes comprovados

| ID | Descoberta e correção técnica | Evidência / resultado |
|---|---|---|
| DEF-001 | Encontro com início duplicado retornava 500. MeetingForm e tratamento atômico da constraint específica passaram a informar erro útil | cccfa6e / PR #11; R-08 e tests/workshops/test_defect_regressions.py. HTTP 200 com mensagem, dados preservados |
| DEF-002 | RF-006 não tinha perfil próprio. Criados view/form/rota/template com alvo request.user e whitelist nome/e-mail | R-18–R-21 e tests/accounts/test_profile.py: papéis, CSRF, privilégios/campos alheios, duplicidade/race |
| DEF-003 | Admin permitia concluir turma sem registros acadêmicos. Campos readonly e POSTs/inlines forjados bloqueados; fluxo canônico obrigatório | R-22–R-24, regressões de admin e completion: transição indevida rejeitada; conclusão canônica validada |

Fontes preservadas: [consolidação histórica](../06-testes/consolidacao-verificacao.md), [defeitos originais](../06-testes/validacao-publicada/VALIDATION-20261013-120621/defeitos.md), [reteste](../06-testes/correcoes-publicadas/RETEST-20261013-130005/relatorio.md). Descobertos na validação técnica; não atribuídos a pessoas avaliadoras.

## Evidência quantitativa e novo achado

Histórico: 235 testes, zero skip e cobertura 89,84% em PostgreSQL isolado; [CI de develop 58db4fc](https://github.com/RafhaelH/projeto-integrador-ii-codigo-do-futuro/actions/runs/38471294257) confirmada. Reteste anterior: 25 cenários HTTP consolidados, 278 verificações/465 requisições; preparação anterior: 57 verificações/81 requisições. São universos diferentes, não somar como cenários novos.

Em 19/10: [39 tarefas por perfil](../07-avaliacoes/relatorio-simulacoes.md), 37 aprovadas e duas reprovadas pelo único DEF-004, mais cinco reexecuções de diagnóstico/continuação. Chromium real verifica renderização básica; viewport móvel não é aceite humano. Novo defeito: datas localizadas esvaziam controles HTML5 e bloqueiam edição simples. Gravidade média; a correção é necessária antes da rodada que dependa dessa edição.

Candidato local d1a5523: dez widgets ISO, dez regressões reproduzidas antes, 41 testes direcionados aprovados em SQLite isolado e conferência nativa de dez campos no Chromium. Não houve CI remota desta branch nem implantação; não atribuir a ela a cobertura histórica. Requer revisão/integração/implantação autorizadas posteriores e reteste no publicado.

## Parecer e pendências

O MVP tem implementação, testes e correções históricas demonstráveis. **Parecer condicionado, não aprovação integral:** DEF-004 permanece publicado; cinco avaliações humanas, PDF de opiniões, decisões humanas e vídeo ainda não foram comprovados. Modelo AVA e documentos originais I dependem dos arquivos efetivamente disponibilizados. SMTP externo, carga/escala, versões exigidas de navegadores e auditoria completa de acessibilidade não estão aprovados.

Preservação: backup verificado antes das alterações, 57 registros fictícios novos rastreáveis e nenhum registro preexistente de negócio alterado/excluído. Autenticação modifica last_login das contas usadas. Produção não foi reimplantada. Reavaliar o parecer somente com evidências finais e versão identificada.
