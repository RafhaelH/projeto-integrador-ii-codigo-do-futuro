# Roteiro final de vídeo — 5:00 / candidato 9f0fd32

Preparação de 03/11/2026. **Versão demonstrada: candidato funcional `9f0fd32f0d57f97c953a1e39cb62b0b601d1aeb5` em ambiente isolado com dados fictícios**, conforme validações descritas. Vídeo ainda não gravado. A aplicação pública não foi reimplantada nesta tarefa. O estudante narra com sua voz; nome/RGM completos constam somente da cópia privada.

Para a gravação final na URL pública, antes: revisar/integrar a PR em develop, publicar o SHA aprovado em operação autorizada separada, repetir smoke HTTPS e atualizar a identificação da versão efetivamente implantada. Não usar o site antigo para afirmar que estas melhorias estão publicadas. Para mostrar o candidato antes disso, usar capturas ou ambiente isolado, sempre identificado.

Os tempos são metas de edição, não garantia por contagem de palavras. Exportar e medir exatamente 300 segundos, incluindo abertura, transições e encerramento.

| Início | Fim | Duração | Cena |
|---|---|---:|---|
| 0:00 | 0:30 | 30s | Identificação, problema e versão |
| 0:30 | 1:10 | 40s | Edição de participante e preservação de dados |
| 1:10 | 1:50 | 40s | Cadastro seguro de instrutor e vínculo |
| 1:50 | 2:35 | 45s | A02 mobile, Nova turma e confirmação de cancelamento |
| 2:35 | 3:05 | 30s | Vagas, indicadores e regra de responsável |
| 3:05 | 4:10 | 65s | Relatos, qualidade, datas e organização dos testes |
| 4:10 | 4:40 | 30s | Arquitetura e evidência das correções |
| 4:40 | 5:00 | 20s | Entrega e passos antes da publicação |

## 0:00–0:30 — Identificação, problema e versão

Conta/perfil: sem conta; capa privada e identificação do candidato.

Tela e caminho: capa do documento e commit local 9f0fd32.

Ação exata: Mostrar identificação do estudante e a legenda CANDIDATO 9f0fd32 — AMBIENTE ISOLADO. Não apresentar o site público antigo como atualizado.

Narração integral em primeira pessoa:

> Eu sou o estudante responsável pelo Código do Futuro, um sistema para organizar oficinas de tecnologia, pessoas, turmas, inscrições e acompanhamento. Apresento a versão candidata de três de novembro, identificada pelo commit na tela. Esta demonstração utiliza dados fictícios em ambiente de testes. As melhorias foram verificadas, mas ainda dependem de integração e publicação para chegar à aplicação pública.

Resultado a mostrar: Nome/RGM na capa privada, versão 9f0fd32 e ambiente claramente identificados.

Alternativa: Usar capa e capturas do candidato identificadas; informar que são imagens da validação, sem afirmar navegação ao vivo.

## 0:30–1:10 — Edição de participante e preservação de dados

Conta/perfil: A02 administrador funcional no fixture isolado.

Tela e caminho: Pessoas → Participantes → participante fictício → Editar; /pessoas/participantes/ e /pessoas/participantes/<uuid>/editar/.

Ação exata: Mostrar WEB-01, WEB-02 e WEB-03 ou repetir somente em novo dado fictício isolado: três campos carregados, CPF inválido preservado e edição de nome. Explicar consentimento opcional.

Narração integral em primeira pessoa:

> Na edição de participante, eu mostro nascimento, CPF e telefone já preenchidos. A falha da data foi reproduzida e corrigida com o formato aceito pelo navegador. No teste isolado, CPF e telefone não apareceram vazios; mantive o relato e acrescentei verificações de carregamento e preservação. Uma submissão inválida informa o problema sem apagar os valores digitados. Ao editar o nome, os demais dados permanecem. O registro de consentimento é explicado e não é preenchido automaticamente.

Resultado a mostrar: Controles preenchidos, erro útil no CPF, valores preservados; nenhuma coleta automática de consentimento.

Alternativa: Mostrar as capturas WEB-01–03 e dizer que os resultados são do teste isolado.

## 1:10–1:50 — Cadastro seguro de instrutor e vínculo

Conta/perfil: A02 ADMIN sem staff/superusuário, ambiente isolado.

