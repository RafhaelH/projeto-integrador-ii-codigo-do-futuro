# Publicação e retestes — 03/11/2026

PR [#14](https://github.com/RafhaelH/projeto-integrador-ii-codigo-do-futuro/pull/14) integrada por squash em develop: **`10210ad7bc9c995c90207fa1c2dce6c546d217f6`**. Imagem publicada **`sha256:8bcc8d37eb5b397eaf2695286904b6f065bdd8176253733a2b1f775e88816bd3`**. Os 124 arquivos Python/HTML/CSS/JS conferidos no contêiner correspondem ao checkout integrado. App em 127.0.0.1:8031; banco sem porta pública. main preservada.

CI do HEAD da PR e [CI pós-merge](https://github.com/RafhaelH/projeto-integrador-ii-codigo-do-futuro/actions/runs/41742825072) aprovadas. Suíte PostgreSQL: **264 testes, zero skips, cobertura 90,54%**. Não há migrations novas. O deploy usou o script existente e somente o projeto Compose codigo-do-futuro.

## Evidências publicadas

- Health, readiness e login: HTTP 200 por HTTPS com TLS validado.
- [24 verificações registradas](retestes.json): PUB-01–19 e cinco perfis. Sessões independentes, CSRF nativo; senhas/cookies não capturados. Instrumentação do agente, sem atribuir resultados a avaliadores humanos.
- PUB-03–05: valores existentes de nascimento/CPF/telefone no novo participante fictício; POST inválido mantém valores sem gravar; edição de nome preserva os demais e consentimento vazio.
- PUB-06–09: provisionamento apenas INSTRUCTOR, sem staff/superusuário/grupos; cadastro/vínculo de turma pelo A02 e confirmação de cancelamento. Somente a turma nova foi cancelada.
- PUB-10–13: obrigatórios/mensagem PT-BR; frequência, revisão e avaliação acadêmica nos registros fictícios exclusivos.
- PUB-14–17: capacidade/ocupação antes da confirmação, pendentes/espera separados, três CSV e PDF recebidos pelo navegador. Status da interface diz somente “Download solicitado”. Certificado existente consultado, sem emissão/revogação/exclusão.
- Perfis A01–A05 e novo instrutor: leituras e negativas de autorização esperadas; cinco identificadores de sessão distintos conferidos em memória.
- [24 combinações publicadas](layout.json): oito telas em 320/390/1440px, sem overflow horizontal externo, menus visíveis. [Ação de tabela em 320px](acao-tabela-mobile.json) acessível após rolagem interna, sem clicar na ação.
- [12 rotas estáveis para o vídeo](cenarios-video.json), somente leitura: pessoas/vínculo, oficina, fila, acompanhamento, revisão/avaliação, conclusão, certificado e jornada própria.
- [Manifest de capturas](capturas.json) e [PNG](capturas/): páginas realmente renderizadas; máscaras de identificação declaradas. Não é verificação em aparelho físico, todos os navegadores ou certificação AA.

O primeiro executor de negativas esperava um elemento main na página padrão 403; ajustado o executor para ler body, sem correção da aplicação e sem classificar o timeout instrumental como defeito do produto. Escritas já aprovadas não foram repetidas na retomada. As 52 combinações e 12 fluxos anteriores permanecem evidências isoladas em [fechamento](../fechamento-20261103/README.md); não são novamente contados como retestes da publicação.

## Preservação e rollback

Backup pelo script do projeto, diretório restrito novo sem remover backups antigos; catálogo com 193 entradas e SHA-256 verificado. Dump e plano operacional somente na cópia restrita. Imagem anterior preservada por ID/tag para rollback de código; sem migrations novas, não se prevê restauração do banco para esse rollback.

**Zero alterações em registros de negócio preexistentes e zero exclusões.** Foram criados 19 registros fictícios exclusivos da rodada, inventariados privadamente. Somente last_login das contas utilizadas mudou nos registros anteriores. Cenários de apresentação e certificados de simulação antigos preservados. 73 contêineres de outros projetos sem alteração de ID/imagem/início/restarts/portas; banco deste projeto preservou o ID. Nginx/certificados/configuração global e main permaneceram inalterados.

## Complemento após HUM-005

[15 leituras específicas de A05](reteste-A05-HUM005.json), início/inscrições/certificados/jornada/ofertas em 320/390/1440, sem overflow externo; cinco capturas. Somente consulta, sem alteração de registros de negócio. O dispositivo/navegador/versão da sessão humana não foram informados; não se declara reprodução exata, causa ou aceite em aparelho físico. Esses dados são um complemento técnico aos resultados anteriores, não cinco novas opiniões nem substituição do relato.
