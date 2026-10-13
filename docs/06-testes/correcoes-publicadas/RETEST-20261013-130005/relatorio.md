# Correções e retestes — RETEST-20261013-130005

**Os três defeitos estão resolvidos, incluindo as duas falhas de severidade alta.
A candidata está tecnicamente pronta para iniciar as cinco avaliações humanas.** Essa conclusão
não substitui as avaliações nem comprova SMTP, usabilidade, responsividade ou acessibilidade.

Publicado em https://projeto-integrador.tesseratointegra.com.br, commit `cccfa6ee7fb13f0c428e8375dbed5b8a3a9e4fa1`,
branch `fix/validacao-publicada-20261013`, imagem `sha256:ffc5670680bfaafd39bac9c5690173d53743f901b26c9d99c69e82719ccaf993`. Os 119 arquivos de código/templates
do container foram comparados por SHA-256 com esse commit. App e PostgreSQL estão saudáveis;
`/healthz/`, `/readyz/` e `/entrar/` responderam 200 por HTTPS com TLS validado. App em
127.0.0.1:8031; banco sem porta publicada. Nginx, certificado, manifesto e ambiente permaneceram
idênticos por hash. Somente o container da aplicação foi substituído; o banco manteve seu ID.

## Histórico preservado

Referência: [validação original](../../validacao-publicada/VALIDATION-20261013-120621/relatorio.md),
commit `00665be5889ae639e9c1facec8be6c853f5895fa`.
Os 33 arquivos originais permanecem byte a byte iguais. As quatro reprovações históricas
HTTP-101, HTTP-260, HTTP-297, HTTP-320 permanecem REPROVADO naquela matriz. Os resultados abaixo são
uma nova execução, com contas e registros exclusivos. A reprodução HTTP **antes** é a evidência
original preservada, identificada por caso; não foi reclassificada como resultado desta versão.

## DEF-001 — MÉDIO — RESOLVIDO

- **Antes:** HTTP-101 e HTTP-297, POST de início duplicado retornava 500, com UniqueViolation na
  constraint `workshops_meeting_start_unique`; registro original preservado.
- **Causa:** MeetingForm omitia class_group, e a validação automática ignorava a unicidade
  composta. A constraint continuava ativa no banco.
- **Correção:** `src/apps/workshops/forms.py` verifica turma/início excluindo a própria instância;
  `views.py` salva dentro de atomic e captura a violação específica fora do savepoint. Outros
  IntegrityError continuam propagando. Não houve migration nem remoção da constraint.
- **Automatizados:** criação duplicada, edição com próprio início, alteração para início de
  outro encontro, disputa real por conexão independente em criação/edição e integridade alheia
  não mascarada: `tests/workshops/test_defect_regressions.py`.
- **Depois:** os dois POSTs HTTP de duplicidade retornaram 200 com mensagem útil e nenhuma
  alteração; criação e edição legítimas passaram. Ver cenário R-08 e matriz detalhada.

## DEF-002 — ALTO — RESOLVIDO (RF-006)

- **Antes:** HTTP-260, página inicial 200 sem acesso ao perfil; não havia endpoint correspondente.
- **Causa:** fluxo próprio não implementado.
- **Escopo do requisito:** texto original: “O usuário deve consultar e atualizar os dados
  permitidos do próprio perfil.” Não existiam critérios CA-006 nem enumeração de campos;
  documentados nome completo e e-mail da conta, comuns aos três papéis, com critérios CA-006-01/03.
- **Correção:** endpoint `/conta/perfil/`, OwnProfileForm, OwnProfileView, template e navegação
  **Meu perfil**. Objeto determinado exclusivamente por request.user; gravação limitada a
  full_name/email/updated_at. Perfil, ativação, senha, grupos e privilégios não entram na lista.
  Nome obrigatório até 150 caracteres; e-mail válido, normalizado e único, inclusive em disputa.
  Cadastro acadêmico e certificados existentes não são reescritos.
- **Arquivos:** `src/apps/accounts/{forms,views,urls}.py`, `src/config/urls.py`,
  `src/templates/accounts/own_profile.html`, `src/templates/base.html`; requisitos e manual.
- **Automatizados:** `tests/accounts/test_profile.py`: três papéis, anônimo, alvo de terceiro,
  privilégios forjados, dados inválidos/duplicados, CSRF e unicidade concorrente
  sem escrita parcial.
- **Depois:** consulta/edição e login com e-mail atualizado nos três papéis passaram. Anônimo,
  tentativa de selecionar terceiro, privilégios, obrigatórios, formato, tamanho e unicidade
  foram conferidos por HTTP, sem alteração de contas preexistentes. Cenários R-18 a R-21.

## DEF-003 — ALTO — RESOLVIDO