Tela e caminho: Pessoas → Instrutores → Novo instrutor → Criar acesso e cadastrar instrutor; /pessoas/instrutores/novo/ e /pessoas/instrutores/novo-acesso/; turma planejada → Instrutores → Vincular.

Ação exata: Mostrar o seletor vazio explicado, o novo fluxo com senhas em branco e o instrutor fictício já criado/vinculado. Não exibir nem digitar senhas na gravação.

Narração integral em primeira pessoa:

> O cadastro de instrutor dependia de um usuário elegível. A consulta estava correta, mas não havia um caminho acessível para o administrador funcional criar esse acesso. Eu acrescentei orientação e um fluxo específico, que cria somente o perfil de instrutor e seu cadastro. A senha é validada e armazenada protegida. O usuário criado não recebe acesso administrativo, grupos ou privilégios adicionais. Eu mostro o instrutor fictício vinculado à turma planejada; esse fluxo também foi testado no navegador.

Resultado a mostrar: Fluxo acessível sem Django admin; formulário sem credenciais visíveis e vínculo persistido.

Alternativa: Mostrar formulário vazio e capturas WEB-04/06, identificadas como dados isolados.

## 1:50–2:35 — A02 mobile, Nova turma e confirmação de cancelamento

Conta/perfil: A02 administrador funcional fictício; A01 como conferência complementar.

Tela e caminho: Início → Nova turma (/oficinas/turmas/nova/); Turmas → turma fictícia → Cancelar turma → confirmação (/oficinas/turmas/<uuid>/situacao/cancelled/).

Ação exata: Demonstrar viewport 390px identificado como emulação; mostrar o atalho e a turma fictícia cadastrada. Abrir confirmação sem marcar/cancelar registros publicados.

Narração integral em primeira pessoa:

> No perfil A zero dois, eu mostro menus, ações e formulários em largura móvel. O cadastro de turma já existia; a dificuldade relatada foi de localização. Agora há um atalho Nova turma no início, e o teste confirmou cadastro e vínculo do instrutor por um administrador sem privilégios extras. Menus e ações se ajustam à largura, enquanto tabelas podem rolar dentro do seu espaço. Cancelar turma abre uma confirmação explícita. A alteração exige envio autorizado e proteção contra requisições indevidas. Estas são verificações emuladas, não testes em celulares físicos.

Resultado a mostrar: A02 encontra Nova turma; ações legíveis e acessíveis; GET de confirmação não cancela nada.

Alternativa: Usar capturas candidate-nova-turma-320, WEB-05, WEB-07/08. Não cancelar uma turma publicada para a gravação.

## 2:35–3:05 — Vagas, indicadores e regra de responsável

Conta/perfil: A02 administrador; dados fictícios isolados.

Tela e caminho: Turma → Ver inscrições → Confirmar inscrição; /inscricoes/turmas/<uuid>/fila/ e /inscricoes/<uuid>/confirmar/.

Ação exata: Mostrar pendentes e espera separados, capacidade/ocupação/disponibilidade antes de confirmar. Consultar aviso de responsável em participante menor.

Narração integral em primeira pessoa:

> Na fila, eu separo inscrições pendentes da lista de espera. Antes de confirmar, apresento capacidade, ocupação e vagas disponíveis. O banco verifica as vagas novamente, protegendo a última vaga contra outra confirmação. Para menores, mantenho a regra existente: o cadastro preparatório é permitido, mas a inscrição sem responsável ativo é bloqueada. Acrescentei um aviso para explicar essa etapa, sem criar uma restrição nova arbitrária.

Resultado a mostrar: Indicadores distintos; resumo de vagas; aviso coerente com o bloqueio existente na inscrição.

Alternativa: Mostrar candidate-fila-390 e WEB-09; citar o teste de página desatualizada, sem afirmar concorrência manual não executada.

## 3:05–4:10 — Relatos, qualidade, datas e organização dos testes

Conta/perfil: sem conta; laudo e fontes anonimizadas.

Tela e caminho: docs/09-entrega/laudo-qualidade.md → docs/07-avaliacoes/fechamento-20261103/README.md → resultados e evidências.

Ação exata: Mostrar três fontes humanas sem nomes/dados pessoais; data histórica/divergência do primeiro avaliador; 264/90,54%; comparação visual e plano de certificados sem exclusão.

