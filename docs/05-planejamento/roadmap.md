# Roadmap de execução

O roadmap é orientado por dependências, não por datas fixas. As datas do cronograma acadêmico serão adicionadas assim que forem confirmadas no ambiente da faculdade.

| Fase | Entregas | Critério de saída |
|---|---|---|
| 0. Descoberta e especificação | visão, escopo, requisitos, regras, dados, arquitetura e backlog | documentos revisados e sem contradições críticas |
| 1. Fundação executável | Django, PostgreSQL, configurações, qualidade, CI e layout base | aplicação e testes executam localmente e na CI |
| 2. Acesso e pessoas | autenticação, permissões, participantes, responsáveis e instrutores | perfis isolados e regras de menor validadas |
| 3. Oferta educacional | oficinas, turmas, instrutores e encontros | cronograma válido e ciclo de estados protegido |
| 4. Inscrições | solicitações, análise, vagas, espera e cancelamento | concorrência testada e ocupação consistente |
| 5. Jornada acadêmica | frequência, projeto, avaliação, conclusão e certificado | turma completa processada de ponta a ponta |
| 6. Gestão | painéis, filtros, relatórios e dados de demonstração | números reconciliados com a base de teste |
| 7. Validação | testes técnicos, cinco avaliações e correções | nenhum erro crítico; decisões documentadas |
| 8. Entrega | manual, PDF de evidências, versão estável e vídeo | checklist acadêmico integralmente atendido |

Fases 0 a 5 possuem implementação versionada. Na fase 6, os painéis gerenciais por escopo,
filtros coerentes e relatórios CSV protegidos estão implementados. A carga fictícia de
demonstração encerra essa fase e prepara os testes com cinco avaliadores.

## Marcos

- **M1 — Especificação congelada:** fim da fase 0.
- **M2 — Primeiro fluxo utilizável:** participante e oficina cadastrados.
- **M3 — MVP operacional:** fim da fase 5.
- **M4 — Release candidata:** fim da fase 6.
- **M5 — Entrega acadêmica:** fim da fase 8.

## Controle de risco

| Risco | Impacto | Resposta |
|---|---|---|
| Escopo crescer durante o desenvolvimento | Alto | proteger itens Must e registrar novas ideias fora do MVP |
| Regras contraditórias | Alto | usar IDs e atualizar a matriz de rastreabilidade |
| Atraso na interface | Médio | adotar componentes simples e reutilizáveis |
| Falha na demonstração | Alto | seed determinística e roteiro ensaiado em ambiente publicado |
| Falta de avaliadores | Alto | convidar os cinco participantes antes da release candidata |
| Dados pessoais em evidências | Alto | usar personas e dados fictícios em screenshots e vídeo |
| Publicação tardia | Médio | validar implantação ainda na fase 3 |

## Registro de progresso

Cada fase deve terminar com:

1. uma versão executável;
2. testes aprovados;
3. evidências mínimas;
4. documentação atualizada;
5. commit ou pull request identificável.
