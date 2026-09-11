# ADR 0001 — Monólito modular Django

- **Status:** aceito
- **Data:** 11/09/2026

## Contexto

O trabalho precisa entregar front-end, back-end, banco de dados, testes e documentação em um semestre. A solução será desenvolvida individualmente e deve ser fácil de demonstrar e manter.

## Decisão

Adotar Python, Django, templates renderizados no servidor e PostgreSQL, organizados como monólito modular. Regras de negócio mutáveis serão implementadas em serviços e consultas complexas em selectors.

## Motivos

- aderência à experiência do desenvolvedor;
- atendimento ao padrão MVC/MTV discutido no material acadêmico;
- autenticação, formulários, ORM e proteções web maduras;
- menor custo operacional que front-end e API separados;
- boa testabilidade e evolução incremental;
- prazo mais previsível para o MVP.

## Alternativas consideradas

### FastAPI com front-end separado

Oferece uma API moderna, mas adiciona autenticação distribuída, dois projetos, contratos HTTP e pipeline de build do front-end sem necessidade atual.

### Django REST Framework com SPA

É adequado para múltiplos clientes, mas o MVP possui apenas navegador web e não precisa pagar essa complexidade antecipadamente.

### Low-code/no-code

Pode acelerar protótipos, mas reduz o controle sobre regras, testes e evidências de arquitetura que enriquecem o trabalho acadêmico.

## Consequências

### Positivas

- uma única aplicação para desenvolver, testar e publicar;
- domínio centralizado;
- interface responsiva sem depender de uma SPA;
- infraestrutura simples.

### Negativas

- maior acoplamento da interface ao Django;
- uma API para aplicativo móvel exigiria trabalho adicional futuro;
- disciplina interna é necessária para o monólito não perder modularidade.

## Reavaliação

A decisão será revista apenas se surgir um cliente externo obrigatório, uma integração que exija API pública ou uma restrição acadêmica incompatível com a abordagem.
