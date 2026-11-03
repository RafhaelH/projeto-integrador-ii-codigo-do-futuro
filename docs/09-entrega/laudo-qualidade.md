# Laudo de qualidade — fechamento de 03/11/2026

**Parecer condicionado.** Candidato funcional `9f0fd32f0d57f97c953a1e39cb62b0b601d1aeb5`, testado em PostgreSQL isolado e navegador local; não implantado. Identificação do estudante e dos avaliadores apenas na cópia privada. [Fontes, causas e decisões](../07-avaliacoes/fechamento-20261103/README.md).

## Histórico preservado

DEF-001: encontro duplicado retornava 500; validação e tratamento da constraint passaram a informar erro útil. DEF-002: perfil próprio ausente; formulário/view/rota limitados ao próprio nome/e-mail. DEF-003: conclusão acadêmica indevida pelo Django admin; campos protegidos e fluxo canônico exigido. [Retestes históricos](../06-testes/consolidacao-verificacao.md) permanecem preservados, sem atribuição retroativa a avaliadores humanos.

## Correções e limites atuais

- **Edição de participante:** data ISO corrige valor nativo vazio. CPF/telefone existentes estavam preenchidos no fixture da base; o esvaziamento relatado não foi reproduzido. Candidato formata valores iniciais sem sobrescrever POST inválido, preserva os demais campos e a precisão do consentimento. Testes de persistência e navegador aprovados.
- **Instrutor:** consulta de elegíveis correta, com zero opções no inventário publicado. Criado fluxo acessível ao administrador funcional para provisionar apenas INSTRUCTOR e cadastro, com senha validada/hash, transação e rollback; nenhum staff/superusuário/grupo adicional. Vínculo à turma testado.
- **Responsividade e descoberta:** duas combinações com overflow na base; 52 candidatas sem overflow. Rótulos acessíveis contidos, menus/ações com quebra e campos ajustados. A02 sem staff encontrou Nova turma pelo início, cadastrou e vinculou instrutor em 390px; A01 conferido em 320px. Cadastro de turma já existia, não foi inventado como funcionalidade nova.
- **Operação:** confirmação explícita antes do cancelamento, GET sem alteração e POST com CSRF/papel; indicadores de pendentes/espera separados; vagas visíveis antes da confirmação e validação transacional preservada contra página desatualizada; obrigatórios padronizados; mensagem numérica em PT-BR; consentimento explicado sem coleta automática; download apenas solicitado, sem afirmação indevida de conclusão.
- **Menores:** regra existente bloqueia inscrição sem responsável ativo quando menor na inscrição ou no início. Cadastro preparatório continua permitido com aviso. Relato de inscrição permitida não reproduzido nas condições da regra; faltam IDs/datas para concluir esse caso humano. Não foi aplicada restrição nova arbitrária.
- **Certificados SIM:** dois IDs correspondem aos manifests. Inventário/plano restritos preparados; nenhuma exclusão ou revogação publicada. Registros continuam no histórico, inclusive os que poluem apresentação global.

## Evidência e avaliação humana

**264 testes aprovados, zero skips, 90,54% de cobertura**, PostgreSQL 17 isolado; Ruff, Django check, ausência de migrations novas e sintaxe JS aprovados. Comparação visual: 44 combinações de base / 52 candidatas, quatro larguras; 12 fluxos completos aprovados. [Evidências](../06-testes/fechamento-20261103/README.md). Não somar combinações/requisições como novas pessoas ou cenários. Não há prova de AA, aparelhos físicos, carga ou todos os navegadores.

Três relatos humanos preservados; não cinco. HUM-003 conseguiu editar, mas relatou campos vazios ao abrir: fatos compatíveis quando houve redigitação. Não testados foram transcritos exatamente. HUM-001 mantém captura 13/10/2026 e informação do estudante 03/11/2026, **data do teste a confirmar**, sem segunda sessão comprovada. Senhas, fontes nominais e dump não estão no Git.

Antes da gravação final na aplicação pública: revisar/integrar PR em develop, publicar em tarefa separada autorizada, identificar SHA implantado e repetir smoke HTTPS. Sem isso, apresentar somente o candidato isolado com versão explícita. Vídeo e requisito de cinco colegas/orientação do tutor seguem pendentes, além dos documentos originais I ausentes.
