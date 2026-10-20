# Relato humano recebido e conferência técnica posterior

Recebido um relato humano, HUM-001/A01, em print fornecido nesta conversa. Data informada: 13/10/2026. Nome e computador confirmados pelo estudante; identificação completa/transcrição ficam fora do Git. Condição de colega/profissional, navegador, tela e método da observação mobile ainda a confirmar. Quatro relatos faltam. Não há notas de satisfação, tempos ou execução completa do roteiro comprovados.

O relato confirma seis itens (perfil/cabeçalho, inscrição, cancelamento, validação do período do encontro, filtro do painel e consulta/download PDF) e informa “Responsividade mobile quebra”. Não especifica correção ou funcionalidades não testadas. As [opiniões humanas](../consolidacao.md) estão separadas das medições abaixo.

## DEF-005 — transbordamento reproduzido tecnicamente

Agente Codex, 19/10/2026, Chromium/Playwright por HTTPS com TLS validado, login/CSRF nativos e somente leitura nas páginas. Backup do projeto validado antes da autenticação; nenhuma operação de negócio foi salva. [24 verificações](mobile.json): oito telas em 320, 390 e 768px; 22 APROVADO no critério de largura e duas REPROVADO. Isso não aprova usabilidade nem representa teste em aparelho físico. Não somar essas verificações às 39 tarefas anteriores.

Na lista `/pessoas/participantes/`, o documento tinha 435px em viewports 320/390. O rótulo acessível “Ações” era absoluto e referido ao body; a própria tabela já tinha rolagem interna prevista. [320px](mobile-participantes-320.png) e [390px](mobile-participantes-390.png). Gravidade média. A identidade com o caso humano depende da confirmação da tela/método/navegador.

Correção mínima: `position: relative` em `.table-shell`, commit local `00ee7f9`, branch `fix/layout-mobile-tabelas-20261019`, sobre o candidato de datas d1a5523. Nenhum conteúdo foi ocultado ou rótulo acessível removido. [Quatro verificações isoladas](mobile-isolado.json) em 320/390/768/1440px: largura corrigida, tabela segue rolável, última ação acessível por teclado e nome acessível preservado. [Imagem isolada do candidato](DEF005-candidato-mobile-isolado.png). Sem implantação; não é reteste público nem CI remota.

Duas primeiras tentativas do executor usaram endereços incorretos para Meu perfil e foram interrompidas por 404; o endereço real `/conta/perfil/` foi conferido no URLconf. Não são defeitos da aplicação nem fazem parte das 24 verificações concluídas. Uma sessão da primeira tentativa não pôde ser associada com segurança a um cookie retido; foi deixada para expiração normal, sem excluir sessões possivelmente alheias. A segunda e a sessão concluída foram encerradas por logout HTTPS/CSRF.

## Atualização concorrente da fila de apresentação

Durante a revisão surgiu uma inscrição em espera, com seu histórico, por A01 na Robótica, às 20:48:50 de 19/10/2026 (São Paulo). Nenhum POST de inscrição foi executado pelo agente nesta revisão. Os novos registros foram preservados, sem inferir quem usou a conta ou relacionar esse evento ao relato humano. Conferência posterior por HTTPS/ORM somente leitura confirmou 2 confirmadas, 2 em espera e 1 pendente. [Captura atual, nomes ocultos](robotica-fila-atual.png). A captura antiga permanece como evidência do estado anterior. Roteiro atualizado; reconferir antes de gravar.