- **Antes:** HTTP-320, POST no Django admin retornava 302 e gravava PLANNED → COMPLETED em turma
  sem instrutor, encontros, inscrições ou avaliações.
- **Causa:** ModelAdmin salvava status diretamente; não havia actions de transição nem
  list_editable de status. Formulários add/change e MeetingInline também expunham estados.
- **Correção:** status somente leitura e formulário que rejeita POST forjado antes de gravar
  registro principal/inlines; links para os fluxos da aplicação. Cadastro de turma começa
  PLANNED, oficina DRAFT e encontro PLANNED. Não foram criadas actions que salvem estado.
  ModelAdmins de inscrições, projetos e avaliações permitem consulta e exigem serviços
  canônicos para gravação; frequência e certificado já possuíam guardas. Encontro processado
  ou turma encerrada não aceita edição de agenda; exclusão de encontros/turmas foi bloqueada.
- **Arquivos:** `src/apps/workshops/{admin,forms}.py`, `src/apps/enrollments/admin.py`,
  `src/apps/learning/admin.py`, `src/apps/core/admin.py` e testes de regressão.
- **Automatizados:** turma add/change, quatro estados forjados, ausência de gravação parcial,
  edição legítima e inline, guardas de agenda e registros acadêmicos. Os testes existentes de
  `learning` conferem conclusão canônica, nota, frequência, projetos e elegibilidade
  de certificados.
- **Depois:** tentativa de concluir diretamente retornou 200 com erro e preservou título,
  estado e inlines. Edição de outros campos retornou 302 e manteve PLANNED. Inline/MeetingAdmin
  forjados foram rejeitados; registros acadêmicos protegidos retornaram 403 para escrita.
  O fluxo acadêmico concluiu corretamente 1 aprovado e 3 não concluídos. Cenários R-22 a R-24.

Todos os defeitos foram corrigidos no commit `cccfa6ee7fb13f0c428e8375dbed5b8a3a9e4fa1` e retestados nessa imagem.

## Testes e regressão

**225 testes automatizados aprovados, sem falhas/skip, cobertura 89,11%.** Antes da suíte completa,
127 testes direcionados passaram. Ruff lint e format do repositório, Django check,
makemigrations --check --dry-run e sintaxe dos scripts passaram. Os scripts históricos estão
excluídos do Ruff para preservar bytes; o código atual, testes e executores novos são verificados.

Banco exclusivo PostgreSQL 17: `cdf_fix_test`, pytest `test_cdf_fix_test`, container temporário
`codigo-do-futuro-fix-test-db`, rede interna própria, sem porta publicada ou volume de produção.
Settings `config.settings.test`; DATABASE_URL/configuração/conexão efetivos foram verificados
antes da suíte final. Nenhuma migration ou pytest foi direcionado ao banco publicado.
Não houve mudança de schema. A proteção do único administrador foi implementada em
UserChangeForm/UserAdmin e testada somente nesse banco descartável: desativação, retirada de
papel/acesso, exclusão e duas desativações concorrentes preservam um administrador ativo.

HTTP real: 465 requisições, timeout 20s, limite 650, sessões independentes e CSRF,
sequenciais exceto duas confirmações da última vaga. 25 cenários consolidados
em [cenarios-consolidados.csv](cenarios-consolidados.csv), com variações por papel reunidas.
A matriz contém 278 verificações aprovadas, incluindo
9 passos de preparação e repetições;
**esse número não representa cenários distintos**. Preparação e
repetições não aumentam a contagem consolidada. Há ainda um registro de bloqueio do executor
superado por reteste, preservado com anotação e não contado como cenário aprovado adicional.

Regressão: autenticação/logout/redefinição de senha; permissões; pessoas; oficinas/turmas;
encontros; inscrições/capacidade/fila/concorrência; frequência e correção; projetos e revisão;
notas/publicação; conclusão; emissão/PDF/autorização/idempotência/revogação; painel e CSV.
Frequências 75/50/100/100%; aprovado com 75%, nota 6 e projeto; outros três não concluíram
respectivamente por frequência, nota e projeto. PDF de quatro horas excluiu encontro cancelado.
Painel filtrado: 4 inscrições, 100% de ocupação, frequência média 81,25%, aprovação 25%.
Recuperação completa funcionou via console, incluindo senha antiga rejeitada e token usado
inválido. Isso não demonstra entrega SMTP.

## Backup, implantação e preservação

Backup: `/home/ubuntu/projetos/projeto-integrador-ii-codigo-do-futuro/backups/codigo-futuro-20261013T161538Z.dump`, 105278 bytes, modo 600, SHA-256 `d3c59db9b0fed8673a43113ecd4c0b1ddcbc40a6c89f1e9e4486b5ad6057ceb3`.
Checksum e catálogo de 193 entradas conferidos;
não restaurado no banco em uso.
Versão anterior e imagem preservadas em versao-anterior.json e tag local
`codigo-do-futuro-app:rollback-20261013-130005`.

