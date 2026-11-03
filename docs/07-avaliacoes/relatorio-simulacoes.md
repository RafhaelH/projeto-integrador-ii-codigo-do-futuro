# Simulações técnicas por perfil — 19/10/2026

## Autoria, natureza e versão

Execução SIM-20261019 pelo **agente Codex**, por solicitação do estudante. Não são cinco pessoas, opiniões, assinaturas nem satisfação humana. Durante a execução inicial nenhum relato humano havia sido disponibilizado. Posteriormente chegou HUM-001/A01 por print, com identificação confirmada pelo estudante; ver consolidação separada. Não se infere autoria pelo uso de uma conta. A exigência de cinco colegas/profissionais e eventual autorização do tutor para substituição continuam pendentes.

Publicação a351c5a reconfirmada por 122 hashes; develop 58db4fc, PR #13 integrada. Main preservada. Navegador Chromium/Playwright, HTTPS real com TLS validado, cinco contextos independentes, login/logout e formulários HTML com CSRF. Não há API REST presumida. Viewports 1440×1000 e 390×844; não são aparelhos físicos nem aprovação de usabilidade/AA.

## Resultados e evidências

**39 tarefas distintas: 37 APROVADO, 2 REPROVADO, 0 BLOQUEADO, 0 NÃO EXECUTADO.** As duas reprovações (A01-T03/A02-T03) reproduzem um único defeito, DEF-004. Na primeira passagem houve 34 aprovações e cinco reprovações: três eram falhas do executor e foram corrigidas/retestadas sem alterar a aplicação. São 39 execuções iniciais + cinco reexecuções, não 44 cenários distintos. As 150 respostas HTTP registradas não são 150 cenários. A conferência adicional das oito telas do vídeo é somente leitura, separada dessa contagem.

| Perfil | Tarefas distintas | Aprovadas | Reprovadas | Observação |
|---|---:|---:|---:|---|
| A01 ADMIN funcional | 8 | 7 | 1 | Edição simples do participante SIM bloqueada pela data nativa vazia |
| A02 ADMIN funcional | 8 | 7 | 1 | Mesmo DEF-004; conclusão e PDF de 2h confirmados |
| A03 INSTRUCTOR | 8 | 8 | 0 | Chamada, revisão e nota 8 publicada somente na turma SIM atribuída |
| A04 INSTRUCTOR | 8 | 8 | 0 | Mesmo método em registros exclusivos distintos |
| A05 PARTICIPANT | 7 | 7 | 0 | Inscrição SIM pendente, projeto novo entregue e certificado próprio consultado |

- [Matriz completa CSV](simulacoes-20261019/matriz-tarefas.csv) e [JSON](simulacoes-20261019/tarefas.json): identificador, perfil, início/fim com fuso, autoria/método, objetivo, pré-condições, esperado/observado, evidência e situação para cada tarefa.
- [Primeira passagem preservada](simulacoes-20261019/primeira-passagem.json), [cinco retestes](simulacoes-20261019/retestes.json), [respostas HTTP sem payload/cookies/tokens](simulacoes-20261019/respostas-http.json) e [manifesto/hashes](simulacoes-20261019/evidencias.json).
- Capturas completas da primeira passagem ficam restritas, porque a saudação de uma conta pode conter identificação informada por seu usuário. Só capturas feitas com essa saudação ocultada foram incluídas no Git. O identificador `restrito:capturas-completas/...` é referência ao anexo privado, não link público.

## Dados exclusivos e preservação

Backup custom do projeto validado por checksum e catálogo com 193 entradas antes de alterações. Manifesto privado registra o caminho/sha; dumps não entram no Git. Foram criadas seis turmas SIM-20261019-A01/A02/A03/A04/A05/A05-I e quatro participantes fictícios sem nova conta de login. A05 reutiliza seu perfil fictício comprovado apenas como titular de novas inscrições/projetos; não altera seu cadastro antigo. Novos vínculos de instrutores não substituem os antigos. [Manifesto dos cenários](simulacoes-20261019/cenarios.json).

