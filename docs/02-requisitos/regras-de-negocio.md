# Regras de negócio

## Usuários e pessoas

| ID | Regra |
|---|---|
| RN-001 | Cada usuário deve possuir um e-mail único, normalizado sem diferença entre maiúsculas e minúsculas. |
| RN-002 | Somente usuários ativos podem se autenticar. |
| RN-003 | Cada usuário autenticado possui exatamente um perfil de acesso: administrador, instrutor ou participante. |
| RN-004 | O participante deve ter entre 14 e 21 anos, inclusive, na data de início da turma. |
| RN-005 | Participante com menos de 18 anos na data da inscrição deve possuir pelo menos um responsável legal ativo, com nome, vínculo e telefone. |
| RN-006 | CPF, quando coletado, deve ser único por pessoa, validado e acessível apenas a administradores. |
| RN-007 | Pessoas e usuários com histórico acadêmico não podem ser excluídos fisicamente pela interface; devem ser desativados. |

## Oficinas, turmas e encontros

| ID | Regra |
|---|---|
| RN-008 | Uma oficina segue o fluxo `rascunho → publicada → arquivada`; oficina arquivada não recebe novas turmas. |
| RN-009 | Uma turma deve estar ligada a uma oficina publicada e possuir título, capacidade, local, datas de inscrição e período de realização. |
| RN-010 | A capacidade da turma deve ser um inteiro positivo. |
| RN-011 | O início das inscrições não pode ser posterior ao encerramento das inscrições. |
| RN-012 | A data inicial da turma não pode ser posterior à data final e não pode anteceder o encerramento das inscrições. |
| RN-013 | Uma turma segue apenas as transições `planejada → inscrições abertas → em andamento → concluída`; pode ser cancelada antes de concluída. |
| RN-014 | Uma turma só pode abrir inscrições se tiver capacidade, período válido e pelo menos um instrutor ativo. |
| RN-015 | Uma turma só pode iniciar quando tiver pelo menos um encontro planejado e um instrutor ativo. |
| RN-016 | Um encontro deve ocorrer dentro do período da turma; encontros da mesma turma não podem possuir o mesmo início. |
| RN-017 | Cancelar uma turma cancela seus encontros futuros e impede novas inscrições, sem apagar o histórico. |

## Inscrições e vagas

| ID | Regra |
|---|---|
| RN-018 | Um participante pode possuir apenas uma inscrição por turma. |
| RN-019 | A inscrição pelo participante só é aceita durante o período de inscrições e quando a turma estiver com inscrições abertas. |
| RN-020 | O sistema deve validar idade, responsável legal e situação ativa do participante antes de registrar a inscrição. |
| RN-021 | A vaga é ocupada somente por inscrição confirmada; inscrições pendentes e em lista de espera não ocupam vaga. |
| RN-022 | A quantidade de inscrições confirmadas nunca pode exceder a capacidade da turma, inclusive em solicitações simultâneas. |
| RN-023 | Quando não houver vaga, a inscrição elegível deve ir para a lista de espera se esse recurso estiver habilitado; caso contrário, permanece pendente para decisão administrativa. |
| RN-024 | A ordem da lista de espera é definida pela data e hora de entrada, da mais antiga para a mais recente. |
| RN-025 | A promoção da lista de espera deve respeitar a ordem; o administrador deve registrar justificativa se promover fora dela. |
| RN-026 | Uma inscrição pode ser cancelada pelo participante antes do início da turma; após o início, somente o administrador pode alterar sua situação, com justificativa. |
| RN-027 | O cancelamento de uma inscrição confirmada antes do início libera uma vaga. |
| RN-028 | Inscrições não podem ser excluídas fisicamente após confirmação; alterações de situação preservam o histórico. |

## Frequência, projetos, avaliação e conclusão

| ID | Regra |
|---|---|
| RN-029 | Somente administrador ou instrutor atribuído à turma pode registrar frequência, projeto revisado ou avaliação. |
| RN-030 | Deve existir no máximo um registro de frequência por inscrição e encontro. |
| RN-031 | A frequência admite `presente`, `ausente` ou `falta justificada`; falta justificada permanece registrada e não conta como presença. |
| RN-032 | O percentual de frequência é `presenças ÷ encontros realizados × 100`; encontros cancelados ou futuros não entram no cálculo. |
| RN-033 | A correção de frequência deve preservar quem realizou a última alteração e quando ela ocorreu. |
| RN-034 | Cada participante pode possuir no máximo um projeto individual por inscrição no MVP. |
| RN-035 | A nota final deve variar de 0,0 a 10,0, com uma casa decimal. |
| RN-036 | Para concluir com aprovação, o participante deve ter frequência mínima de 75%, nota final mínima de 6,0 e projeto marcado como entregue. |
| RN-037 | Caso não cumpra os critérios, a inscrição deve ser concluída como `não concluída`, mantendo os resultados registrados. |
| RN-038 | A situação final só pode ser calculada após o encerramento de todos os encontros não cancelados e o registro da avaliação. |

## Certificados e relatórios

| ID | Regra |
|---|---|
| RN-039 | Certificados são exclusivos de inscrições concluídas com aprovação. |
| RN-040 | Cada inscrição aprovada possui no máximo um certificado ativo, identificado por código único. |
| RN-041 | A carga horária do certificado corresponde à soma da duração dos encontros realizados da turma. |
| RN-042 | O certificado deve mostrar nome do participante, oficina, turma, período, carga horária e código de identificação. |
| RN-043 | O participante só pode consultar os próprios dados, resultados e certificados. |
| RN-044 | O instrutor só pode consultar dados acadêmicos das turmas às quais está atribuído. |
| RN-045 | Indicadores devem considerar os filtros aplicados e explicitar o período e universo dos dados. |

## Privacidade e conservação

| ID | Regra |
|---|---|
| RN-046 | O sistema não deve exibir CPF integral em listagens ou relatórios comuns. |
| RN-047 | Dados reais de participantes não devem ser usados em documentação pública, screenshots ou vídeo sem autorização; devem ser fictícios ou anonimizados. |
| RN-048 | Dados pessoais só podem ser exportados por administrador e apenas quando necessários ao objetivo acadêmico ou operacional declarado. |

## Decisões configuráveis

Os valores de idade, frequência mínima e nota mínima são regras oficiais do MVP. A arquitetura deve concentrá-los em uma camada de domínio/configuração, evitando números espalhados pelo código. Uma alteração futura exige atualização desta especificação e dos testes relacionados.
