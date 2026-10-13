# Pacote das cinco avaliações humanas

Estado: **aguardando avaliação humana**. As pessoas ainda serão escolhidas; A01–A05 são identificadores de acesso, não nomes de avaliadores. Não há respostas, notas, assinaturas ou resultados preenchidos.

Aplicação: https://projeto-integrador.tesseratointegra.com.br. Código publicado: `a351c5a`; dados preparados com referência **13/10/2026**, fuso America/Sao_Paulo. Todos os nomes e registros de apresentação são fictícios; e-mails novos usam example.com. Nenhuma mensagem foi enviada. O telefone obrigatório dos responsáveis usa `00000000000`, com DDD 00 deliberadamente não discável. CPF, CNPJ e telefones opcionais permanecem vazios.

| Identificação | Perfil | Conta de acesso | Turma de trabalho |
|---|---|---|---|
| A01 | Administrador funcional | a01@example.com | PY-2026-A01 |
| A02 | Administrador funcional | a02@example.com | PY-2026-A02 |
| A03 | Instrutor | a03@example.com | PY-2026-A03 |
| A04 | Instrutor | a04@example.com | PY-2026-A04 |
| A05 | Participante | a05@example.com | PY-2026-A05, A05-F e A05-I |

As cinco contas não têm `is_staff`, superusuário, grupos ou permissões extras de Django admin. Cada senha é aleatória e distinta. Senhas ficam somente em `/root/codigo-do-futuro-presentation/20261013/credentials.json`, modo 600, fora do Git, com diretório 700. O responsável consulta esse arquivo localmente e entrega **apenas** a credencial da pessoa em canal privado. Não cole seu conteúdo em terminal gravado, issue, chat, Git ou relatório público. A senha do administrador operacional foi preservada.

Os administradores têm alcance funcional global, conforme o produto; sua separação é por dados e roteiro, não por um novo sistema de tenants. A01/A02 só alteram o próprio participante, turma, avaliação e certificado. Instrutores têm autorização aplicada no servidor às suas turmas; A05 acessa seus próprios registros. Acompanhamento do mediador evita operações administrativas fora do roteiro. As sessões podem ocorrer sequencialmente; nunca use os acessos de captura como contas de avaliação.

- [Instruções do responsável](instrucoes-responsavel.md)
- [Roteiros A01–A05](roteiros/README.md)
- [Formulário individual](formulario-de-avaliacao.md)
- [Consolidação](consolidacao.md)
- [Problemas e decisões](registro-de-melhorias.md)
- [Checklist](checklist-execucao.md)
- [Pacote HTML imprimível](pacote-imprimivel.html) e [PDF](pacote-imprimivel.pdf)
- [Resultados individuais ainda em branco](resultados/README.md)
- [Relatório técnico da preparação](../06-testes/preparacao-20261013/relatorio.md)

Tempo sugerido: 25–35 minutos por pessoa. Atividades em celular e teclado são observações de uso, não uma auditoria completa de acessibilidade. As capturas e verificações automáticas não substituem as cinco avaliações.

Exigência da disciplina: cinco **colegas de curso ou profissionais da área reais**, não cinco logins. [Modelo de PDF consolidado](modelo-pdf-consolidado.md) / [PDF em branco](modelo-consolidado.pdf), ainda aguardando opiniões. PY-2026-A05-I encerra 16/10/2026 18h São Paulo; revisar a tarefa se posterior, sem renovação nesta auditoria.
