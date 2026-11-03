# Fechamento após relatos humanos — 03/11/2026

Há **quatro relatos humanos disponíveis**, separados das simulações de outubro. Identidades e fonte integral estão na cópia privada de entrega. A fonte fornecida pelo estudante foi preservada em UTF-8, SHA-256 `d75f2b6f6b8b24487ddd0fc587d69dd0a57f6362ed2be308247d389d7957c5f8`. Não há assinatura, satisfação ou dado ausente preenchido por inferência.

| Fonte | Acesso / perfil | Data e limite |
|---|---|---|
| HUM-001 | A01 / administrador | Data do teste corrigida para 03/11/2026 conforme confirmação do estudante responsável em 03/11/2026; a captura original foi preservada. Não se inventa segunda sessão. |
| HUM-002 | A02 / administrador, confirmado pelo estudante | Relato datado 03/11/2026. Navegador e detalhes do aparelho não informados |
| HUM-003 | Administrador; username não informado | Relato datado 03/11/2026. Dispositivo/navegador não informados |
| HUM-004 | Instrutor 03; turma PY-2026-A03; username não informado | 03/11/2026, conforme confirmação do estudante. Dispositivo/navegador não informados |

## Reconciliação e fonte adicional

O relato anterior localizado é a fonte de HUM-001, cuja identidade o estudante já confirmou, e não uma quinta pessoa. HUM-004 foi recebido integralmente na conversa nesta continuação. Há quatro avaliadores distintos comprovados. Falta o conteúdo de um quinto avaliador distinto e sua identificação; não se atribuem simulações a essa pessoa.

HUM-004 relatou frequência com justificativas, percentuais de presença, revisão de projetos, edição de avaliações, notas e devolutivas funcionando; descreveu experiência positiva. Falhas e itens não testados não foram informados — isso não significa ausência de falhas ou aprovação dos demais recursos. A fonte integral e a atribuição nominal permanecem restritas.

## Observações e limites humanos

HUM-002 informou “Teste navegação do sistema.”, sugeriu melhorar a responsividade mobile e não encontrou o cadastro de turma. Não se converte essa dificuldade em ausência da funcionalidade: a rota já existia para administradores, inclusive sem staff. Atalho e verificação específicos de A02 foram incluídos.

HUM-003 declarou cadastros, vínculos, validações, downloads e cancelamentos funcionando. A frase “Depois editei o participante de teste e funcionou.” é preservada junto da observação de campos vazios: o avaliador conseguiu editar/redigitar, mas identificou falha no preenchimento inicial. Ele informou que não salvou o cadastro antigo. A fonte integral permanece privada, sem alteração de autoria.

Não testados por HUM-003, **exatamente como informados**:

- Cadastro de instrutor e vínculo de instrutor a uma turma, pelo motivo acima.
- Botão "Publicar" da oficina: deixei como rascunho para não publicar nada no sistema real.
- Outros perfis (instrutor, participante e responsável): só tive acesso de administrador.
- Cronograma da turma e outras edições: priorizei o fluxo principal.

O relato cita “responsável” entre outros perfis. A implementação possui três perfis de acesso (administrador, instrutor, participante); responsável é um cadastro/vínculo. Essa citação não cria um quarto perfil nem é tratada como funcionalidade faltante. Para HUM-001/002, não testados e demais campos ausentes continuam “não informado”. Elegibilidade de colega/profissional e ciência/autorização permanecem a confirmar.

## Reprodução técnica, causa, decisão e reteste

