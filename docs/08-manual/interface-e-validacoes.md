# Interface, navegação, validações e mensagens

## Interface atual e revisão

A interface executável HTML/templates/CSS representa o estado atual da candidata, documentado por [manual](README.md) e [38 imagens](plano-de-capturas.md) com hash/rota/perfil/viewport. Não há protótipo original identificável do Integrador I; não se inventa comparação antes/depois com ele. A revisão atual confronta templates/URLs/forms/services/testes e corrige documentação de fluxos que divergiam: perfil próprio, guardas do admin, duplicidade e roteiro A05.

## Mapa de navegação real

| Papel | Cabeçalho e fluxos |
|---|---|
| Público | Entrar → recuperação → confirmação de redefinição; início protegido redireciona |
| Todos autenticados | Logotipo/Início; Meu perfil (/conta/perfil/); Certificados; Sair via POST CSRF |
| ADMIN funcional | Pessoas → participantes/responsáveis/instrutores/instituições; Turmas → oficinas/detalhe/cronograma/instrutores; Inscrições → fila/decisão; acompanhamento → projetos/notas/conclusão/emissão; Painel → filtros/três CSVs |
| INSTRUCTOR | Minhas turmas → detalhe/cronograma/acompanhamento → chamada/revisão/nota; Inscrições/Certificados/Painel somente vinculados; sem Pessoas/CSV/conclusão/emissão |
| PARTICIPANT | Turmas disponíveis → solicitar; Minhas inscrições; Minha jornada → projeto/frequência/devolutiva/resultado; Meus certificados → PDF; não tem acesso ao detalhe administrativo de turma |

Turmas disponíveis é lista global de ofertas elegíveis/abertas; **não possui busca q**. Links diretos ajudam mediação, mas não substituem controle do servidor. /admin/ exige staff/permissões distintas do papel ADMIN. Formulários GET de capturas não foram submetidos; telas com notas acadêmicas fictícias não são avaliações humanas.

## Validações e mensagens

| Gatilho | Fonte e comportamento atual | Evidência |
|---|---|---|
| Login inválido/inativo | Auth Django; erro sem distinguir conta inexistente/senha/inatividade | tests/accounts/test_authentication.py e HTTP |
| Perfil salvo | OwnProfileView: “Seu perfil foi atualizado.”; whitelist e alvo da sessão | tests/accounts/test_profile.py, figura 03 |
| E-mail duplicado | Form/UNIQUE/race: “Este e-mail já está em uso.”, HTTP 200 e sem gravação parcial | Mesmo teste; reteste R-18–21 |
| Menor sem responsável | services: “Participantes menores de 18 anos precisam de responsável ativo.” | people/enrollments test_services |
| Fora de prazo/duplicidade de inscrição | create_enrollment rejeita com ValidationError; não cria novo registro | enrollments test_services/views |
| Sem vaga ou promoção fora de ordem | Revalida em transação; pede justificativa para exceção e preserva estado | cenário de última vaga e fila |
| Início duplicado de encontro | MeetingForm/MeetingSaveMixin; mensagem no campo, HTTP 200; UNIQUE permanece | regressões DEF-001 |
| Datas inválidas/nota fora 0–10 | Model.clean/forms/validators, erros de campo; CHECK nota complementar | workshops forms/models, learning models/forms |
| Turma não pronta/conclusão forjada | Serviços/admin exigem fluxo canônico; erro antes de gravação/inlines | DEF-003, learning completion tests |
| Chamada salva/projeto atualizado | “Chamada registrada e percentuais atualizados.” / “Projeto atualizado com sucesso.” | learning/views.py e HTTP |
| Papel/vínculo sem acesso | Login redireciona anônimo; papel negado 403; consulta fora de escopo pode ser 404 | testes negativos de views/HTTP |
| Certificado sem aprovação/revogado | Bloqueia emissão/download; motivo conserva histórico, não exclusão | tests/learning e PDF real |

base.html usa mensagens aria-live=polite, skip-link e labels; app.css define foco e layout flexível. Form.errors/non_field_errors orientam correção; Voltar/Cancelar abandonam entrada sem salvar. Isso documenta os mecanismos, não comprova automaticamente todas as metas de clareza/teclado/contraste.

## Correspondência do manual e capturas

Os 122 arquivos publicados conferem com a351c5a e src de develop. Manifest identifica 36 capturas de app (35 telas + scroll interno adicional), visualizador de CSV real e página do PDF real. Manual/legendas mostram: Robótica 2 confirmadas/0 vagas/1 espera/1 pendente; Web Carla 100%/Diego 50% e nota não publicada; Python Ana aprovada/Bruno não concluinte/8h; mobile 390×844. Não houve recaptura ou edição do banco nesta revisão; integridade dos 38 hashes foi reconferida.

## Limites de avaliação

Viewport e inspeção visual não são aparelhos reais nem avaliações de colegas. Scroll interno de tabela móvel está explícito; não se promete ausência universal de rolagem. Contraste AA, navegadores exigidos, teclado completo e aceitação de uso continuam sem aprovação suficiente. Ver [RNF](../02-requisitos/rastreabilidade-implementada.md#requisitos-não-funcionais-e-lacunas-de-mensuração).
