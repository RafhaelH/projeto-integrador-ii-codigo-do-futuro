# Código do Futuro

Projeto acadêmico desenvolvido para o **Projeto Integrador Transdisciplinar em Engenharia de Software II**.

A plataforma Código do Futuro apoiará a organização de oficinas gratuitas de programação e tecnologia, permitindo acompanhar participantes, responsáveis, instrutores, turmas, inscrições, encontros, frequência, projetos, avaliações, certificados e indicadores de resultado.

## Situação do projeto

O projeto está na fase de especificação e modelagem. A fundação documental foi criada antes da implementação para garantir rastreabilidade entre problema, requisitos, regras de negócio, código e testes.

## Objetivo

Centralizar a gestão das oficinas e substituir controles dispersos por um fluxo único, confiável e acessível, permitindo que administradores e instrutores acompanhem a jornada de cada participante e que os jovens consultem sua própria evolução.

## Escopo do MVP

- autenticação e recuperação de acesso;
- gerenciamento de usuários e perfis;
- participantes e responsáveis;
- instrutores e instituições parceiras;
- oficinas, turmas e encontros;
- inscrições, vagas e lista de espera;
- registro e consulta de frequência;
- projetos e avaliações dos participantes;
- conclusão e emissão de certificados;
- painel gerencial e relatórios básicos.

## Stack planejada

- Python e Django;
- PostgreSQL;
- templates Django, HTML, CSS e JavaScript;
- Bootstrap para a base responsiva da interface;
- Pytest para testes automatizados;
- GitHub Actions para integração contínua.

As versões serão fixadas quando a fundação executável for criada, utilizando versões oficialmente suportadas na data da implementação.

## Documentação

O índice completo está em [`docs/README.md`](docs/README.md).

Documentos centrais:

- [Visão do produto](docs/01-contexto/visao-do-produto.md)
- [Escopo](docs/01-contexto/escopo.md)
- [Requisitos funcionais](docs/02-requisitos/requisitos-funcionais.md)
- [Requisitos não funcionais](docs/02-requisitos/requisitos-nao-funcionais.md)
- [Regras de negócio](docs/02-requisitos/regras-de-negocio.md)
- [Matriz de permissões](docs/02-requisitos/matriz-permissoes.md)
- [Critérios de aceite e rastreabilidade](docs/02-requisitos/criterios-de-aceite.md)
- [Casos de uso](docs/03-modelagem/casos-de-uso.md)
- [Modelo de dados](docs/03-modelagem/modelo-de-dados.md)
- [Arquitetura](docs/04-arquitetura/arquitetura.md)
- [Backlog](docs/05-planejamento/backlog.md)
- [Plano de testes](docs/06-testes/plano-de-testes.md)
- [Checklist acadêmico](docs/09-entrega/checklist.md)

## Estratégia de branches

- `main`: versões estáveis e entregáveis;
- `develop`: integração do trabalho em andamento;
- `feat/<descricao>`: funcionalidades;
- `fix/<descricao>`: correções;
- `docs/<descricao>`: documentação.

## Origem acadêmica

O sistema evolui o projeto de extensão **Código do Futuro: Oficina de Programação e Tecnologia para Jovens**, realizado em Santa Rosa de Viterbo/SP com jovens de 14 a 21 anos. A experiência prática da oficina é utilizada como base para definir o problema, as funcionalidades e os critérios de acompanhamento da plataforma.

## Autor

Rafhael Henrique — Engenharia de Software.
