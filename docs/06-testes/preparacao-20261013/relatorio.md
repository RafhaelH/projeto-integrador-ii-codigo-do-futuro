# Preparação para avaliações, manual e vídeo

Ambiente: https://projeto-integrador.tesseratointegra.com.br. Referência dos dados: **13/10/2026**, America/Sao_Paulo. Código publicado: **a351c5aeb6a9bf104693818a75a0acc6c82e49ad**. Os 122 arquivos de código do runtime conferem por SHA-256 com o commit; app e banco estão saudáveis. O administrador operacional foi preservado com todos os campos iguais ao inventário, inclusive senha, permissões, nome e datas.

O PR [#11](https://github.com/RafhaelH/projeto-integrador-ii-codigo-do-futuro/pull/11), das três correções anteriores, passou na CI e foi integrado em develop no commit `8924a6d`. A preparação está na branch `feat/preparacao-avaliacoes-20261013`, com implementação `3be6200` e ajuste de cronologia `a351c5a`. A publicação deste pacote é registrada separadamente; main não recebe promoção.

## Backup, origem e limpeza

Antes de qualquer modificação de dados foi criado `backups/codigo-futuro-20261013T170703Z.dump`, 114607 bytes, SHA-256 `572058b38fc3bb8bdae8e4caf765d12c3eeb45372934a513676be89e05918d77`, catálogo de 193 entradas conferido. O backup foi restaurado somente no PostgreSQL temporário deste projeto para ensaiar limpeza e preparação. Não houve restauração no banco publicado. Backups anteriores foram preservados; houve também backup intermediário e backup final da base preparada, registrados em JSON.

Os manifests das duas execuções históricas comprovaram **225 registros técnicos** em 17 modelos, incluindo 14 usuários, 14 turmas, 26 inscrições, 61 históricos, 32 frequências, 8 avaliações e 2 certificados. A prova usou IDs, relatórios e relações, não prefixos. A exportação restrita está em `/root/codigo-do-futuro-presentation/20261013/technical-archive.json`, com 225 registros e 56 sessões autenticadas, IDs/relações e checksum. Após revisão de FKs/cascatas, esses registros foram removidos em transação. Não houve dependência ambígua nessa base.

Os **95 registros originais** foram preservados por ID, incluindo a conta operacional. A origem fictícia foi corroborada com fixtures exatas do seed original, autor operacional e grafo de relações. Não foram encontrados registros de negócio de origem desconhecida no inventário; permissões/content types globais e sessões sem prova de origem foram preservados. Os 33 arquivos da validação e 52 arquivos do reteste anteriores mantêm os bytes originais. Nenhuma evidência histórica foi apagada.

Os dois ensaios HTTP desta preparação criaram e removeram **32 registros e 5 sessões cada**, também com IDs exclusivos e exportação restrita. O primeiro conferiu 3be6200; o segundo repetiu os fluxos em a351c5a após o ajuste das datas. Total removido nesta tarefa: 289 registros de domínio/log e 66 sessões comprovadas. As exportações dos ensaios permanecem na pasta restrita, separadas da exportação histórica. Não há limpeza pendente identificada.

## Base preparada

Todos os nomes e atividades são fictícios. Prefixos técnicos foram removidos dos nomes e títulos apresentados. E-mails novos usam example.com; nenhum e-mail foi enviado. CPF/CNPJ/telefones opcionais são vazios; telefone obrigatório de responsável usa DDD 00 não discável. A conta operacional e o código histórico do certificado original foram mantidos.

| Cenário estável | Estado e consistência |
|---|---|
| Ana Oliveira e responsável | Menor com responsável ativo e vínculo principal |
| PY-2026-02 | Planejada, período futuro e instrutor vinculado |
| ROB-2026-01 | Aberta; capacidade 2, confirmadas 2, espera 1, pendente 1; encontros em 10/11 e 01/12 |
| WEB-2026-01 | Em andamento; dois encontros realizados e dois futuros; Carla 100%, Diego 50% |
| Projetos/avaliação Web | Projeto entregue e rascunho; nota de Carla 8,5 ainda não publicada |
| PY-2026-01 | Concluída; Ana aprovada com 100%, nota 9,2 e projeto; Bruno não concluinte por 50%, nota 7,0 e projeto |
| Certificado original | Ativo, PDF real de Ana, 8h = quatro encontros de 2h |

A abertura original de Robótica em agosto foi preservada, para anteceder confirmações e entrada na espera daquele mês. Fechamento e cronograma foram prorrogados de forma coerente; a correção ficou registrada e coberta em teste. Não houve ajuste artificial de contadores.

| Entidade final | Quantidade |
|---|---:|
| Usuários | 19 |
| Participantes | 11 |
| Responsáveis/vínculos | 3 / 3 |
| Instrutores | 4 |
| Instituições | 1 |
| Oficinas | 3 |
| Turmas | 11 (4 estáveis + 7 exclusivas) |
| Encontros | 17 |
| Inscrições/históricos | 15 / 33 |
| Frequências | 16 |
| Projetos/avaliações | 10 / 6 |
| Certificados ativos | 2 (8h e 2h) |

Painel global: 11 turmas, 11 participantes únicos, 15 inscrições, 12 ocupantes acadêmicos de 53 vagas (22,64%), 8 projetos entregues, 2 aprovados e 1 não concluinte (66,67% de aprovação). Frequência média 87,50% entre as oito inscrições com encontros realizados; inscrições ainda sem encontro realizado ficam fora dessa média. No filtro Python/abril, o universo é 1 turma, 2 participantes, frequência média 75%, 1 aprovado e 1 não concluinte (50% de aprovação). CSV e tela usam o mesmo filtro.

## Cinco acessos humanos e materiais

A01/A02 são administradores funcionais, A03/A04 instrutores vinculados somente a suas próprias turmas, A05 participante. Nenhuma conta de avaliação possui staff, superusuário ou permissões extras. Os registros de trabalho são distintos; administradores têm alcance global do produto e seguem roteiro próprio acompanhado pelo responsável. Nenhuma tarefa modifica os cenários estáveis. A05 tem três turmas próprias: projeto em elaboração, oferta aberta e certificado de uma conclusão calculada pelos serviços canônicos.

Senhas aleatórias distintas e estado da carga ficam somente em `/root/codigo-do-futuro-presentation/20261013/credentials.json` e `state.json`, diretório 700/arquivos 600, fora do Git. Para consulta e entrega individual, seguir [instruções do responsável](../../07-avaliacoes/instrucoes-responsavel.md); nunca expor o conteúdo em gravações. A idempotência foi testada inclusive após tarefas administrativas, sem reset de notas/senhas. A execução antiga seed_demo fica bloqueada após a preparação. Veja [operação e simulação](operacao.md).

O [pacote de avaliações](../../07-avaliacoes/pacote-de-avaliacao.md) reúne instruções, cinco roteiros com objetivo/partida/resultado/evidência, fichas individuais, consolidação, problemas/decisões e checklist. Tudo permanece **aguardando avaliação humana**, com respostas/notas/resultados em branco. Há [HTML imprimível](../../07-avaliacoes/pacote-imprimivel.html) e [PDF](../../07-avaliacoes/pacote-imprimivel.pdf).

Foram produzidos 38 PNG: 36 screenshots reais da aplicação em desktop/mobile, visualizador local do CSV real e página renderizada do PDF real. Não houve edição de números ou geração de telas. O [plano](../../08-manual/plano-de-capturas.md) identifica perfis, caminhos, cenário, viewport, arquivos e legendas; manifest guarda hashes e horários. [Manual ilustrado](../../08-manual/README.md), [PDF](../../08-manual/manual-imprimivel.pdf), [HTML](../../08-manual/manual-imprimivel.html) e [roteiro do vídeo](../../08-manual/roteiro-video.md) estão prontos. Não há captura obrigatória pendente; Excel específico/aparelho físico são opcionais. O vídeo ainda será gravado e as cinco pessoas ainda realizarão as sessões.

## Verificações e preservação da VPS

- 235 testes aprovados, sem skips, PostgreSQL isolado; cobertura 89,84%; lint, formatação, check Django, check deploy e ausência de migrations pendentes conferidos.
- 57 verificações e 81 requisições HTTPS na versão final, com TLS, sessão e CSRF: cinco acessos, perfil, permissões, fila/capacidade, chamada, projeto, avaliação, conclusão, PDF e três CSV.
- Os três defeitos permanecem corrigidos: conclusão forjada no admin rejeitada antes de gravar; perfil próprio edita só nome/e-mail; encontro duplicado responde com erro de formulário sem 500.
- Dados exclusivos dos verificadores foram removidos por IDs, preservando apresentação e espaços humanos. Capturas consultaram formulários sem submeter alterações.
- 65 outros containers permanecem iguais na comparação de IDs, imagens, início, reinícios, saúde e portas. O container do PostgreSQL de produção também permaneceu igual. Apenas o app deste projeto foi reimplantado. Não houve mudanças em Nginx, certificado, firewall ou infraestrutura global, nem instalações globais.
- Banco temporário foi removido pelo nome exato após verificação de tmpfs/rede/portas; nenhum volume de produção foi removido.

Limitações declaradas: a oferta exclusiva A05-I fecha em 16/10/2026 às 18h; revisar o roteiro se as sessões ocorrerem depois. SMTP continua de console; atividades mobile/teclado não equivalem a auditoria completa de acessibilidade. Avaliações humanas, gravação do vídeo e promoção definitiva para main permanecem futuras.
