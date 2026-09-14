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
- [ADR 0001 — Monólito modular Django](04-arquitetura/adr/0001-monolito-modular-django.md)

## 5. Planejamento

- [Backlog priorizado](05-planejamento/backlog.md)
- [Roadmap](05-planejamento/roadmap.md)

## 6. Qualidade

- [Plano de testes](06-testes/plano-de-testes.md)
- [Dados de demonstração](06-testes/dados-de-demonstracao.md)
- [Modelo de caso de teste](06-testes/modelo-caso-de-teste.md)

## 7. Avaliação com usuários

- [Plano de avaliação](07-avaliacoes/plano-de-avaliacao.md)
- [Formulário de avaliação](07-avaliacoes/formulario-de-avaliacao.md)
- [Registro de melhorias](07-avaliacoes/registro-de-melhorias.md)

## 8. Manual

- [Estrutura do manual do usuário](08-manual/README.md)

## 9. Entrega acadêmica

- [Checklist completo](09-entrega/checklist.md)

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
