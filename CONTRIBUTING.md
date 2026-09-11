# Guia de contribuição

## Fluxo de trabalho

1. Atualize a branch `develop`.
2. Crie uma branch curta a partir de `develop`.
3. Faça alterações pequenas e coesas.
4. Inclua ou atualize testes e documentação.
5. Abra um pull request para `develop`.
6. Use `main` apenas para versões estáveis.

## Convenção de commits

O projeto adota Conventional Commits:

- `feat:` nova funcionalidade;
- `fix:` correção de defeito;
- `docs:` alteração apenas documental;
- `test:` criação ou manutenção de testes;
- `refactor:` alteração interna sem mudar o comportamento;
- `chore:` manutenção de ferramentas ou configuração.

Exemplo: `docs: define requisitos e regras do MVP`.

## Critério de pronto

Uma entrega somente é considerada concluída quando:

- atende aos critérios de aceite;
- respeita as regras de negócio relacionadas;
- possui testes compatíveis com o risco;
- não introduz falhas nos testes existentes;
- atualiza a documentação afetada;
- não contém credenciais ou dados pessoais reais.