| Item | Observação humana | Reprodução / causa | Decisão / correção | Reteste comprovado |
|---|---|---|---|---|
| DEF-004 | HUM-003: nascimento/CPF/telefone vazios | Na base, data HTML localizada esvazia o controle nativo. **CPF e telefone salvos apareceram no fixture isolado**: esse esvaziamento não foi reproduzido | Corrigir data ISO; formatar textos somente no formulário não vinculado; preservar dados inválidos vinculados e a precisão do consentimento. Não atribuir causa não demonstrada a CPF/telefone | GET com três valores, POST inválido retém valores; edição de nome preserva CPF/telefone/data/consentimento. WEB-01–03 e regressões |
| DEF-006 | HUM-003: seletor Usuário vazio para instrutor | Consulta está correta: somente instrutores ativos e sem vínculo. Inventário publicado tem zero elegíveis. Falta fluxo para administrador funcional criar esse acesso | Fluxo explícito “Criar acesso e cadastrar instrutor”, papel INSTRUCTOR fixo, sem staff/superusuário/grupos; senhas validadas; transação e rollback | WEB-04/06, vínculo à turma; testes de papel/CSRF/duplicidade/senha/rollback/usuários indevidos |
| DEF-005 / descoberta | HUM-001/002: responsividade; HUM-002: não encontra turma | Base apresentou duas combinações com transbordamento; cadastro de turma já existia | Contenção do rótulo acessível, menus/ações com quebra, campos limitados à largura e atalho Nova turma no início | 52 combinações candidatas sem transbordamento externo; WEB-05/12, A02 cadastra em 390px e A01 navega em 320px |
| UX-007 | Cancelar turma imediato | POST antigo cancelava sem etapa de confirmação | GET somente mostra confirmação; POST exige checkbox, autorização e CSRF; serviço transacional mantido | WEB-07/08 e testes GET/POST/CSRF/papel |
| UX-008 | Pendentes / espera ambíguos | Números estavam juntos | Indicadores separados na fila e no painel; mesmo universo de filtros | Asserções do banco, snapshot, tabela e captura |
| UX-009 | Lotação só percebida ao confirmar | Formulário não mostrava resumo | Capacidade/ocupadas/disponíveis antes de confirmar; alerta de disputa pela última vaga | WEB-09; teste ocupa a última vaga após GET e POST não sobrelota |
| UX-010/011/012 | Obrigatórios, 0.01 e consentimento pouco claros | Templates divergentes; mensagem numérica padrão; registro sem explicação | Campo obrigatório padronizado; carga horária em PT-BR; ajuda explica registro real, sem preenchimento automático ou autorização de imagem implícita | WEB-10, regressões, consentimento vazio permanece vazio e existente mantém precisão |
| RN-005/020 | Relatou inscrição de menor sem responsável | Não reproduzido com menor de 18 anos sem vínculo ativo. Regra existente verifica a idade na inscrição e no início; 14–21 no início | Manter bloqueio **na inscrição**, permitir cadastro preparatório e mostrar aviso de responsável no detalhe. Nenhuma restrição nova no cadastro | Testes de serviço existentes e POST administrativo sem responsável rejeitado |
| UX-014 | Download sem retorno visual | Links respondiam arquivo sem status na página | “Download solicitado”, com orientação para conferir o navegador. Não anunciar “concluído” | WEB-11 recebeu CSV real no navegador; texto do status não afirma conclusão |
| DATA-015 | Certificados com SIM-20261019 | Dois certificados correspondem aos IDs dos manifests da preparação | Somente inventário/plano restritos; **nenhuma exclusão, revogação ou limpeza publicada** | IDs/vínculos conferidos por leitura; usar certificado de apresentação previamente identificado ou escopo do participante; a listagem global de certificados não possui filtro |

Os casos não reproduzidos continuam identificados; correção técnica não se converte em reteste humano. Não atribuir a HUM-001 a mesma tela de overflow sem confirmação.

## Versão e evidências

Candidato funcional `9f0fd32f0d57f97c953a1e39cb62b0b601d1aeb5`. Base develop 58db4fc; inclui os candidatos anteriores de datas/layout. **Não implantado.** Publicação anteriormente identificada como a351c5a não recebeu essas alterações nesta tarefa.

- [Relatório de testes](../../06-testes/fechamento-20261103/README.md): 264 testes em PostgreSQL isolado, zero skips, cobertura 90,54%; Ruff/check/migrations/JS aprovados.
- [96 verificações de largura](../../06-testes/fechamento-20261103/verificacao-visual.json): 44 da base, 52 do candidato; não são 96 pessoas nem cenários funcionais independentes.
- [12 fluxos completos no navegador](../../06-testes/fechamento-20261103/fluxos-navegador.json), com ações apenas em dados fictícios isolados.
- [Dados humanos anonimizados](avaliacoes.json). Fonte integral e inventário nominal ficam fora do Git.

Até 17/11/2026: revisar/integrar PR para develop em ação posterior, publicar o SHA aprovado, repetir smoke HTTPS, confirmar somente lacunas efetivamente ausentes e completar a evidência de um quinto avaliador distinto, gravar/exportar 300s e submeter. A continuação autoriza integrar e publicar exclusivamente este Compose; main será preservada. Resultados de implantação serão registrados após a execução.
