# Validação funcional publicada — VALIDATION-20261013-120621

**Conclusão: não liberar a aplicação como totalmente validada nem iniciar as cinco avaliações como aceite do MVP enquanto os defeitos altos estiverem abertos.** O fluxo principal foi exercitado por HTTP real, mas RF-006 não possui ponto de entrada e a interface Django admin contorna a guarda de conclusão acadêmica. Também existe HTTP 500 no cadastro de encontro com início duplicado.

Execução: 2026-10-13T12:14:44.384849-03:00 a 2026-10-13T12:37:09.942074-03:00; timezone America/Sao_Paulo (UTC−03:00). Origem: a própria VPS 31.97.167.150. Todas as chamadas usaram o domínio público e passaram por Nginx/Django com verificação normal de TLS. Não representam uma medição independente a partir de outra rede.

Domínio: https://projeto-integrador.tesseratointegra.com.br. Diretório: /home/ubuntu/projetos/projeto-integrador-ii-codigo-do-futuro. Branch: develop; commit: 00665be5889ae639e9c1facec8be6c853f5895fa. Imagem da aplicação: sha256:dc5d59ebc59598bc5f46fb4d976e12fdc4b28f1db0a33a2d87c51448ef03604f. Containers: codigo-do-futuro-app-1 e codigo-do-futuro-database-1. Aplicação em 127.0.0.1:8031; banco sem porta publicada.

## Resultado quantitativo

340 casos registrados, incluindo preparação HTTP, repetições de autenticação e retestes. 557 requisições HTTP instrumentadas, timeout de 20 segundos e limite de 650. Execução sequencial, exceto duas confirmações simultâneas na turma exclusiva de última vaga. A matriz JSON contém verificações, efeitos persistidos e hashes do estado; a CSV facilita revisão.

- APROVADO: 331
- REPROVADO: 4
- BLOQUEADO: 0
- NÃO EXECUTADO: 5

| Grupo | APROVADO | REPROVADO | BLOQUEADO | NÃO EXECUTADO |
|---|---:|---:|---:|---:|
| Autenticação | 38 | 0 | 0 | 0 |
| Autorização | 63 | 0 | 0 | 0 |
| Avaliações | 12 | 0 | 0 | 0 |
| CSV | 10 | 0 | 0 | 0 |
| Certificados | 15 | 0 | 0 | 0 |
| Conclusão | 6 | 1 | 0 | 0 |
| Disponibilidade | 5 | 0 | 0 | 0 |
| Encontros | 12 | 2 | 0 | 0 |
| Frequência | 9 | 0 | 0 | 0 |
| Inscrições | 29 | 0 | 0 | 0 |
| Limitações | 0 | 0 | 0 | 5 |
| Oficinas | 6 | 0 | 0 | 0 |
| Painéis | 12 | 0 | 0 | 0 |
| Perfil próprio | 0 | 1 | 0 | 0 |
| Pessoas | 26 | 0 | 0 | 0 |
| Preparação HTTP | 27 | 0 | 0 | 0 |
| Projetos | 8 | 0 | 0 | 0 |
| Recuperação | 10 | 0 | 0 | 0 |
| Turmas | 22 | 0 | 0 | 0 |
| Usuários | 3 | 0 | 0 | 0 |
| Vagas | 18 | 0 | 0 | 0 |

## Funcionalidades e perfis realmente testados

Administrador isolado, dois instrutores, três participantes adultos e um menor. Sessões independentes por conta; sessão anônima para os bloqueios. Foram testados disponibilidade/TLS/redirecionamento, estáticos, login válido/inválido/inativo, logout, CSRF, permissões por perfil e vínculo, cadastro/pesquisa/edição de pessoas e instituições, responsável do menor, oficinas e estados, turmas/instrutores/cronograma, inscrições e histórico, ocupação/fila/promoção/cancelamento/concorrência, frequência, projetos, avaliações/publicação, conclusão, certificados/PDF/revogação, painel e os três CSVs filtrados.

A turma acadêmica produziu 75%, 50%, 100% e 100% de frequência. O participante com 75%, nota 6,0 e projeto entregue foi aprovado; os outros três não concluíram respectivamente por frequência, nota e ausência de projeto. O certificado teve quatro horas, excluindo encontro cancelado. O painel filtrado indicou uma turma, quatro inscrições, 100% de ocupação, 81,25% de frequência média, três projetos e 25% de aprovação. Os CSVs continham quatro linhas do mesmo universo e não continham CPF, telefone ou e-mail.

Recuperação de senha: formulário, mensagem no console, link com token, redefinição numa conta exclusiva, rejeição da senha anterior, novo login e rejeição de reutilização do token foram exercitados. Tokens permaneceram somente em memória; os caminhos nas evidências usam placeholders. **Isso não comprova entrega SMTP.**

## Preparação e correções do executor

O primeiro administrador isolado foi provisionado por um bootstrap mínimo Django/ORM porque não existe auto provisionamento público sem autenticação administrativa. Isso preservou as contas existentes e não conta como validação HTTP de cadastro. As seis contas seguintes foram criadas pelo endpoint real do Django admin; todos os perfis e registros de negócio foram criados por formulários HTTP. Nenhuma conta [DEMO] foi autenticada, editada ou teve senha alterada. Senhas temporárias ficam exclusivamente em /root/codigo-do-futuro-validation/VALIDATION-20261013-120621/credentials.json, modo 600, diretório 700, fora do Git.