Narração integral em primeira pessoa:

> Eu separei três relatos humanos das reproduções técnicas. O segundo avaliador informou navegação e dificuldade para localizar a turma. O terceiro avaliador relatou fluxos funcionando, mas identificou campos vazios ao abrir a edição; conseguir editar após redigitar não elimina essa falha inicial. Na evidência do primeiro avaliador aparece treze de outubro. A informação de três de novembro fica separada, com a data a confirmar, sem inventar outra sessão. A suíte completa passou em duzentos e sessenta e quatro testes, com noventa vírgula cinquenta e quatro por cento de cobertura em PostgreSQL isolado. Também passaram cinquenta e duas combinações de tela e largura e doze fluxos no navegador. Dois certificados de simulação foram identificados pelos manifests e IDs; nenhum foi apagado.

Resultado a mostrar: Fontes e datas preservadas, reprodução parcial explicitada, contagens corretas e plano de dados sem limpeza.

Alternativa: Usar PDFs locais e resultados.json. Não atribuir testes técnicos aos avaliadores nem mostrar o relato nominal em gravação pública.

## 4:10–4:40 — Arquitetura e evidência das correções

Conta/perfil: sem conta; arquivos locais sanitizados.

Tela e caminho: Arquitetura MTV/MVC → modelo de dados → PR para develop e evidências de validação.

Ação exata: Mostrar camadas e testes. Destacar mensagens/obrigatórios e feedback “Download solicitado”; nenhum texto “concluído”.

Narração integral em primeira pessoa:

> A aplicação utiliza Python e Django, PostgreSQL, templates HTML e CSS. Views coordenam a entrada, serviços concentram regras e transações, e models preservam a integridade. As correções mantêm essa estrutura e não exigem migrations novas. Padronizei campos obrigatórios, mensagens em português e a orientação de download. O sistema informa que o download foi solicitado; não afirma que terminou. Código, testes e documentação seguem para revisão em develop.

Resultado a mostrar: Arquitetura preservada, migrations ausentes, orientação honesta e branch de revisão identificada.

Alternativa: Mostrar diagrama e logs identificados. Só anunciar CI remota concluída se o resultado real estiver disponível.

## 4:40–5:00 — Entrega e passos antes da publicação

Conta/perfil: sem conta; índice e checklist privados.

Tela e caminho: Modelo oficial e checklist-final.md.

Ação exata: Mostrar materiais e pendências. Encerrar no tempo de edição 5:00.

Narração integral em primeira pessoa:

> Eu entrego o laudo, as fontes preservadas, as evidências e o modelo atualizado. Avaliações humanas e testes técnicos continuam separados, com campos pendentes sinalizados. Antes de demonstrar essas melhorias na aplicação pública, ainda é necessário integrar, publicar e retestar por HTTPS. Confiro a versão, os links e a duração final antes da entrega.

Resultado a mostrar: Versão candidata e pendências claras; link do vídeo ainda pendente até gravação/publicação reais.

Alternativa: Mostrar o checklist local; não anunciar merge, deploy ou vídeo publicado que ainda não ocorreram.

## Preparação da gravação

- [ ] Escolher explicitamente candidato isolado ou versão pública já integrada/publicada e retestada; exibir o SHA correto.
- [ ] Usar apenas dados fictícios; abrir previamente telas ou capturas na ordem das oito cenas.
- [ ] Preparar A02 administrador funcional; A01 somente conferência. Não usar administrador operacional nem conceder staff.
- [ ] Autenticar antes da gravação e fechar terminal/arquivo de senhas; não gravar credenciais, cookies, tokens, dados reais ou fontes nominais de avaliadores.
- [ ] Deixar capa privada, laudo, formulários/capturas, fila/vagas, resultados, arquitetura e checklist abertos.
- [ ] Identificar emulação mobile e capturas isoladas. Não afirmar teste em aparelho físico nem reteste de produção.
- [ ] Preservar a data histórica 13/10 do primeiro avaliador e a divergência 03/11; não inventar segunda sessão ou preencher campos ausentes.
- [ ] Não cancelar turmas, emitir/revogar certificados ou excluir registros publicados para gravar.
- [ ] Testar áudio e legibilidade; ler a narração fora da área capturada; ensaiar os tempos e ajustar pausas/cortes sem apagar fatos.
- [ ] Exportar exatamente 300s incluindo abertura/créditos e conferir duração/voz/textos no arquivo final.
- [ ] Publicar e testar acesso do tutor sem sessão do proprietário; somente então preencher “PENDENTE — inserir após gravação e publicação” no DOCX.

