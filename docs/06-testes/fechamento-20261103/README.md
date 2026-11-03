# Verificação do fechamento — 03/11/2026

Autoria: agente Codex. Candidato funcional `9f0fd32f0d57f97c953a1e39cb62b0b601d1aeb5`; banco PostgreSQL 17 efêmero, nome exclusivo de testes, sem portas publicadas e sem dados de produção. Navegador Chromium/Playwright por **HTTP loopback isolado**, sessões e CSRF nativos. Não é teste HTTPS da aplicação implantada nem aceite humano em aparelho real.

Suíte completa: **264 testes aprovados, zero falhas, zero skips, cobertura 90,54%**. A execução anterior de 262 testes/90,43% foi intermediária. Os resultados 235/89,84% e 41 testes de outubro são históricos, não os resultados desta branch.

Ruff lint/format, Django check, makemigrations --check --dry-run e sintaxe JS aprovados. Nenhuma migration nova. [Formulários e fluxos](../../07-avaliacoes/fechamento-20261103/README.md) explica a classificação dos achados.

[Larguras](verificacao-visual.json): 96 combinações (44 base / 52 candidato), 320/390/768/1440px; base teve duas com transbordamento, candidato zero. Os controles nativos da base mostraram data vazia, CPF/telefone preenchidos; no candidato, três preenchidos. Não foram simulados problemas de CPF/telefone que não ocorreram.

[Fluxos do navegador](fluxos-navegador.json): **12 aprovados**, incluindo formulário inválido, persistência, provisionamento/vínculo de instrutor, descoberta/cadastro de turma por A02 sem staff, confirmação do cancelamento, vagas antes da confirmação e CSV real com status honesto. A01 também conferido em 320px. São testes instrumentais; não provam usabilidade, toque, contraste AA ou todos os navegadores.

Capturas em [capturas](capturas/) usam exclusivamente dados fictícios locais. O fixture inicial por ORM foi preparação, não tarefa executada por um avaliador. Os scripts de execução e logs completos ficam restritos; um primeiro seletor amplo de formulário foi corrigido no executor antes da rodada consolidada, sem classificá-lo como defeito da aplicação.

Sem escrita no banco publicado, exclusão de certificados, merge, deploy ou promoção para main. Para gravar usando a URL pública, integrar e publicar uma versão aprovada e repetir os fluxos críticos por HTTPS antes de anunciar essas melhorias como publicadas.
