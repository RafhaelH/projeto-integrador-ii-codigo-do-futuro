## Estado vigente após publicação — 03/11/2026

PR #14 integrada/publicada em `10210ad7bc9c995c90207fa1c2dce6c546d217f6`; [retestes HTTPS](../06-testes/publicacao-20261103/README.md). Quatro fontes humanas, data 03/11 confirmada, uma fonte distinta faltante. Vídeo: **PENDENTE — inserir após gravação**. Os blocos anteriores abaixo são históricos e não substituem o [relatório final](../09-entrega/relatorio-final.md).

# Registro de problemas e melhorias

Estado: **um relato humano recebido; quatro pendentes**. Achado humano e conferência técnica posterior estão separados abaixo. Não remover itens rejeitados; a justificativa faz parte da evidência acadêmica. Nenhuma opinião ou nota é completada por inferência.

## Tipos

- defeito funcional;
- segurança ou privacidade;
- usabilidade/acessibilidade;
- desempenho;
- sugestão de funcionalidade;
- documentação.

## Prioridade de tratamento

1. segurança, perda de dados e bloqueios;
2. requisitos Must incorretos;
3. dificuldades recorrentes entre avaliadores;
4. melhorias simples de alto impacto;
5. ideias fora do MVP para backlog futuro.

## Resumo final

| Indicador | Quantidade |
|---|---:|
| Achados recebidos |  |
| Implementados |  |
| Planejados para depois |  |
| Não aceitos |  |
| Defeitos críticos/altos abertos |  |

## Registro das sessões A01–A05

Estado: **um relato humano recebido, quatro pendentes**. HUM-001 é um relato recebido do estudante; a conferência técnica posterior não substitui sua confirmação.

| ID | Sessão/tarefa | Problema e resultado esperado | Evidência | Severidade | Decisão | Justificativa | Responsável/prazo | Correção/PR | Reteste |
|---|---|---|---|---|---|---|---|---|---|
| HUM-001 | A01; tela a confirmar | “Responsividade mobile quebra”; esperado uso sem corte/rolagem indevida | Print da conversa; original e nome restritos | a confirmar | Aceitar investigação/correção do problema reproduzido | Interface responsiva; confirmação do caso humano depende de tela/método/navegador | A confirmar; antes da rodada móvel definitiva | DEF-005 / candidato local 00ee7f9 | Publicação ainda sem correção; 4 verificações isoladas passaram |

Classificação: defeito, usabilidade, ideia ou fora do escopo. Decisão: corrigir agora, depois, não aceitar ou duplicado. Toda decisão precisa de justificativa; manter também resultados negativos e vínculo à ficha original.

## Distinção das correções técnicas

DEF-001/002/003 e cronologia da carga foram descobertas técnicas, documentadas na [consolidação dos testes](../06-testes/consolidacao-verificacao.md#três-defeitos-e-retestes). Não são feedback de colegas e não preencherão a tabela humana. Para cada sugestão real, ligar sessão/tarefa/evidência, decisão (aceitar, adiar, recusar, duplicada), justificativa, responsável, PR/commit e resultado/data/versão do reteste. Se não houver alteração pertinente, justificar; não implementar funcionalidade apenas para aparentar melhoria.


## Decisões técnicas de 19/10/2026 — separadas dos colegas

| ID | Origem comprovada | Decisão | Justificativa / situação |
|---|---|---|---|
| DEF-004 | Simulação renderizada A01-T03/A02-T03; valores nativos de datas vazios | Corrigir | RF-007/039, preservação de valores no formulário. Candidato local d1a5523, 41 testes isolados; implantação/reteste público pendentes |
| TEC-005 | Oferta A05-I fora de prazo | Manter por ser comportamento esperado | RN de janela de inscrição. Histórica preservada; alternativa SIM exclusiva utilizada, nova solicitação PENDING |
| TEC-006 | Pedido de contraste AA, aparelhos reais, carga e vários navegadores | Melhoria futura / verificação pendente | Chromium/viewport não comprovam essas metas; requer ensaio próprio e avaliação humana |
| TEC-007 | Usar cinco logins/simulações como cinco opiniões | Não aplicável | Enunciado exige pessoas distintas; sem fichas e sem autorização documentada do tutor, requisito continua pendente |
| EXEC-001/002/003 | Seletores/redirects do executor | Corrigir executor | Dois caminhos de certificado e um seletor de descrição; retestados, sem mudança funcional para esses três casos |

Detalhes, horários e evidências no [relatório das simulações](relatorio-simulacoes.md). Nenhum desses itens preenche a tabela reservada às sugestões humanas.


## DEF-005 — achado técnico relacionado ao tema de HUM-001

Decisão: **corrigir**. Em 24 verificações de leitura por HTTPS, 22 não apresentaram transbordamento da página e duas reproduziram largura 435px em viewports 320/390 na lista de participantes. O rótulo acessível “Ações”, posicionado absolutamente, tinha o body como referência. Acrescentar `position: relative` apenas a `.table-shell` mantém esse rótulo contido, preservando a rolagem interna da tabela e sua acessibilidade. Candidato `00ee7f9`, sobre d1a5523, aprovado em quatro larguras com ações acessíveis por teclado; não implantado. A correspondência com a falha humana permanece a confirmar, sem atribuir essa tela à pessoa. [Método e evidências](revisao-humana-20261019/README.md).


## Atualização de 03/11/2026

Novos relatos e decisões: DEF-004/005/006, UX-007 a UX-014 e DATA-015 estão no [fechamento de 03/11/2026](fechamento-20261103/README.md), com observação, reprodução, causa, decisão e reteste separados. Não houve limpeza publicada.
