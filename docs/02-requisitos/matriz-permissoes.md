# Matriz de permissões

Legenda: **G** gerenciar; **R** registrar; **V** visualizar; **P** próprio/vinculado; **—** sem acesso.

| Recurso ou ação | Administrador | Instrutor | Participante |
|---|---:|---:|---:|
| Usuários e permissões | G | P | P |
| Participantes | G | V nas próprias turmas | P |
| Responsáveis legais | G | V mínima nas próprias turmas | P |
| Instrutores | G | P | V dos instrutores da turma |
| Instituições parceiras | G | V | V |
| Oficinas | G | V | V publicadas |
| Turmas | G | V vinculadas | V disponíveis ou inscritas |
| Encontros | G | R/V nas turmas vinculadas | V da turma inscrita |
| Inscrição | G | V nas turmas vinculadas | R/V/P |
| Lista de espera | G | V nas turmas vinculadas | V da própria posição, sem nomes de terceiros |
| Frequência | G | R/V nas turmas vinculadas | V própria |
| Projeto | G | R/V nas turmas vinculadas | R/V próprio |
| Avaliação | G | R/V nas turmas vinculadas | V própria após publicação |
| Certificado | G | V nas turmas vinculadas | V próprio |
| Painel | Visão global | Turmas vinculadas | Resumo próprio |
| Relatórios e exportação | G | V sem dados excessivos nas turmas vinculadas | — |

## Restrições complementares

1. Ocultar um botão na interface não substitui a autorização no servidor.
2. Um instrutor não recebe acesso a uma turma apenas por conhecer seu identificador.
3. O participante não visualiza e-mails, telefones, notas ou frequência de terceiros.
4. Dados do responsável são exibidos ao instrutor somente quando necessários à operação da turma.
5. Alterações de perfil de acesso são exclusivas do administrador.
6. Um administrador não pode desativar o único administrador ativo do sistema.