## Texto corrido para leitura

Eu sou o estudante responsável pelo Código do Futuro, um sistema para organizar oficinas de tecnologia, pessoas, turmas, inscrições e acompanhamento. Apresento a versão candidata de três de novembro, identificada pelo commit na tela. Esta demonstração utiliza dados fictícios em ambiente de testes. As melhorias foram verificadas, mas ainda dependem de integração e publicação para chegar à aplicação pública.

Na edição de participante, eu mostro nascimento, CPF e telefone já preenchidos. A falha da data foi reproduzida e corrigida com o formato aceito pelo navegador. No teste isolado, CPF e telefone não apareceram vazios; mantive o relato e acrescentei verificações de carregamento e preservação. Uma submissão inválida informa o problema sem apagar os valores digitados. Ao editar o nome, os demais dados permanecem. O registro de consentimento é explicado e não é preenchido automaticamente.

O cadastro de instrutor dependia de um usuário elegível. A consulta estava correta, mas não havia um caminho acessível para o administrador funcional criar esse acesso. Eu acrescentei orientação e um fluxo específico, que cria somente o perfil de instrutor e seu cadastro. A senha é validada e armazenada protegida. O usuário criado não recebe acesso administrativo, grupos ou privilégios adicionais. Eu mostro o instrutor fictício vinculado à turma planejada; esse fluxo também foi testado no navegador.

No perfil A zero dois, eu mostro menus, ações e formulários em largura móvel. O cadastro de turma já existia; a dificuldade relatada foi de localização. Agora há um atalho Nova turma no início, e o teste confirmou cadastro e vínculo do instrutor por um administrador sem privilégios extras. Menus e ações se ajustam à largura, enquanto tabelas podem rolar dentro do seu espaço. Cancelar turma abre uma confirmação explícita. A alteração exige envio autorizado e proteção contra requisições indevidas. Estas são verificações emuladas, não testes em celulares físicos.

Na fila, eu separo inscrições pendentes da lista de espera. Antes de confirmar, apresento capacidade, ocupação e vagas disponíveis. O banco verifica as vagas novamente, protegendo a última vaga contra outra confirmação. Para menores, mantenho a regra existente: o cadastro preparatório é permitido, mas a inscrição sem responsável ativo é bloqueada. Acrescentei um aviso para explicar essa etapa, sem criar uma restrição nova arbitrária.

Eu separei três relatos humanos das reproduções técnicas. O segundo avaliador informou navegação e dificuldade para localizar a turma. O terceiro avaliador relatou fluxos funcionando, mas identificou campos vazios ao abrir a edição; conseguir editar após redigitar não elimina essa falha inicial. Na evidência do primeiro avaliador aparece treze de outubro. A informação de três de novembro fica separada, com a data a confirmar, sem inventar outra sessão. A suíte completa passou em duzentos e sessenta e quatro testes, com noventa vírgula cinquenta e quatro por cento de cobertura em PostgreSQL isolado. Também passaram cinquenta e duas combinações de tela e largura e doze fluxos no navegador. Dois certificados de simulação foram identificados pelos manifests e IDs; nenhum foi apagado.

A aplicação utiliza Python e Django, PostgreSQL, templates HTML e CSS. Views coordenam a entrada, serviços concentram regras e transações, e models preservam a integridade. As correções mantêm essa estrutura e não exigem migrations novas. Padronizei campos obrigatórios, mensagens em português e a orientação de download. O sistema informa que o download foi solicitado; não afirma que terminou. Código, testes e documentação seguem para revisão em develop.

Eu entrego o laudo, as fontes preservadas, as evidências e o modelo atualizado. Avaliações humanas e testes técnicos continuam separados, com campos pendentes sinalizados. Antes de demonstrar essas melhorias na aplicação pública, ainda é necessário integrar, publicar e retestar por HTTPS. Confiro a versão, os links e a duração final antes da entrega.
