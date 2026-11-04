# Laudo de qualidade — versão publicada em 03/11/2026

**Apta para gravação técnica no escopo retestado. Entrega acadêmica parcial quanto à quinta fonte humana e ao vídeo.** Publicação `10210ad7bc9c995c90207fa1c2dce6c546d217f6`, imagem `sha256:8bcc8d37eb5b397eaf2695286904b6f065bdd8176253733a2b1f775e88816bd3`; PR #14 integrada em develop, main preservada. Nome/RGM e fontes nominais somente na cópia privada do tutor.

## Achados, decisões e comprovação

DEF-001/002/003 são defeitos técnicos históricos (duplicidade de encontro, perfil próprio e conclusão indevida pelo admin), com evidências preservadas; não foram atribuídos retroativamente aos avaliadores. [Consolidação histórica](../06-testes/consolidacao-verificacao.md).

DEF-004: data localizada esvaziava o controle nativo; ISO corrige o carregamento. CPF/telefone vazios relatados por HUM-003 não foram reproduzidos na base. Na publicação, três valores carregam; erro mantém entradas e edição de outro campo preserva dados/consentimento. Não se inventa causa para CPF/telefone. HUM-003 conseguiu editar após redigitar, o que não elimina a falha de preenchimento inicial.

DEF-006: faltavam usuários elegíveis e fluxo acessível ao administrador funcional. Provisionamento de apenas INSTRUCTOR, senha validada/hash, transação, sem staff/superusuário/grupos; criação e vínculo aprovados no site.

DEF-005 e localização: correções de contenção, menus/ações/formulários; A02 encontra Nova turma. Cadastro já existia. Publicação passou em 24 combinações desktop/mobile e ação da tabela alcançável por rolagem interna em 320px; emulação, não celular físico.

UX-007–014: cancelamento exige confirmação por POST/CSRF/autorização; pendentes e espera separados; capacidade/ocupação antes de confirmar sem remover trava de vagas; obrigatórios e PT-BR padronizados; consentimento explicado sem coleta automática; download apenas solicitado na interface, com PDF/três CSV recebidos pelo navegador.

Menores: cadastro preparatório permitido; bloqueio já existente na inscrição sem responsável ativo quando menor na inscrição ou início. Aviso esclarece a regra. O caso humano de inscrição permitida não foi reproduzido nas condições conhecidas; faltam IDs/datas para analisar aquela ocorrência, sem nova restrição arbitrária.

Certificados de simulação: dois IDs conferidos por manifests/vínculos. Inventário/plano restritos, sem exclusão/revogação. Para gravação, abrir certificado de apresentação conhecido; a lista global não possui filtro.

## Verificação e fontes humanas

Quatro relatos humanos disponíveis, todos consolidados em 03/11/2026 conforme confirmação expressa do estudante. HUM-001: captura original com 13/10/26 preservada; “Data do teste corrigida para 03/11/2026 conforme confirmação do estudante responsável em 03/11/2026; a captura original foi preservada.” Não se inventa segunda sessão. HUM-002 usou A02 administrador; HUM-003 administrador, username não informado; HUM-004 instrutor 03, turma PY-2026-A03, username não informado. O relato anterior localizado é HUM-001, não uma quinta pessoa. Falta a fonte de um quinto avaliador distinto. Não testados de HUM-003 preservados literalmente; demais itens omitidos são “não informado”.

CI do HEAD da PR e pós-merge aprovada: **264 testes PostgreSQL, zero skips, cobertura 90,54%**, Ruff, configuração, migrations, build/startup. [Retestes publicados](../06-testes/publicacao-20261103/README.md): 24 verificações registradas, 24 combinações de tela/largura e 12 consultas estáveis do vídeo, HTTPS/TLS, sessões independentes e CSRF. A rodada isolada anterior de 52 combinações/12 fluxos é evidência distinta, não duplicada. Não se afirma AA, aparelhos físicos, carga ou cobertura de todos os navegadores.

Backup com checksum/catálogo verificados e imagem anterior preservada. Zero alterações de negócio preexistentes, zero exclusões; 19 registros fictícios exclusivos inventariados. 73 contêineres de outros projetos, banco deste projeto, configuração global e main preservados.

## Limitações e entrega

Planejamento/backlog/roadmap atuais do Integrador II foram conferidos; não foi localizado planejamento/protótipo original atribuível ao Integrador I. Isso é limitação histórica, sem fabricar continuidade. Fontes nominais, original AVA e cópias DOCX/PDF ficam restritos. Falta a fonte de uma quinta pessoa distinta; campos ausentes ficam sinalizados. Vídeo: **PENDENTE — inserir após gravação**. Prazo informado: 17/11/2026. O estudante ainda deve gravar, medir 300s, publicar/testar o link, inserir no AVA, regenerar PDF/ZIP e submeter/guardar recibo.
