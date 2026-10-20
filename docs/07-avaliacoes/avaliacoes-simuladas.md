# Quatro avaliações técnicas simuladas por perfil

Preparadas a pedido do estudante em 19/10/2026 (São Paulo), a partir de testes já executados. **São quatro perfis simulados pelo mesmo agente Codex, não quatro pessoas.** Um relato humano A01 permanece identificado separadamente na cópia privada. Não foram criados nomes, assinaturas, opiniões de terceiros ou notas de satisfação.

O modelo oficial pede cinco colegas; a substituição por simulações não foi confirmada pelo tutor. Esta versão apresenta a alternativa declaradamente, mantendo AC-14/15 parciais. Não transforma os testes em cinco avaliações humanas.

**Recorte:** A02–A05, 31 tarefas existentes, 30 aprovadas e uma reprovada (A02-T03/DEF-004). São um subconjunto das 39 tarefas originais, sem novas execuções ou contagem adicional de cenários.

Método e evidências: [39 tarefas originais](simulacoes-20261019/tarefas.json), [CSV](simulacoes-20261019/matriz-tarefas.csv), [relatório técnico](relatorio-simulacoes.md) e [dados desta síntese](quatro-perfis-simulados.json). As datas abaixo são horários dos testes do agente; não datas de participação de terceiros.

## SIM-A02 — Administrador funcional — gestão e conclusão

Autoria: agente Codex. Natureza: simulação técnica. Conta A02; sem avaliador humano. Janela dos registros: 2026-10-19T20:25:30.520968-03:00 a 2026-10-19T20:28:54.648644-03:00. Esse intervalo não é duração de uma sessão humana.

**O que funcionou:** Login e perfil por teclado; consulta de fila; frequência e projeto SIM; feedback mantendo nota 8; conclusão da turma SIM, certificado de 2h e idempotência; painel/CSV; perfil em viewport móvel e logout.

**O que não funcionou / resultado:** A02-T03 REPROVADO: editar somente autorização de imagem foi bloqueado pela data nativa vazia (DEF-004). Candidato d1a5523 existe, sem reteste público de correção.

**Correção ou sugestão técnica:** Recomendação técnica: integrar/retestar o candidato de datas antes de uma rodada que dependa da edição; manter mensagem clara e preservar dados. A falha inicial de navegação do certificado foi do executor e está corrigida no reteste.

**Não testado e limites:** Cadastro/cancelamento de inscrições não foram executados por este perfil nessa rodada; a fila foi somente consultada. Testes de carga, outros navegadores, toque em aparelho físico, satisfação e acessibilidade completa não foram avaliados.

| Tarefa | Objetivo | Resultado |
|---|---|---|
| A02-T01 | Entrar e reconhecer perfil | APROVADO |
| A02-T02 | Consultar Meu perfil por teclado | APROVADO |
| A02-T03 | Consultar/editar participante fictício exclusivo | REPROVADO |
| A02-T04 | Interpretar vagas/fila de Robótica em consulta | APROVADO |
| A02-T05 | Inspecionar frequência/projeto e revisar feedback da avaliação SIM | APROVADO |
| A02-T06 | Concluir turma SIM e emitir certificado uma vez | APROVADO |
| A02-T07 | Consultar painel e exportar CSV | APROVADO |
| A02-T08 | Explorar início/perfil em viewport móvel e sair | APROVADO |

## SIM-A03 — Instrutor — chamada e acompanhamento

Autoria: agente Codex. Natureza: simulação técnica. Conta A03; sem avaliador humano. Janela dos registros: 2026-10-19T20:25:33.941878-03:00 a 2026-10-19T20:26:38.686061-03:00. Esse intervalo não é duração de uma sessão humana.

**O que funcionou:** Login/perfil por teclado; turma e cronograma atribuídos; chamada de um encontro SIM e frequência de 100%; devolutiva de projeto; avaliação acadêmica fictícia de nota 8 publicada; painel próprio; restrições de acesso a Pessoas e turma alheia; chamada móvel em leitura e logout.

**O que não funcionou / resultado:** Nenhum defeito novo foi observado nas oito tarefas deste recorte. Isso não comprova ausência de defeitos no sistema. Pessoas retornou 403 e turma alheia 404, como esperado para o papel.

**Correção ou sugestão técnica:** Recomendação técnica: manter a separação por turma e conferir persistência de presença/devolutiva/nota ao alterar esses fluxos. Melhorias de clareza e usabilidade dependem de observação humana, sem nota inferida.

**Não testado e limites:** Conclusão administrativa e emissão de certificado não foram executadas por este instrutor; botões ausentes são restrição esperada. Outros navegadores, aparelhos físicos, carga e avaliação humana de usabilidade não foram testados.

