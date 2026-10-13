# Relatório final — candidata e pendências acadêmicas

## 1. Identificação e conclusão atual

Código do Futuro — Projeto Integrador Transdisciplinar em Engenharia de Software II. Autor registrado no projeto: Rafhael Henrique, Engenharia de Software. Auditoria: 13/10/2026. [Repositório](https://github.com/RafhaelH/projeto-integrador-ii-codigo-do-futuro); aplicação https://projeto-integrador.tesseratointegra.com.br.

Base documental develop: 644e7a657c1aeec80b7df530856fd354e5a02454. Código publicado: a351c5aeb6a9bf104693818a75a0acc6c82e49ad, mesmo src da base; 122 hashes reconfirmados nesta auditoria. [Estado](estado-verificado.json). Main permanece 5730e37. Não há tag/versão acadêmica final nem data de conclusão integral registrada.

**O MVP possui implementação e evidências técnicas; a entrega acadêmica não está integralmente concluída.** Faltam cinco opiniões de pessoas elegíveis, PDF preenchido, decisões sobre feedback e vídeo narrado; há lacunas de origem I/modelo AVA. A [matriz](matriz-conformidade.md) fundamenta cada situação.

## 2. Problema, objetivo e escopo

Oficinas gratuitas precisam organizar pessoas, responsáveis, vagas, encontros, presença e resultados. Planilhas/mensagens dispersas prejudicam integridade e rastreabilidade. A solução web acompanha jovens de 14–21 anos da inscrição à conclusão, com três papéis. O [escopo](../01-contexto/escopo.md) distingue funcionalidades implementadas e fora do MVP; a evolução comprovada vem do Git do Integrador II, sem inventar revisão histórica do Integrador I.

Entregues: acesso/perfil próprio, pessoas/instituições, ofertas/turmas/encontros, inscrições/fila/transações, frequência/projeto/avaliação/conclusão objetiva, certificado PDF/revogação, painéis e CSV. Recuperação usa console na publicação e não comprova entrega de e-mail externo.

## 3. Projeto e implementação

[Arquitetura](../04-arquitetura/arquitetura.md) documenta camadas e MTV/MVC. Python 3.12, Django 5.2, PostgreSQL 17, templates HTML/CSS; dependências uv.lock; CI Pytest/Ruff/GitHub Actions; publicação Gunicorn/Docker/Nginx/HTTPS. [UML/DER](../03-modelagem/diagramas.md), [conceitual e normalização](../03-modelagem/modelo-de-dados.md), [modelo lógico](../03-modelagem/modelo-logico.md), [banco físico](../03-modelagem/banco-fisico.md) e [dicionário](../03-modelagem/dicionario-de-dados.md) refletem 16 models persistentes e 7 migrations próprias. SQL de referência é gerado offline, não um dump da VPS.

## 4. Verificação e correções comprovadas

[Consolidação](../06-testes/consolidacao-verificacao.md): 235 testes aprovados em PostgreSQL isolado, zero skip, cobertura 89,84%; CI develop 644e7a6 aprovada. Reteste anterior: 25 cenários HTTP consolidados, 278 verificações/465 requisições; preparação atual: 57 verificações/81 requisições aprovadas. Requisições e repetições não são cenários distintos. Os relatórios históricos conservam as reprovações originais.

Três defeitos corrigidos em cccfa6e/PR #11 e retestados: encontro duplicado 500 → formulário 200 útil; RF-006 ausente → perfil próprio com whitelist/CSRF/unique; conclusão direta no admin → bloqueio e processamento acadêmico canônico. PR #12 prepara cenários e materiais, integrado em 644e7a6. O manual reúne 38 imagens reais/fontes identificadas; inspeção visual limitada não é aceite humano nem aprovação WCAG.

Esta auditoria realiza checks/documentação fora do banco publicado, confere fontes/links/renderizações/segredos e abre PR documental. Nenhuma alteração de banco, conta, cenário, container ou Nginx foi necessária. [Verificações documentais](verificacoes-documentais.json).

## 5. Cinco avaliações e decisões

**aguardando avaliação humana**. Selecionar cinco colegas de curso ou profissionais da área; A01–A05 são contas, não pessoas. Distribuição atual: A01/A02 ADMIN, A03/A04 INSTRUCTOR, A05 PARTICIPANT. Fichas permanecem em branco, incluindo nome/data/funcionou/falhou/correção/não testado/motivo. [Pacote](../07-avaliacoes/pacote-de-avaliacao.md), [modelo consolidado](../07-avaliacoes/modelo-pdf-consolidado.md) e [registro de decisões](../07-avaliacoes/registro-de-melhorias.md).

A oferta PY-2026-A05-I encerra 16/10/2026 às 18h America/Sao_Paulo. Para sessão posterior, revisar a tarefa e planejar oferta exclusiva futura após autorização/revisão/backup em trabalho operacional separado; nesta auditoria não renovar datas. Se não puder testar, registrar motivo verdadeiro, sem preencher sucesso fictício.

## 6. Limitações e pendências

Não há prova identificada do planejamento/protótipo original I nem o modelo específico de entrega AVA. O estudante deve obtê-los/conferir com tutor. SMTP externo, testes de carga/escala, compatibilidade nos navegadores exigidos e auditoria completa de acessibilidade não estão aprovados; [rastreabilidade RNF](../02-requisitos/rastreabilidade-implementada.md) explicita limites. Não há resultados de usabilidade humana nem sugestões humanas aceitas/recusadas nesta data.

Vídeo: roteiro exatamente 5:00 resolve os dois limites do PDF; narração deve ser do estudante. Gravação/arquivo/link permanecem pendentes. Exibir funcionamento, testes e mudanças efetivamente adotadas; citar a ausência de resultados enquanto faltarem sessões.

## 7. Fechamento necessário

Seguir a [sequência exata do checklist](checklist-final.md#sequência-exata-para-concluir): obter documentos/AVA; selecionar pessoas; conferir prazos/cenários; realizar cinco sessões; consolidar/decidir; corrigir e retestar o pertinente; gerar PDF real, atualizar manual/versões se necessário; gravar/exportar 300s; conferir modelo/links/anexos e submeter ao tutor. Merge desta PR e eventual promoção/release são decisões posteriores, não executadas aqui. Atualizar matriz e relatório somente com evidências reais.
