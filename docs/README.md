# Índice da documentação

Esta documentação é a fonte oficial das decisões do projeto. Cada requisito utiliza um identificador estável para permitir sua ligação com regras de negócio, casos de uso e testes.

## 1. Contexto

- [Visão do produto](01-contexto/visao-do-produto.md)
- [Escopo](01-contexto/escopo.md)

## 2. Requisitos

- [Requisitos funcionais](02-requisitos/requisitos-funcionais.md)
- [Requisitos não funcionais](02-requisitos/requisitos-nao-funcionais.md)
- [Regras de negócio](02-requisitos/regras-de-negocio.md)
- [Matriz de permissões](02-requisitos/matriz-permissoes.md)
- [Critérios de aceite e rastreabilidade](02-requisitos/criterios-de-aceite.md)
- [Glossário](02-requisitos/glossario.md)

## 3. Modelagem

- [Casos de uso](03-modelagem/casos-de-uso.md)
- [Modelo de dados](03-modelagem/modelo-de-dados.md)
- [Dicionário de dados](03-modelagem/dicionario-de-dados.md)
- [Diagramas](03-modelagem/diagramas.md)

## 4. Arquitetura

- [Arquitetura da solução](04-arquitetura/arquitetura.md)
- [Implantação na VPS](04-arquitetura/implantacao-vps.md)
- [ADR 0001 — Monólito modular Django](04-arquitetura/adr/0001-monolito-modular-django.md)

## 5. Planejamento

- [Backlog priorizado](05-planejamento/backlog.md)
- [Roadmap](05-planejamento/roadmap.md)

## 6. Qualidade

- [Plano de testes](06-testes/plano-de-testes.md)
- [Evidências automatizadas](06-testes/evidencias-automatizadas.md)
- [Dados de demonstração](06-testes/dados-de-demonstracao.md)
- [Modelo de caso de teste](06-testes/modelo-caso-de-teste.md)

## 7. Avaliação com usuários

- [Plano de avaliação](07-avaliacoes/plano-de-avaliacao.md)
- [Formulário de avaliação](07-avaliacoes/formulario-de-avaliacao.md)
- [Pacote das cinco avaliações](07-avaliacoes/pacote-de-avaliacao.md)
- [Registro de melhorias](07-avaliacoes/registro-de-melhorias.md)

## 8. Manual

- [Manual do usuário](08-manual/README.md)
- [Plano de capturas](08-manual/plano-de-capturas.md)

## 9. Entrega acadêmica

- [Checklist completo](09-entrega/checklist.md)
- [Plano de fechamento](09-entrega/plano-de-fechamento.md)
- [Relatório final — base](09-entrega/relatorio-final.md)
- [Roteiro do vídeo](09-entrega/roteiro-video.md)

## Padrão de identificação

| Prefixo | Artefato | Exemplo |
|---|---|---|
| RF | Requisito funcional | RF-014 |
| RNF | Requisito não funcional | RNF-006 |
| RN | Regra de negócio | RN-011 |
| UC | Caso de uso | UC-005 |
| CA | Critério de aceite | CA-014-02 |
| CT | Caso de teste | CT-014-03 |
| US | História de usuário | US-021 |

## Controle de mudanças

Mudanças que afetem comportamento devem atualizar, quando aplicável:

1. requisito funcional;
2. regra de negócio;
3. critério de aceite;
4. modelo de dados ou diagrama;
5. caso de teste;
6. manual do usuário.

## Auditoria acadêmica e estado atual

- [Índice de entrega para o tutor](09-entrega/README.md) e [matriz de conformidade](09-entrega/matriz-conformidade.md).
- [Rastreabilidade implementada](02-requisitos/rastreabilidade-implementada.md).
- [Modelo lógico](03-modelagem/modelo-logico.md), [banco físico](03-modelagem/banco-fisico.md) e inventário reproduzível.
- [Consolidação de testes/correções](06-testes/consolidacao-verificacao.md).
- [Interface e validações](08-manual/interface-e-validacoes.md).
- [Modelo PDF consolidado das cinco opiniões](07-avaliacoes/modelo-pdf-consolidado.md).
- [Relatório atual](09-entrega/relatorio-final.md) e [roteiro único 5:00](09-entrega/roteiro-video.md).

As cinco pessoas e o vídeo ainda são pendentes; contas e simulações não equivalem a resultados humanos.


## Preparação de entrega em 19/10/2026

A PR #13 foi integrada em develop 58db4fc. [Índice para o tutor](09-entrega/README.md), [simulações técnicas](07-avaliacoes/relatorio-simulacoes.md), [laudo](09-entrega/laudo-qualidade.md) e [roteiro definitivo do vídeo](08-manual/roteiro-video-final.md) registram o estado atual: 37/39 tarefas técnicas aprovadas, DEF-004 com correção local ainda não implantada, cinco avaliações humanas e vídeo pendentes. Simulações não equivalem a cinco pessoas. Novos commits desta tarefa permanecem locais.

Atualização após recebimento do modelo e print: modelo oficial preenchido parcialmente fora do Git; um relato humano identificado privadamente, quatro pendentes e lacunas explícitas. DEF-005 móvel reproduzido tecnicamente, candidato local 00ee7f9 sobre d1a5523, sem implantação.


Fechamento de 03/11/2026: [relatos/decisões](07-avaliacoes/fechamento-20261103/README.md), [testes](06-testes/fechamento-20261103/README.md) e [roteiro final 5:00](08-manual/roteiro-video-final.md). Candidato 9f0fd32 ainda aguarda revisão/integração/publicação; sem exclusão de dados publicados.