Os 16 modelos de negócio preexistentes, incluindo contas DEMO e validação anterior,
mantiveram contagens e hashes. A comparação cobre antes do deploy e depois do HTTP. Nenhuma
conta anterior foi autenticada, desativada, removida ou editada. Dados fictícios da nova execução
foram mantidos; IDs constam em ids-execucao.json. Credenciais ficam apenas no diretório privado
`/root/codigo-do-futuro-fix/RETEST-20261013-130005`, arquivo 600/diretório 700; tokens/cookies não foram registrados.

Dos 67 containers iniciais, apenas app mudou. Os 65 containers de outros projetos
e o PostgreSQL deste projeto mantiveram IDs, início, saúde, reinícios, imagem, portas e limites.
`hospitalar-staging-docs` e `bancodetalentos_frontend` já estavam unhealthy;
`hospitalar-staging-migrate` já estava parado/unhealthy. Nenhum foi reiniciado ou corrigido.
O ambiente temporário de teste foi removido de forma restrita, sem remoção de volumes.
Não houve restart de Docker/VPS, alteração de Nginx/certificado, push, merge ou promoção para main.

## Pendências e próximos passos

- **SMTP real:** backend continua console; entrega externa não validada.
- **Cinco avaliações humanas e usabilidade:** ainda não executadas; utilizar o pacote atualizado.
- **Responsividade:** testes HTTP não validam diferentes tamanhos de tela.
- **Acessibilidade:** ainda requer verificação dedicada de teclado/leitor/contraste.

A candidata corrigida pode iniciar as cinco avaliações; aceite humano e eventual promoção para
main continuam pendentes. A evidência original mantém sua conclusão histórica, válida para a
versão antiga. Não foi realizado teste de carga ou limpeza de registros.

## Artefatos e reprodução

- testes-automatizados.log / banco-teste.json: suíte/checks e isolamento.
- retestar.py: importa helpers originais, adapta apenas a expectativa da nova mensagem de
  duplicidade e adiciona cenários novos; não altera scripts antigos.
- matriz.json / matriz.csv / requisicoes.json: verificações, efeitos e HTTP sanitizado.
- cenarios-consolidados.csv: cenários sem inflar por preparação ou repetições.
- versao-publicada.json / backup.json / deploy.log / smoke-pos-deploy.json: operação.
- containers-*.json / dados-*.json / infra-comparacao.json / historico-preservado.json: conservação.
- segredos-verificados.json: varredura das senhas desta execução e segredos de produção sem
  divulgar valores.

Para uma futura rodada, use outro identificador/diretório de evidências e credenciais; não
execute novamente nesta pasta com os mesmos dados. Consulte os endpoints/formulários reais
e preserve os registros deste reteste.

## Diagnósticos durante a implementação

Uma ampliação dos testes detectou guarda de MeetingAdmin tratando UUID pré-gerado como registro
já persistido; corrigido com `_state.adding` antes de implantar. As iterações de lint/formatação
também foram resolvidas antes do deploy. Uma verificação inicial de endereço usou inet em texto
com sufixo /32; o lote de checks continuou apesar dessa asserção. Banco/host/settings já estavam
confirmados como exclusivos. O executor foi corrigido para `host(inet_server_addr())` e fail-fast;
a verificação final foi aprovada antes de repetir a suíte. Nenhum teste utilizou o banco publicado.

O executor HTTP parou após HTTP-124 por NameError em CREDS, uma variável do helper histórico
normalmente inicializada pelo seu ponto de entrada. Corrigida a inicialização no novo executor;
retomada restrita antes das confirmações de última vaga, sem repetir inscrições já criadas.
Matriz, requisições, log e término da primeira passagem permanecem nos arquivos
`*-primeira-passagem.*`; falha-executor.json registra o diagnóstico. Novos logins para a retomada
são repetições operacionais, não novos cenários. A aplicação e o commit publicado não precisaram
de outra alteração para essa correção do script.

Na etapa de perfil, HTTP-240 foi BLOQUEADO pelo executor: ele procurava o formulário CSRF
na página protegida anônima (302), portanto nenhum POST foi enviado. Corrigidos source público,
omissão deliberada de CSRF e verificação do formulário; o POST real retornou 403 sem escrita.
O registro inicial permanece em matriz-segunda-passagem.json; a matriz atual o anota como
SUPERADO_EXECUTOR e liga ao reteste válido, sem incluí-lo entre cenários aprovados. A segunda
passagem e seu log também estão preservados. Não foi necessário alterar código da aplicação.
