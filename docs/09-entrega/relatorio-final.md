# Relatório de entrega — estado verificável em 19/10/2026

## Conclusão atual

Código do Futuro, Projeto Integrador Transdisciplinar em Engenharia de Software II. Identificação completa/RGM do estudante constam apenas da cópia privada destinada ao tutor. Aplicação https://projeto-integrador.tesseratointegra.com.br; código já publicado no GitHub em develop. PR #13 integrada em 58db4fc; código da aplicação a351c5a conferido por 122 hashes. Main preservada em 5730e37.

**O pacote não está integralmente conforme.** Há documentação e evidências técnicas, mas não cinco opiniões humanas disponíveis, vídeo publicado ou correção pública de DEF-004/005. Modelo oficial AVA recebido e preenchido parcialmente fora do Git; planejamento/protótipo I continuam ausentes, sem reconstrução apresentada como original.

## Solução e materiais

Aplicação web de oficinas para jovens de 14–21 anos, com administrador funcional, instrutor e participante. Python/Django, PostgreSQL, templates HTML/CSS, codificação tradicional; hospedagem na VPS existente com Docker/Gunicorn/Nginx/HTTPS e porta de app em loopback. Não se infere fornecedor comercial da VPS pelo domínio. Recuperação de senha usa console; SMTP externo não comprovado.

Escopo, 40 RF/RNF, camadas MTV/MVC, 16 models próprios e sete migrations, conceitual/lógico/normalização, banco físico e dicionário estão ligados no [índice](README.md). Manual com 38 imagens históricas identificadas permanece evidência da candidata; novas capturas técnicas têm data/método e saudação pessoal ocultada. [Roteiro operacional do vídeo](../08-manual/roteiro-video-final.md) tem oito blocos totalizando 300s, narração em primeira pessoa e alternativas; arquivo de vídeo não foi criado.

## Evidências distintas

- Automatizados históricos: 235 aprovados, zero skip, cobertura 89,84%, PostgreSQL isolado e CI develop 58db4fc. Não foram reexecutados no banco publicado.
- HTTP histórico: reteste com 25 cenários, 278 verificações/465 requisições; preparação com 57 verificações/81 requisições. Relatórios originais preservados.
- Simulações atuais do agente: 39 tarefas distintas, 37 aprovadas e duas reprovadas pelo mesmo DEF-004. Cinco reexecuções resolveram três falhas do executor e reproduziram o defeito. 150 respostas HTTP não são 150 cenários. Chromium, TLS, sessões independentes e CSRF; renderização desktop/viewport móvel, sem usabilidade/AA aprovadas.
- Correção candidata: commit local d1a5523 em branch própria; 41 testes direcionados isolados e dez widgets nativos confirmados após correção, sem implantação/CI remota nova.
- Avaliação humana: um relato HUM-001/A01 recebido por print; data informada 13/10/2026, nome e computador confirmados pelo estudante e guardados privadamente. Quatro relatos faltam. Navegador, tela/método mobile, condição de colega/profissional, não testados e ciência/autorização a confirmar. Não há notas inventadas.

Fontes: [simulações completas](../07-avaliacoes/relatorio-simulacoes.md), [consolidação humana separada](../07-avaliacoes/consolidacao.md), [laudo](laudo-qualidade.md) e [histórico](../06-testes/consolidacao-verificacao.md).

## Defeitos, decisões e preservação

DEF-001/002/003 foram encontrados tecnicamente e corrigidos/retestados antes desta tarefa; não atribuídos aos colegas. DEF-004 foi descoberto agora em campos HTML5 com datas localizadas: correção local pronta, mas segue reproduzível no publicado. Oferta histórica A05-I encerrada é comportamento esperado. Alternativa SIM exclusiva foi criada e recebeu PENDING, sem alterar a histórica; para nova tarefa humana, consultar situação ou preparar outra oferta própria.

Backup verificado antes de alterações. 57 novos registros fictícios gerenciados, nenhum registro preexistente de negócio alterado/excluído; autenticação atualiza last_login das contas usadas. Nenhuma conta nova, senha redefinida ou privilégio extra. Main, infraestrutura, Nginx/certificados e outros serviços preservados, sem deploy.

## Pendências e sequência

Seguir o [checklist](checklist-final.md): revisar cópia oficial AVA já preenchida e obter documentos I; incorporar somente relatos reais recebidos; tratar implantação/reteste de DEF-004/005 em operação autorizada separada; realizar cinco avaliações elegíveis; consolidar e decidir; gerar PDF de opiniões; atualizar versão/materiais; estudante gravar/exportar 300s, publicar e conferir acesso; preencher link no documento oficial e submeter no AVA com comprovante. Os DOCX/PDF de revisão não substituem requisitos que ainda faltam.


Conferência móvel posterior: 24 leituras HTTPS, 22 sem transbordamento e duas com DEF-005 na lista de participantes em 320/390px. Candidato CSS 00ee7f9 (sobre d1a5523) aprovado isoladamente em quatro larguras com teclado; não implantado. Não equivale ao caso humano sem confirmação da tela. Contagem separada das 39 tarefas e da suíte histórica.

Durante a revisão do modelo chegou nova inscrição em espera de A05 na Robótica, com um histórico, fora das operações executadas pelo agente nesta revisão. Ambos preservados e distinguidos dos 57 registros SIM criados anteriormente. Fila atual: 2 confirmadas, 2 em espera e 1 pendente; roteiro/captura atualizados sem inferir autoria de pessoa real.