| Tarefa | Objetivo | Resultado |
|---|---|---|
| A03-T01 | Entrar e reconhecer perfil | APROVADO |
| A03-T02 | Consultar Meu perfil por teclado | APROVADO |
| A03-T03 | Localizar turma e cronograma SIM | APROVADO |
| A03-T04 | Registrar chamada somente da turma SIM | APROVADO |
| A03-T05 | Revisar projeto SIM | APROVADO |
| A03-T06 | Cadastrar/publicar avaliação acadêmica fictícia SIM | APROVADO |
| A03-T07 | Observar limites de autorização | APROVADO |
| A03-T08 | Ler chamada em viewport móvel e sair | APROVADO |

## SIM-A04 — Instrutor — projetos, notas e permissões

Autoria: agente Codex. Natureza: simulação técnica. Conta A04; sem avaliador humano. Janela dos registros: 2026-10-19T20:25:36.924144-03:00 a 2026-10-19T20:26:48.935740-03:00. Esse intervalo não é duração de uma sessão humana.

**O que funcionou:** Login/perfil por teclado; acesso à sua turma SIM e cronograma; presença de 1/1 encontro e 100%; revisão de projeto e reabertura da devolutiva; nota 8 publicada em registro fictício; escopo do painel e negativas de permissão; leitura móvel da chamada e logout.

**O que não funcionou / resultado:** Nenhum defeito novo foi observado nas oito tarefas delimitadas. Negativas de acesso a dados de outro instrutor e Pessoas foram comportamento esperado. Não representa aprovação universal do produto.

**Correção ou sugestão técnica:** Recomendação técnica: preservar autoria, publicação de notas e isolamento dos vínculos ao evoluir o acompanhamento. Não converter a nota acadêmica fictícia 8 em satisfação de um avaliador.

**Não testado e limites:** Rotinas administrativas de pessoas, conclusão e emissão não fizeram parte do papel; não se considera falta de implementação. Não houve estudo humano de navegação, toque, carga ou auditoria completa de acessibilidade.

| Tarefa | Objetivo | Resultado |
|---|---|---|
| A04-T01 | Entrar e reconhecer perfil | APROVADO |
| A04-T02 | Consultar Meu perfil por teclado | APROVADO |
| A04-T03 | Localizar turma e cronograma SIM | APROVADO |
| A04-T04 | Registrar chamada somente da turma SIM | APROVADO |
| A04-T05 | Revisar projeto SIM | APROVADO |
| A04-T06 | Cadastrar/publicar avaliação acadêmica fictícia SIM | APROVADO |
| A04-T07 | Observar limites de autorização | APROVADO |
| A04-T08 | Ler chamada em viewport móvel e sair | APROVADO |

## SIM-A05 — Participante — inscrição, projeto e certificado

Autoria: agente Codex. Natureza: simulação técnica. Conta A05; sem avaliador humano. Janela dos registros: 2026-10-19T20:25:40.131845-03:00 a 2026-10-19T20:28:58.001957-03:00. Esse intervalo não é duração de uma sessão humana.

**O que funcionou:** Login/perfil por teclado; oferta histórica encerrada foi bloqueada pelo prazo; nova solicitação SIM ficou PENDING; jornada própria mostrou frequência integral; descrição e entrega do projeto SIM persistiram; certificado próprio existente de 2h foi consultado/baixado; jornada/ofertas em viewport móvel e logout.

**O que não funcionou / resultado:** Nenhum defeito da aplicação foi observado nas sete tarefas. A oferta antiga fora do prazo é comportamento esperado. A falha inicial de seletor da descrição era do executor e foi corrigida/retestada.

**Correção ou sugestão técnica:** Recomendação técnica: explicitar o prazo da oferta e a situação da solicitação; para nova rodada, consultar a situação existente ou preparar oferta exclusiva após backup. Não renovar a oferta histórica.

**Não testado e limites:** Cancelamento de inscrição, alteração de senha, fluxos de instrutor/admin, outros navegadores, aparelho físico e satisfação humana não foram avaliados neste recorte. Não presumir funcionalidades ausentes.

| Tarefa | Objetivo | Resultado |
|---|---|---|
| A05-T01 | Entrar e reconhecer perfil | APROVADO |
| A05-T02 | Consultar Meu perfil por teclado | APROVADO |
| A05-T03 | Conferir prazo histórico e solicitar somente na nova oferta SIM | APROVADO |
| A05-T04 | Interpretar jornada própria em consulta | APROVADO |
| A05-T05 | Atualizar e entregar somente projeto SIM | APROVADO |
| A05-T06 | Consultar/baixar certificado próprio existente em leitura | APROVADO |
| A05-T07 | Usar oferta/jornada em viewport móvel e sair | APROVADO |

Os candidatos de datas d1a5523 e layout móvel 00ee7f9 continuam identificados como locais, sem implantação nesta preparação. A verificação posterior de layout (24 leituras e quatro larguras isoladas) tem contagem separada e não foi atribuída a esses quatro perfis como nova execução.