O bootstrap usa datas **sintéticas** coerentes para pré-condições de encontros passados, inscrições e entregas. O relógio foi simulado apenas dentro do processo de criação desses novos fixtures, nunca no servidor, navegador ou datas/horários das tarefas. Bootstrap por ORM/serviços não conta como execução HTTPS de uma tarefa. Não foram criados relatos ou eventos humanos.

Ao final há **57 registros gerenciados novos**: quatro participantes, seis turmas, seis vínculos, seis encontros, seis inscrições, treze históricos, cinco presenças, cinco projetos, quatro avaliações acadêmicas fictícias e dois certificados. Nenhum registro preexistente de negócio foi alterado ou excluído. Sessões iniciais preservadas, sessões de teste encerradas; autenticação altera last_login somente das contas utilizadas. A01/A02 são administradores globais sem staff/superusuário: separação por roteiro/dados, não por tenant. Totais globais passam a incluir os dados SIM; o vídeo usa Python/abril para manter universo explícito.

## A05: encerramento esperado e alternativa

PY-2026-A05-I encerrou em **16/10/2026 18h America/Sao_Paulo**. Não apareceu nas ofertas; POST HTTPS direto com CSRF retornou a mensagem “A solicitação está fora do período de inscrições.”, sem mudar a oferta histórica. Isso é comportamento esperado, não defeito.

A alternativa **SIM-20261019-A05-I** abriu somente no espaço gerenciado, com encerramento em **22/10/2026 18h** e início 26/10. A simulação enviou uma solicitação e confirmou PENDING, sem confirmação automática. Essa tarefa já foi consumida pelo agente: uma pessoa real deve consultar a situação existente ou receber outra oferta exclusiva preparada pelo responsável após novo backup. Não atribuir essa solicitação ao avaliador humano nem renovar a oferta histórica.

## Achado real, correção e limites

DEF-004: campos date/datetime-local recebem valores localizados, como 15/02/2007. O HTML tem o valor, mas o input nativo fica vazio; salvar só autorização de imagem retorna data obrigatória. Reproduzido em A01/A02 novos, sem modificar cadastros antigos. [Captura do erro](simulacoes-20261019/capturas/A01-T03-defeito-data.png).

Correção mínima em branch local fix/inputs-data-html5-20261019, commit `d1a55239fb6518d7610eded64966dce41abe2917`: formatos ISO explícitos nos dez widgets de pessoas/turmas/encontros/filtros; sem models/migrations. Dez regressões falharam antes; **41 testes direcionados passaram em SQLite :memory:** depois; Ruff/check/makemigrations passaram. Chromium confirmou dez valores nativos vazios antes e dez preenchidos depois em HTML isolado. [Antes](simulacoes-20261019/capturas/DEF004-widgets-original-isolados.png) / [candidato corrigido, não publicado](simulacoes-20261019/capturas/DEF004-widgets-corrigido-isolados.png).

**Não houve deploy. DEF-004 continua na aplicação a351c5a.** Implantação autorizada posterior e reteste público são pendências antes de anunciar correção publicada ou marcar A01-T03/A02-T03 aprovadas. Não usar 235/89,84% como resultado da branch corretiva: esses números são históricos de outra execução.

Falhas do executor: A01/A02-T06 procuravam link de certificado após emissão que já redireciona ao detalhe; continuação confirmou PDF real 2h e idempotência. A05-T05 usava seletor description que também encontrava meta description; restringido a textarea, entrega confirmada. As três falhas iniciais permanecem no histórico, diferenciadas do defeito do produto.

## Avaliações humanas disponíveis

Após a simulação inicial, recebido **um relato humano HUM-001/A01** por print, data informada 13/10/2026, nome e computador confirmados pelo estudante. Conteúdo e lacunas estão na [consolidação humana](consolidacao.md) e na cópia privada do modelo oficial. Quatro relatos ainda faltam; condição de colega/profissional e demais lacunas do primeiro seguem a confirmar. As [fichas de distribuição](resultados/README.md) permanecem modelos em branco. Nenhuma simulação foi convertida em opinião humana.

A [conferência móvel posterior](revisao-humana-20261019/README.md) tem contagem própria de 24 verificações (22 sem transbordamento e duas com DEF-005); não altera os resultados das 39 tarefas. Quatro verificações do candidato CSS passaram isoladamente, sem implantação ou aprovação de dispositivos reais.