O executor precisou ser retomado após gerar um código de turma maior que 30 caracteres; o servidor corretamente rejeitou a entrada. Os códigos válidos preservam o identificador completo com sufixo curto. Também foram corrigidos seletores de mensagens de formulário, expectativas de certificado revogado e o contexto do CPF após a retomada. As expectativas anteriores estão preservadas em matriz-antes-revisao-executor.json; correcoes-executor.json liga cada revisão a retestes HTTP reais. Para CSV, a resposta inicial e o reteste possuem exatamente o mesmo SHA-256. Nenhuma correção foi aplicada ao código da aplicação. Não foram encontrados AGENTS.md aplicáveis no projeto ou em seus diretórios ancestrais.

## Defeitos e pendências

Ver [defeitos.md](defeitos.md) para severidade, passos, resultado esperado/observado e correção proposta. Foram encontrados 3 defeitos, sem correções nesta tarefa. RF-006 é Must e precisa de implementação e reteste. A guarda acadêmica deve também valer no Django admin. O erro 500 por duplicidade deve ser convertido em erro de formulário.

Os cinco casos LIMIT na matriz explicam testes não executados: SMTP real, cinco avaliações/usabilidade, responsividade, acessibilidade e desativação do único administrador ativo. O último exigiria alterar contas existentes; deve ser testado em banco descartável. Não foi executado teste de carga ou restauração de banco em uso.

## Preservação e dados mantidos

Comparação de containers: 0 diferenças em IDs, início, saúde, reinícios, portas, imagem e limites. Comparação dos dados preexistentes: modelos alterados = []. As duas imagens/containers do projeto continuam saudáveis. Nenhum deploy, nova migração, alteração de código da aplicação, push, merge, promoção de branch ou alteração de infraestrutura foi realizado. Os únicos arquivos locais novos estão nesta pasta de evidências.

hospitalar-staging-docs e bancodetalentos_frontend já estavam unhealthy e permaneceram assim; hospitalar-staging-migrate também já estava parado/unhealthy. Nenhum serviço de outro projeto foi reiniciado ou corrigido.

Os dados fictícios desta execução foram mantidos, incluindo o certificado revogado e a turma usada para demonstrar a guarda ausente. Todos são identificáveis por VALIDATION-20261013-120621. O plano abaixo não foi executado.

## Plano de remoção restrita

1. Criar backup e revisar [ids-execucao.json](ids-execucao.json); confirmar cada ID e seus vínculos antes de qualquer alteração. Usar somente esses IDs, nunca filtros globais ou exclusão por um prefixo genérico.
2. Preferir desativar as sete contas e perfis desta execução e cancelar/arquivar as turmas/oficina exclusivas, preservando histórico. O certificado revogado já mantém seu registro histórico.
3. Se houver autorização posterior para remoção física, avaliar transação e dependências: logs do admin desta execução, frequências, avaliações, projetos, histórico de inscrições, certificado, inscrições, encontros, vínculos de instrutores e responsáveis, turmas, oficina, perfis, responsáveis/instituição e usuários. Respeitar PROTECT e a proibição de delete de certificado; não contornar essas guardas automaticamente.
4. Invalidar somente sessões cujos usuários decodificados correspondam aos IDs desta execução. Não listar ou gravar chaves de sessão no relatório. Excluir depois o arquivo privado de credenciais, conforme retenção acordada.
5. Conferir contagens/IDs e hashes dos dados existentes após a operação e repetir o smoke test. Nenhuma etapa destrutiva desse plano foi executada nesta tarefa.

## Reprodução e artefatos

- validar.py: executor principal; nova execução usa novo identificador e novo diretório privado.
- complementar.py: executado após o principal, com o mesmo identificador e diretório privado.
- reteste_formulario.py: reteste pontual que preservou somente a mensagem de erro sanitizada.
- finalizar_relatorio.py: consolidação desta execução, com consultas de leitura; revisões históricas referenciam seus IDs originais.
- matriz.json / matriz.csv: casos e classificação final.
- requisicoes.json: trilha sanitizada de requisições, sem corpos completos, cookies ou tokens.
- estado-final-execucao.json / ids-execucao.json: registros exclusivos e seus efeitos.
- endpoints-descobertos.json: inventário real de URLs da aplicação.
- pdf-evidencia.json e csv-*-evidencia.json: fingerprints e verificações dos documentos.
- diagnostico-sanitizado.json: somente tipos de exceção e nome da constraint.
- containers-*.json / dados-existentes-*.json: preservação do ambiente e dos cenários existentes.

```bash
cd /home/ubuntu/projetos/projeto-integrador-ii-codigo-do-futuro
PYTHONDONTWRITEBYTECODE=1 python3 docs/06-testes/validacao-publicada/VALIDATION-20261013-120621/validar.py --private-dir /root/codigo-do-futuro-validation/NOVA-EXECUCAO
# Use o identificador impresso/gerado na pasta e o mesmo diretório privado:
PYTHONDONTWRITEBYTECODE=1 python3 docs/06-testes/validacao-publicada/VALIDATION-20261013-120621/complementar.py --private-dir /root/codigo-do-futuro-validation/NOVA-EXECUCAO --run-id VALIDATION-AAAAMMDD-HHMMSS
```

A validação técnica não substitui as cinco avaliações reais e não comprova, sozinha, usabilidade, responsividade ou acessibilidade.
