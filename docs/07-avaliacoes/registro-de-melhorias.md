# Registro de problemas e melhorias

Estado: **aguardando avaliação humana**. Este registro será preenchido após as sessões reais. Não remover itens rejeitados; a justificativa faz parte da evidência acadêmica. A tabela única abaixo reúne achados, decisões e retestes.

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

Estado: **aguardando avaliação humana**. Não há problemas humanos ou decisões preenchidos pela preparação técnica.

| ID | Sessão/tarefa | Problema e resultado esperado | Evidência | Severidade | Decisão | Justificativa | Responsável/prazo | Correção/PR | Reteste |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

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
